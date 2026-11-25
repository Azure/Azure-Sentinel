#!/usr/bin/env bash
# Grants this playbook's system-assigned managed identity the Microsoft
# Defender for Endpoint (WindowsDefenderATP) application permissions it
# needs to run PolySwarm-Sandbox-DefenderFile:
#   - Machine.LiveResponse   (start the GetFile live response action)
#   - Machine.ReadWrite.All  (poll the machine action, get the download link)
#   - AdvancedQuery.Read.All (run the advanced hunting query)
#
# A note on Machine.ReadWrite.All vs Machine.Read.All: Microsoft's current API
# reference for get-machineaction-object and get-live-response-result both
# list Machine.ReadWrite.All as the required application permission, not
# Machine.Read.All. This script grants Machine.ReadWrite.All for that reason.
# See the playbook README, "A permission correction", for the doc citations.
#
# Modeled on Azure/Azure-Sentinel's own
# Tools/Microsoft-Sentinel-Training-Lab/Tools/sentinel-training-lab-onboarding.sh,
# which grants a Microsoft Graph app role to a managed identity the same way:
# resolve the role id from the resource service principal's own appRoles list
# rather than trust a hardcoded GUID, then POST an appRoleAssignment and poll
# until Microsoft Graph shows it.

set -Eeuo pipefail

WINDOWS_DEFENDER_ATP_APP_ID="fc780465-2017-40d4-a0c5-307022471b92"
REQUIRED_ROLES=("Machine.LiveResponse" "Machine.ReadWrite.All" "AdvancedQuery.Read.All")

