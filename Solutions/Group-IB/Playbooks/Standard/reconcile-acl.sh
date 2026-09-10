#!/usr/bin/env bash
#
# reconcile-acl.sh — Add the current Logic App MSI as an access-policy
# principal on the Standard package's managed API connections.
#
# WHEN TO RUN THIS
#
#   Only if a workflow run returns 403 "Permission denied due to missing
#   connection ACL" on actions that authenticate through a managed API
#   connection (Upload_Indicators_V2, Save_seqUpdate_in_loop, etc.) AFTER
#   a redeploy of the Logic App.
#
#   First-time deploys on a fresh tenant do NOT need this script — the
#   Designer's "Add new" creates the access policy correctly when no
#   surviving token-store entry exists.
#
# WHY IT EXISTS
#
#   Microsoft.Web/connections resources retain their access-policy
#   registration in the Logic Apps managed-API token store even after the
#   ARM resource is deleted. When a redeploy's Designer-bind step recreates
#   a connection with the same name (e.g. azuresentinel-1), Azure
#   reattaches that surviving entry, which carries forward the previous
#   MSI's accessPolicies. The current MSI doesn't match, so token exchange
#   returns 403 even though the workspace-scoped RBAC is correct.
#
# BEHAVIOR
#
#   - Targeted cleanup of *this Logic App's own orphans*: deletes any access
#     policy whose name starts with "<LogicAppName>-" and whose principal
#     does not match the current MSI. Leaves all other policies alone.
#     Empirically, the apim.net token-exchange path 403s on the first
#     stale policy it evaluates without falling through to a later matching
#     one — purely-additive PUTs do not unblock the runtime, so we must
#     prune our own orphans before re-asserting the current policy.
#   - Upserts the current MSI as an access-policy principal.
#   - Idempotent: safe to re-run; safe to run on a fresh tenant (in which
#     case there's nothing to prune and the PUT just re-affirms the
#     Designer's existing policy).
#   - Restarts the Logic App at the end to flush the token cache.
#
# USAGE
#
#   ./reconcile-acl.sh <resource-group> <logic-app-name>
#
# EXAMPLE
#
#   ./reconcile-acl.sh sentinel-gibtia-rg GIBTIA-Standard
#
set -euo pipefail

# `az ... -o tsv` returns one record per line. Split on newlines only, and disable
# globbing, so a name containing a space or a glob character can't word-split or
# expand into filenames. Azure resource names don't currently allow either, so
# this is defensive rather than a live bug fix.
IFS=$'\n'
set -f

if [ $# -lt 2 ]; then
  cat >&2 <<USAGE
Usage: $0 <resource-group> <logic-app-name>

Example:
  $0 sentinel-gibtia-rg GIBTIA-Standard
USAGE
  exit 1
fi

RG="$1"
APP="$2"

echo "=== Phase 1 — Discovering current Logic App identity ==="
MSI=$(az webapp identity show -g "$RG" -n "$APP" --query principalId -o tsv 2>/dev/null || echo "")
if [ -z "$MSI" ]; then
  echo "ERROR: Logic App '$APP' in RG '$RG' not found or has no system-assigned MSI." >&2
  exit 1
fi
TENANT=$(az account show --query tenantId -o tsv)
LOC=$(az resource show -g "$RG" --resource-type Microsoft.Web/sites -n "$APP" \
        --query location -o tsv)
POLICY_NAME="$APP-$MSI"

echo "  Logic App:  $APP"
echo "  MSI:        $MSI"
echo "  Tenant:     $TENANT"
echo "  Location:   $LOC"
echo "  Policy:     $POLICY_NAME"
echo

echo "=== Phase 2 — Finding Standard-package managed API connections ==="
CONNS=$(az resource list -g "$RG" --resource-type Microsoft.Web/connections \
  --query "[?contains(name, 'azuresentinel') || contains(name, 'azureloganalyticsdatacollector')].name" \
  -o tsv)

if [ -z "$CONNS" ]; then
  echo "ERROR: No managed API connections matching azuresentinel*/azureloganalyticsdatacollector* found in '$RG'." >&2
  echo "       Has the Designer-bind step completed?" >&2
  exit 1
fi

echo "$CONNS" | sed 's/^/  /'
echo

echo "=== Phase 3 — Reconciling MSI access policy on each connection ==="
for CONN_NAME in $CONNS; do
  CONN_ID=$(az resource show -g "$RG" -n "$CONN_NAME" \
    --resource-type Microsoft.Web/connections --api-version 2016-06-01 \
    --query id -o tsv)
  echo "  $CONN_NAME"

  # Find orphans: policies named "<LogicAppName>-*" whose principal isn't the current MSI.
  STALE=$(az rest --method GET \
    --url "https://management.azure.com${CONN_ID}/accessPolicies?api-version=2016-06-01" \
    --query "value[?starts_with(name, '${APP}-') && properties.principal.identity.objectId != '${MSI}'].name" \
    -o tsv)

  for P in $STALE; do
    echo "    deleting orphan policy: $P"
    az rest --method DELETE \
      --url "https://management.azure.com${CONN_ID}/accessPolicies/${P}?api-version=2016-06-01" \
      --output none
  done

  az rest --method PUT \
    --url "https://management.azure.com${CONN_ID}/accessPolicies/${POLICY_NAME}?api-version=2016-06-01" \
    --body "{
      \"location\": \"${LOC}\",
      \"properties\": {
        \"principal\": {
          \"type\": \"ActiveDirectory\",
          \"identity\": {
            \"tenantId\": \"${TENANT}\",
            \"objectId\": \"${MSI}\"
          }
        }
      }
    }" \
    --output none
  echo "    upserted access policy for MSI $MSI"
done
echo

echo "=== Phase 4 — Restarting Logic App to flush token cache ==="
az logicapp restart -g "$RG" -n "$APP" --output none 2>/dev/null \
  || az webapp restart -g "$RG" -n "$APP" --output none
echo "  Restart issued."
echo

cat <<DONE
====================================================================
reconcile-acl.sh complete.
====================================================================

Next steps:

  1. Wait ~60 seconds for the host to come back online.
  2. Re-trigger the failing workflow from the Portal:
     Logic App -> Workflows -> <workflow-name> -> Run Trigger.
  3. Inspect Run history. Actions that previously returned 403 on
     'missing connection ACL' should now succeed.

Note (cleanup scope):

  Orphan policies named "${APP}-*" with non-current principals were
  pruned. Any other policies on these connections (e.g. policies named
  outside the "${APP}-" pattern, possibly added by other tools or other
  Logic Apps that share the connection) were left in place.

  Why prune at all: the runtime's token-exchange evaluates policies
  in order and returns 403 on the first stale principal it finds,
  without falling through to a later matching policy. Purely additive
  PUTs leave the runtime blocked.
DONE
