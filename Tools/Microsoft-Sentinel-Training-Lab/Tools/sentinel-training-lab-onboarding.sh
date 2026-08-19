#!/usr/bin/env bash
# Prepares the only external prerequisite required by the official
# Microsoft Sentinel Training Lab "Deploy to Azure" button:
#   1. Create/reuse a user-assigned managed identity.
#   2. Grant Microsoft Graph CustomDetection.ReadWrite.All.
#   3. Print the identity resource ID and Microsoft's deployment URL.

set -Eeuo pipefail

IDENTITY_NAME="SentinelDetectionRulesIdentity"
GRAPH_APP_ID="00000003-0000-0000-c000-000000000000"
APP_ROLE_ID="e0fd9c8d-a12e-4cc9-9827-20c8c3cd6fb8"
APP_ROLE_VALUE="CustomDetection.ReadWrite.All"
DEPLOY_URL="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FMicrosoft-Sentinel-Training-Lab%2FPackage%2FmainTemplate.json"

usage() {
  cat <<'EOF'
Prepare the Microsoft Sentinel Training Lab custom-detection identity.

Usage:
  bash sentinel-training-lab-onboarding.sh RESOURCE_GROUP

Arguments:
  RESOURCE_GROUP  Existing target resource group

The script creates or reuses SentinelDetectionRulesIdentity, grants the
Microsoft Graph application permission CustomDetection.ReadWrite.All, verifies
the assignment, and prints the value for detectionRulesIdentityResourceId plus
the official Microsoft "Deploy to Azure" URL.

Run this in Azure Cloud Shell (Bash) using an account with the required Azure
resource permissions and a supported Microsoft Entra administrator role.
EOF
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

if (( $# != 1 )); then
  usage >&2
  exit 2
fi

RESOURCE_GROUP="$1"

on_error() {
  local exit_code=$?
  echo >&2
  echo "[!] Preparation failed at line ${BASH_LINENO[0]} (exit ${exit_code})." >&2
  echo "    Nothing from the Microsoft lab template was deployed by this script." >&2
  exit "${exit_code}"
}
trap on_error ERR

if ! command -v az >/dev/null 2>&1; then
  echo "[!] Azure CLI ('az') was not found. Run this in Azure Cloud Shell (Bash)." >&2
  exit 1
fi

if ! az account show --output none 2>/dev/null; then
  echo "[!] No active Azure login. Run 'az login' or reopen Azure Cloud Shell." >&2
  exit 1
fi

SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
ACTIVE_TENANT_ID="$(az account show --query tenantId -o tsv)"
SIGNED_IN_USER="$(az account show --query user.name -o tsv)"

echo "[*] Azure context"
echo "    Subscription: ${SUBSCRIPTION_ID}"
echo "    Tenant:       ${ACTIVE_TENANT_ID}"
echo "    User:         ${SIGNED_IN_USER}"

if ! az group show --name "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "[!] Resource group '${RESOURCE_GROUP}' does not exist in the active subscription." >&2
  exit 1
fi

if az identity show \
  --resource-group "${RESOURCE_GROUP}" \
  --name "${IDENTITY_NAME}" \
  --output none 2>/dev/null; then
  echo "[*] Reusing UAMI '${IDENTITY_NAME}'."
else
  echo "[*] Creating UAMI '${IDENTITY_NAME}' in '${RESOURCE_GROUP}'..."
  az identity create \
    --resource-group "${RESOURCE_GROUP}" \
    --name "${IDENTITY_NAME}" \
    --only-show-errors \
    --output none
fi

IFS=$'\t' read -r MI_PRINCIPAL_ID MI_TENANT_ID MI_RESOURCE_ID < <(
  az identity show \
    --resource-group "${RESOURCE_GROUP}" \
    --name "${IDENTITY_NAME}" \
    --query '[principalId, tenantId, id]' \
    -o tsv
)

if [[ "${MI_TENANT_ID,,}" != "${ACTIVE_TENANT_ID,,}" ]]; then
  echo "[!] Tenant mismatch." >&2
  echo "    Active tenant:   ${ACTIVE_TENANT_ID}" >&2
  echo "    Identity tenant: ${MI_TENANT_ID}" >&2
  exit 1
fi

GRAPH_SP_ID="$(az ad sp show \
  --id "${GRAPH_APP_ID}" \
  --query id -o tsv)"

GRAPH_ROLE_VALUE="$(az ad sp show \
  --id "${GRAPH_APP_ID}" \
  --query "appRoles[?id=='${APP_ROLE_ID}'].value | [0]" \
  -o tsv)"

if [[ "${GRAPH_ROLE_VALUE}" != "${APP_ROLE_VALUE}" ]]; then
  echo "[!] Microsoft Graph app role verification failed." >&2
  echo "    Expected ${APP_ROLE_VALUE} (${APP_ROLE_ID})." >&2
  exit 1
fi

echo "[*] Waiting until Microsoft Graph can resolve the UAMI service principal..."
MI_VISIBLE=false
for attempt in {1..60}; do
  if az rest \
    --method GET \
    --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${MI_PRINCIPAL_ID}?\$select=id" \
    --output none 2>/dev/null; then
    MI_VISIBLE=true
    break
  fi

  echo "    Attempt ${attempt}/60: not visible yet; waiting 5 seconds..."
  sleep 5
done

if [[ "${MI_VISIBLE}" != true ]]; then
  echo "[!] The UAMI is still not visible in Microsoft Graph after five minutes." >&2
  echo "    principalId: ${MI_PRINCIPAL_ID}" >&2
  exit 1
fi

assignment_count() {
  az rest \
    --method GET \
    --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${MI_PRINCIPAL_ID}/appRoleAssignments" \
    --query "value[?resourceId=='${GRAPH_SP_ID}' && appRoleId=='${APP_ROLE_ID}'] | length(@)" \
    -o tsv
}

if [[ "$(assignment_count)" == "0" ]]; then
  echo "[*] Granting ${APP_ROLE_VALUE}..."

  REQUEST_BODY="$(printf \
    '{"principalId":"%s","resourceId":"%s","appRoleId":"%s"}' \
    "${MI_PRINCIPAL_ID}" "${GRAPH_SP_ID}" "${APP_ROLE_ID}")"

  if ! POST_OUTPUT="$(az rest \
    --method POST \
    --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${GRAPH_SP_ID}/appRoleAssignedTo" \
    --headers "Content-Type=application/json" \
    --body "${REQUEST_BODY}" \
    --output none 2>&1)"; then
    if [[ "${POST_OUTPUT}" != *"Permission being assigned already exists"* ]]; then
      echo "${POST_OUTPUT}" >&2
      exit 1
    fi
  fi
else
  echo "[*] ${APP_ROLE_VALUE} is already assigned."
fi

echo "[*] Verifying the Graph permission..."
PERMISSION_VERIFIED=false
for attempt in {1..12}; do
  if [[ "$(assignment_count)" != "0" ]]; then
    PERMISSION_VERIFIED=true
    break
  fi
  sleep 5
done

if [[ "${PERMISSION_VERIFIED}" != true ]]; then
  echo "[!] Graph permission assignment could not be verified." >&2
  exit 1
fi

echo
echo "[+] Preparation complete."
echo
echo "Paste this value into 'detectionRulesIdentityResourceId':"
echo "${MI_RESOURCE_ID}"
echo
echo "Official Microsoft 'Deploy to Azure' page:"
echo "${DEPLOY_URL}"