usage() {
  cat <<'EOF'
Grant the WindowsDefenderATP application permissions PolySwarm-Sandbox-DefenderFile
needs to its playbook's managed identity.

Usage:
  bash grant-defender-permissions.sh RESOURCE_GROUP PLAYBOOK_NAME

Arguments:
  RESOURCE_GROUP   Resource group the playbook (Logic App) was deployed into
  PLAYBOOK_NAME    The Logic App resource name (the PlaybookName parameter
                    value used at deployment, e.g. PolySwarm-Sandbox-DefenderFile)

Grants, on the WindowsDefenderATP application:
  - Machine.LiveResponse
  - Machine.ReadWrite.All
  - AdvancedQuery.Read.All

Run this in Azure Cloud Shell (Bash), or locally with the Azure CLI signed in
as a Global Administrator or Privileged Role Administrator (application
permission grants require one of those Entra roles; Owner/Contributor on the
subscription is not enough).

This script does not touch the Key Vault role assignment (Key Vault Secrets
User) or the Data Collection Rule role assignment (Monitoring Metrics
Publisher, needed for this playbook to write PolySwarmSandbox_CL rows via the
Logs Ingestion API) -- both are Azure RBAC role assignments, not WindowsDefenderATP
application permissions, and are granted the same way, e.g.:
  az role assignment create --role "Key Vault Secrets User" \
    --assignee-object-id <principalId> --assignee-principal-type ServicePrincipal \
    --scope <key-vault-resource-id>
  az role assignment create --role "Monitoring Metrics Publisher" \
    --assignee-object-id <principalId> --assignee-principal-type ServicePrincipal \
    --scope <data-collection-rule-resource-id>
EOF
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
esac

if (( $# != 2 )); then
  usage >&2
  exit 2
fi

RESOURCE_GROUP="$1"
PLAYBOOK_NAME="$2"

on_error() {
  local exit_code=$?
  echo >&2
  echo "[!] Permission grant failed at line ${BASH_LINENO[0]} (exit ${exit_code})." >&2
  echo "    Re-run is safe: existing role assignments are detected and skipped." >&2
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

echo "[*] Looking up the playbook's managed identity..."
MI_PRINCIPAL_ID="$(az resource show \
  --resource-group "${RESOURCE_GROUP}" \
  --resource-type "Microsoft.Logic/workflows" \
  --name "${PLAYBOOK_NAME}" \
  --query "identity.principalId" -o tsv 2>/dev/null || true)"

if [[ -z "${MI_PRINCIPAL_ID}" || "${MI_PRINCIPAL_ID}" == "None" ]]; then
  echo "[!] Could not find a system-assigned managed identity on Logic App '${PLAYBOOK_NAME}' in '${RESOURCE_GROUP}'." >&2
  echo "    Confirm the playbook deployed successfully and identity.type is SystemAssigned." >&2
  exit 1
fi

echo "    principalId: ${MI_PRINCIPAL_ID}"

echo "[*] Resolving the WindowsDefenderATP service principal (appId ${WINDOWS_DEFENDER_ATP_APP_ID})..."
DEFENDER_SP_ID="$(az ad sp show --id "${WINDOWS_DEFENDER_ATP_APP_ID}" --query id -o tsv 2>/dev/null || true)"

if [[ -z "${DEFENDER_SP_ID}" ]]; then
  echo "[!] WindowsDefenderATP service principal not found by appId in this tenant." >&2
  echo "    It is created automatically the first time a Defender for Endpoint admin signs in to the" >&2
  echo "    security.microsoft.com portal, or the first time any app requests its permissions in the" >&2
  echo "    Entra admin center. Sign in to the Defender portal once, then re-run this script." >&2
  exit 1
fi

echo "    servicePrincipalId: ${DEFENDER_SP_ID}"

echo "[*] Waiting until Microsoft Graph can resolve the playbook's managed identity..."
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
  echo "[!] The managed identity is still not visible in Microsoft Graph after five minutes." >&2
  echo "    principalId: ${MI_PRINCIPAL_ID}" >&2
  exit 1
fi

assignment_count() {
  local role_id="$1"
  az rest \
    --method GET \
    --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${MI_PRINCIPAL_ID}/appRoleAssignments" \
    --query "value[?resourceId=='${DEFENDER_SP_ID}' && appRoleId=='${role_id}'] | length(@)" \
    -o tsv
}

for role_value in "${REQUIRED_ROLES[@]}"; do
  echo "[*] ${role_value}"

  role_id="$(az ad sp show \
    --id "${WINDOWS_DEFENDER_ATP_APP_ID}" \
    --query "appRoles[?value=='${role_value}' && contains(allowedMemberTypes, 'Application')].id | [0]" \
    -o tsv)"

  if [[ -z "${role_id}" || "${role_id}" == "None" ]]; then
    echo "[!] Could not find an application-type app role named '${role_value}' on WindowsDefenderATP in this tenant." >&2
    echo "    Microsoft may have renamed or retired it; check the Enterprise application's API permissions blade." >&2
    exit 1
  fi
  echo "    role id: ${role_id}"

  if [[ "$(assignment_count "${role_id}")" != "0" ]]; then
    echo "    already granted, skipping."
    continue
  fi

  REQUEST_BODY="$(printf \
    '{"principalId":"%s","resourceId":"%s","appRoleId":"%s"}' \
    "${MI_PRINCIPAL_ID}" "${DEFENDER_SP_ID}" "${role_id}")"

  if ! POST_OUTPUT="$(az rest \
    --method POST \
    --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${DEFENDER_SP_ID}/appRoleAssignedTo" \
    --headers "Content-Type=application/json" \
    --body "${REQUEST_BODY}" \
    --output none 2>&1)"; then
    if [[ "${POST_OUTPUT}" != *"Permission being assigned already exists"* ]]; then
      echo "${POST_OUTPUT}" >&2
      exit 1
    fi
  fi

  echo "    granted."
done

echo "[*] Verifying all three role assignments..."
ALL_VERIFIED=true
for role_value in "${REQUIRED_ROLES[@]}"; do
  role_id="$(az ad sp show \
    --id "${WINDOWS_DEFENDER_ATP_APP_ID}" \
    --query "appRoles[?value=='${role_value}'].id | [0]" \
    -o tsv)"
  VERIFIED=false
  for attempt in {1..12}; do
    if [[ "$(assignment_count "${role_id}")" != "0" ]]; then
      VERIFIED=true
      break
    fi
    sleep 5
  done
  if [[ "${VERIFIED}" != true ]]; then
    echo "[!] ${role_value} could not be verified." >&2
    ALL_VERIFIED=false
  fi
done

if [[ "${ALL_VERIFIED}" != true ]]; then
  exit 1
fi

echo
echo "[+] Permission grant complete."
echo
echo "Reminder: separately confirm, in the Microsoft Defender portal under Settings > Endpoints > Advanced"
echo "features, that 'Live response' and 'Live response for servers' are turned on -- this script cannot"
echo "check that setting."
echo
echo "Also separately grant 'Monitoring Metrics Publisher' on the PolySwarmSandbox_CL Data Collection Rule"
echo "to this same managed identity (principalId above) -- see --help for the az role assignment command."
