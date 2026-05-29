#!/bin/bash
#
# Add an Azure DevOps Audit Logs CCP connector instance for an additional org.
#
# The Azure DevOps Audit Logs (via Codeless Connector Platform) connector UI
# supports connecting one org at a time. To ingest audit logs from multiple
# Azure DevOps organizations into the same Sentinel workspace, run this script
# once per additional org. Each run creates a new RestApiPoller connector
# instance that shares the same DCR/DCE and writes to the ADOAuditLogs_CL table.
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - The first org must already be connected via the Sentinel connector UI
#   - The Entra App (registered for the first connector) must be authorized
#     in the target DevOps org with the vso.auditlog scope
#   - Auditing must be enabled in the target org:
#     Organization Settings > Policies > Log Audit Events = On
#   - The connecting user must have "View audit log" permission set to Allow
#     in the target org
#   - az CLI, curl, jq, and python3 must be installed
#
# Usage:
#   chmod +x add-ado-connector.sh
#   ./add-ado-connector.sh

set -euo pipefail

# ——— Check prerequisites ———
for cmd in az curl jq python3; do
    if ! command -v "${cmd}" &>/dev/null; then
        echo "ERROR: '${cmd}' is required but not installed."
        exit 1
    fi
done

# ——— Prompt for inputs ———
read -rp "Subscription ID: " SUBSCRIPTION_ID
read -rp "Resource Group Name: " RESOURCE_GROUP
read -rp "Sentinel Workspace Name: " WORKSPACE_NAME
read -rp "Azure DevOps Organization Name (new org to connect): " ORG_NAME
read -rp "Entra Tenant ID: " TENANT_ID
read -rp "App Client ID: " CLIENT_ID
read -rsp "App Client Secret: " CLIENT_SECRET
echo
read -rp "Data Collection Endpoint URI: " DCE_URI
read -rp "Data Collection Rule Immutable ID: " DCR_IMMUTABLE_ID

# ——— Derived values ———
CONNECTOR_ID="AzureDevOpsAuditLogs-${ORG_NAME}"
API_VERSION="2024-09-01"
TOKEN_ENDPOINT="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token"
AUTH_ENDPOINT="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize"
API_ENDPOINT="https://auditservice.dev.azure.com/${ORG_NAME}/_apis/audit/auditlog?api-version=7.2-preview"
REDIRECT_URI="https://portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights"

# ——— OAuth authorization ———
echo ""
echo "========================================"
echo " OAuth Authorization Required"
echo "========================================"
echo ""
echo "Open this URL in a browser and sign in with a user that has"
echo "'View audit log' permission in the '${ORG_NAME}' org:"
echo ""

ENCODED_REDIRECT_URI=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${REDIRECT_URI}'))")
echo "  ${AUTH_ENDPOINT}?client_id=${CLIENT_ID}&response_type=code&redirect_uri=${ENCODED_REDIRECT_URI}&scope=499b84ac-1321-427f-aa17-267ca6975798/.default+openid+offline_access"
echo ""
read -rp "Paste the authorization code from the redirect URL: " AUTH_CODE

# ——— Build request body (using jq to safely handle special characters in secrets) ———
BODY=$(jq -n \
    --arg clientSecret      "${CLIENT_SECRET}" \
    --arg clientId          "${CLIENT_ID}" \
    --arg authCode          "${AUTH_CODE}" \
    --arg dceUri            "${DCE_URI}" \
    --arg dcrId             "${DCR_IMMUTABLE_ID}" \
    --arg apiEndpoint        "${API_ENDPOINT}" \
    --arg tokenEndpoint     "${TOKEN_ENDPOINT}" \
    --arg authEndpoint      "${AUTH_ENDPOINT}" \
    --arg redirectUri       "${REDIRECT_URI}" \
    '{
        kind: "RestApiPoller",
        properties: {
            connectorDefinitionName: "AzureDevOpsAuditLogs",
            dataType: "ADOAuditLogs_CL",
            dcrConfig: {
                streamName: "Custom-ADOAuditLogs",
                dataCollectionEndpoint: $dceUri,
                dataCollectionRuleImmutableId: $dcrId
            },
            auth: {
                type: "OAuth2",
                ClientSecret: $clientSecret,
                ClientId: $clientId,
                GrantType: "authorization_code",
                AuthorizationCode: $authCode,
                RedirectUri: $redirectUri,
                scope: "499b84ac-1321-427f-aa17-267ca6975798/.default openid offline_access",
                TokenEndpoint: $tokenEndpoint,
                AuthorizationEndpoint: $authEndpoint,
                TokenEndpointQueryParameters: {},
                TokenEndpointHeaders: {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            },
            request: {
                apiEndpoint: $apiEndpoint,
                httpMethod: "GET",
                queryWindowInMin: 5,
                queryTimeFormat: "yyyy-MM-ddTHH:mm:ss.000000+00:00",
                rateLimitQps: 1,
                retryCount: 3,
                timeoutInSeconds: 60,
                StartTimeAttributeName: "startTime",
                EndTimeAttributeName: "endTime",
                queryParameters: {
                    from: "{_QueryWindowStartTime}",
                    to: "{_QueryWindowEndTime}"
                },
                headers: {
                    Accept: "application/json",
                    "User-Agent": "Scuba"
                }
            },
            response: {
                eventsJsonPaths: ["$.decoratedAuditLogEntries"],
                format: "json"
            },
            paging: {
                pagingType: "NextPageToken",
                nextPageTokenJsonPath: "$.continuationToken",
                nextPageParaName: "continuationToken",
                hasNextFlagJsonPath: "$.hasMore"
            }
        }
    }')

# ——— Get Azure access token ———
echo ""
echo "Fetching Azure access token..."
ACCESS_TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

# ——— Deploy the connector ———
URI="https://management.azure.com/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.OperationalInsights/workspaces/${WORKSPACE_NAME}/providers/Microsoft.SecurityInsights/dataConnectors/${CONNECTOR_ID}?api-version=${API_VERSION}"

echo "Deploying connector '${CONNECTOR_ID}' for org '${ORG_NAME}'..."

RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
    "${URI}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${BODY}")

HTTP_CODE=$(echo "${RESPONSE}" | tail -1)
RESPONSE_BODY=$(echo "${RESPONSE}" | sed '$d')

if [[ "${HTTP_CODE}" =~ ^2 ]]; then
    echo ""
    echo "SUCCESS: Connector '${CONNECTOR_ID}' deployed for org '${ORG_NAME}'."
    echo "Audit logs will flow into the ADOAuditLogs_CL table."
else
    echo ""
    echo "FAILED (HTTP ${HTTP_CODE}):"
    echo "${RESPONSE_BODY}" | python3 -m json.tool 2>/dev/null || echo "${RESPONSE_BODY}"
    exit 1
fi
