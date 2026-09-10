#!/usr/bin/env bash
#
# Group-IB TI → Microsoft Sentinel — Standard Logic App post-deploy automation.
#
# Run AFTER deploying infrastructure-arm.json. This script does everything
# between "infrastructure deployed" and "workflows running" except the one
# manual Designer-bind step in the middle, which Azure cannot automate today.
#
# Usage:
#   ./post-deploy.sh <resource-group> <logic-app-name> <workspace-name>
#
# Example:
#   ./post-deploy.sh sentinel-gibtia-rg GIBTIA-Standard sentinel-gibtia-ws
#
# Prerequisites:
#   - Azure CLI ≥ 2.50 with the `logicapp` extension
#       az extension add --name logicapp
#   - `zip` binary on PATH
#   - You are signed in (`az login`) with rights to assign IAM roles on the
#     workspace AND to deploy to the Logic App.
#   - The infrastructure-arm.json has already been deployed.
#
# What this script does, in order:
#   1. Discovers your deployment (subscription, location, MSI, workspace ID).
#   2. Assigns the two required workspace roles to the Logic App's MSI:
#        - Microsoft Sentinel Contributor   (Sentinel TI upload + LA query)
#        - Log Analytics Contributor        (data-plane writes to GIB*_CL)
#   3. Builds a placeholder connections.json (api.id-only) so the Designer
#      can render workflows at the next step, then zip-deploys the workflows.
#   4. PROMPTS YOU to do two Designer "Add new" binds (the only manual step).
#   5. Polls Azure for the two new connection resources to gain populated
#      connectionRuntimeUrl values.
#   6. Writes the final connections.json with `azuresentinel` and
#      `azureloganalyticsdatacollector` as bare-name keys pointing at the
#      Designer-created resources, and zip-deploys again.
#   7. Restarts the Logic App.
#
set -euo pipefail

if [ $# -lt 3 ]; then
  cat >&2 <<USAGE
Usage: $0 <resource-group> <logic-app-name> <workspace-name>

Example:
  $0 sentinel-gibtia-rg GIBTIA-Standard sentinel-gibtia-ws
USAGE
  exit 1
fi

RG="$1"
APP="$2"
WS_NAME="$3"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/.build"
PKG_DIR="$BUILD_DIR/pkg"
mkdir -p "$BUILD_DIR"

# Stage the deployable package into $PKG_DIR and zip it.
#
# The generated connections.json carries live tenant values (subscription GUID,
# resource group, connection resource IDs, connectionRuntimeUrl). It is staged
# here and never written back over the git-tracked Standard/connections.json,
# which must stay the empty shipping default — see DEV_NOTES.md sanity-check #5.
#
# This copies an allowlist (workflow folders only) rather than zipping the whole
# directory with -x exclusions, so ops scripts and infra templates cannot leak
# into the Logic App content share by being forgotten in the exclusion list.
stage_package() {
  rm -rf "$PKG_DIR"
  mkdir -p "$PKG_DIR"
  for d in "$SCRIPT_DIR"/GIBTIA_*/; do
    [ -d "$d" ] || continue
    cp -R "$d" "$PKG_DIR/"
  done
  cp "$BUILD_DIR/connections.json" "$PKG_DIR/connections.json"
  if [ -f "$SCRIPT_DIR/host.json" ]; then
    cp "$SCRIPT_DIR/host.json" "$PKG_DIR/host.json"
  fi
  rm -f "$BUILD_DIR/gibtia-standard.zip"
  ( cd "$PKG_DIR" && zip -r "$BUILD_DIR/gibtia-standard.zip" . -x "*.DS_Store" > /dev/null )
}

# Ensure az logicapp extension is available (idempotent).
az extension add --name logicapp --only-show-errors 2>/dev/null || true

# ---------- Phase 1: discover deployment ----------
echo "=== Phase 1 — Discovering deployment ==="
SUB=$(az account show --query id -o tsv)
LOC=$(az resource show -g "$RG" --resource-type Microsoft.Web/sites -n "$APP" --query location -o tsv)
MSI=$(az webapp identity show -g "$RG" -n "$APP" --query principalId -o tsv)
WS_ID=$(az resource show -g "$RG" --resource-type Microsoft.OperationalInsights/workspaces -n "$WS_NAME" --query id -o tsv)
echo "  Subscription:    $SUB"
echo "  Resource Group:  $RG"
echo "  Location:        $LOC"
echo "  Logic App:       $APP"
echo "  Logic App MSI:   $MSI"
echo "  Workspace:       $WS_NAME"

# ---------- Phase 2: assign MSI roles ----------
echo
echo "=== Phase 2 — Assigning MSI roles on workspace ==="
ROLE_FAILED=0
for role in "Microsoft Sentinel Contributor" "Log Analytics Contributor"; do
  ROLE_ERR="$BUILD_DIR/.role-err"
  if az role assignment create --assignee "$MSI" --role "$role" --scope "$WS_ID" --output none 2>"$ROLE_ERR"; then
    echo "  Assigned: $role"
  # An existing assignment is the only benign failure. Anything else -- most often
  # the deploying principal lacking Owner/User Access Administrator -- must be
  # surfaced, not swallowed: it resurfaces later as an Upload_Indicators_V2 401
  # that looks exactly like RBAC propagation lag (DEV_NOTES.md #12) and gets
  # waved through.
  elif grep -qi "already exists\|RoleAssignmentExists" "$ROLE_ERR"; then
    echo "  Already present: $role"
  else
    echo "  !! FAILED to assign: $role"
    sed 's/^/     /' "$ROLE_ERR" >&2
    ROLE_FAILED=1
  fi
  rm -f "$ROLE_ERR"
done
if [ "$ROLE_FAILED" -eq 1 ]; then
  echo
  echo "  !! One or more role assignments FAILED (see errors above)."
  echo "     This is NOT propagation lag and will not resolve on its own."
  echo "     Workflows will 401 on Upload_Indicators_V2 and 403 on Log Analytics writes."
  echo "     Assign both roles at the workspace scope with an account holding"
  echo "     Owner or User Access Administrator, then re-run this script."
  echo
fi
echo "  RBAC propagation takes 5-15 minutes; the rest of the script proceeds in parallel."

# ---------- Phase 3: placeholder connections.json + initial workflow deploy ----------
echo
echo "=== Phase 3 — Initial workflow deploy with placeholder connections.json ==="
cat > "$BUILD_DIR/connections.json" <<EOF
{
    "managedApiConnections": {
        "azuresentinel": {
            "api": {
                "id": "/subscriptions/$SUB/providers/Microsoft.Web/locations/$LOC/managedApis/azuresentinel"
            }
        },
        "azureloganalyticsdatacollector": {
            "api": {
                "id": "/subscriptions/$SUB/providers/Microsoft.Web/locations/$LOC/managedApis/azureloganalyticsdatacollector"
            }
        }
    },
    "serviceProviderConnections": {}
}
EOF

stage_package

az logicapp deployment source config-zip \
  --resource-group "$RG" \
  --name "$APP" \
  --src "$BUILD_DIR/gibtia-standard.zip" \
  --output none
echo "  Workflows uploaded."

# ---------- Phase 4: manual Designer-bind step ----------
echo
echo "===================================================================="
echo "  PHASE 4 — MANUAL STEP REQUIRED"
echo "===================================================================="
cat <<INSTRUCTIONS

In the Azure Portal (or the Defender portal):

  1. Logic App ($APP) → Workflows → GIBTIA_IndicatorProcessor_v2 → Designer.
  2. Click the action 'Upload_Indicators_V2'.
  3. Right-pane Connection section → 'Add new'.
  4. Authentication: Managed identity → System-assigned managed identity.
  5. Click Create.
  6. Click 'Save' in the top toolbar of the Designer.

  7. Logic App → Workflows → GIBTIA_IOC_Primary_Updated → Designer.
  8. Click the action 'Save_seqUpdate_in_loop'.
  9. Right-pane Connection section → 'Add new'.
 10. Authentication: Managed identity → System-assigned managed identity.
 11. Click Create.
 12. Click 'Save' in the top toolbar of the Designer.

Both saves should produce a green "Workflow saved" toast.

INSTRUCTIONS

read -p "Press ENTER once both Designer binds are saved..." -r _

# ---------- Phase 5: poll for new connection resources ----------
echo
echo "=== Phase 5 — Polling for Designer-created connections ==="
SENTINEL_NAME="" SENTINEL_URL="" SENTINEL_ID=""
LA_NAME=""       LA_URL=""       LA_ID=""

find_conn_with_url() {
  local connector_substring="$1"
  for cn in $(az resource list -g "$RG" --resource-type Microsoft.Web/connections \
                --query "[?contains(name, '$connector_substring')].name" -o tsv); do
    local url
    url=$(az resource show -g "$RG" --resource-type Microsoft.Web/connections \
            -n "$cn" --api-version 2018-07-01-preview \
            --query "properties.connectionRuntimeUrl" -o tsv 2>/dev/null || echo "")
    if [ -n "$url" ]; then
      echo "$cn|$url"
      return 0
    fi
  done
  return 1
}

for attempt in $(seq 1 30); do
  if [ -z "$SENTINEL_URL" ]; then
    if hit=$(find_conn_with_url "azuresentinel"); then
      SENTINEL_NAME="${hit%%|*}"
      SENTINEL_URL="${hit##*|}"
      SENTINEL_ID="/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/connections/$SENTINEL_NAME"
    fi
  fi
  if [ -z "$LA_URL" ]; then
    if hit=$(find_conn_with_url "azureloganalyticsdatacollector"); then
      LA_NAME="${hit%%|*}"
      LA_URL="${hit##*|}"
      LA_ID="/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Web/connections/$LA_NAME"
    fi
  fi

  if [ -n "$SENTINEL_URL" ] && [ -n "$LA_URL" ]; then
    echo "  Found both:"
    echo "    Sentinel:  $SENTINEL_NAME"
    echo "    LA:        $LA_NAME"
    break
  fi

  echo "  Attempt $attempt/30 — connections not yet ready; waiting 30s..."
  sleep 30
done

if [ -z "$SENTINEL_URL" ] || [ -z "$LA_URL" ]; then
  cat >&2 <<ERR
ERROR: timed out (~15 min) waiting for connectionRuntimeUrl on one or both connections.
       Verify the Designer-binds saved successfully (Designer → workflow → Saved toast),
       then re-run this script. Already-assigned roles will be skipped.
ERR
  exit 1
fi

# ---------- Phase 6: final connections.json + redeploy ----------
echo
echo "=== Phase 6 — Final connections.json + workflow redeploy ==="
cat > "$BUILD_DIR/connections.json" <<EOF
{
    "managedApiConnections": {
        "azuresentinel": {
            "api": {
                "id": "/subscriptions/$SUB/providers/Microsoft.Web/locations/$LOC/managedApis/azuresentinel"
            },
            "connection": {
                "id": "$SENTINEL_ID"
            },
            "authentication": {
                "type": "ManagedServiceIdentity"
            },
            "connectionRuntimeUrl": "$SENTINEL_URL",
            "connectionProperties": {
                "authentication": {
                    "type": "ManagedServiceIdentity",
                    "audience": "https://management.core.windows.net/"
                }
            }
        },
        "azureloganalyticsdatacollector": {
            "api": {
                "id": "/subscriptions/$SUB/providers/Microsoft.Web/locations/$LOC/managedApis/azureloganalyticsdatacollector"
            },
            "connection": {
                "id": "$LA_ID"
            },
            "authentication": {
                "type": "ManagedServiceIdentity"
            },
            "connectionRuntimeUrl": "$LA_URL"
        }
    },
    "serviceProviderConnections": {}
}
EOF

stage_package

az logicapp deployment source config-zip \
  --resource-group "$RG" \
  --name "$APP" \
  --src "$BUILD_DIR/gibtia-standard.zip" \
  --output none
echo "  Workflows + final connections.json uploaded."

# ---------- Phase 7: restart ----------
echo
echo "=== Phase 7 — Restarting Logic App ==="
az logicapp restart -g "$RG" -n "$APP" --output none 2>/dev/null \
  || az webapp restart -g "$RG" -n "$APP" --output none
echo "  Restart issued."

# ---------- Done ----------
cat <<DONE

====================================================================
Post-deploy complete.
====================================================================

Resources:
  Logic App:                 $APP
  Sentinel connection:       $SENTINEL_NAME
  LA Data Collector conn:    $LA_NAME

Allow 5-15 minutes for:
  - RBAC propagation (workspace roles)
  - Connection-claim and runtime-URL provisioning by the Standard runtime

Then verify:
  1. Logic App → Workflows → GIBTIA_IOC_Primary_Updated → 'Run Trigger'
  2. Check Run history; the first run's Query_Last_SeqUpdate returns 400
     (expected — tracking table doesn't exist yet; first-run path kicks in).
  3. Within 5 min the IndicatorProcessor adapter fires automatically.
  4. Confirm in Log Analytics:
       ThreatIntelIndicators
       | where SourceSystem contains "Group-IB"
       | order by TimeGenerated desc
       | take 20

If Upload_Indicators_V2 returns 401 in early runs, that's RBAC propagation
catching up — the action's retry policy handles it (10 retries, exp backoff).
DONE

# Exit non-zero if any role assignment failed earlier. The script deliberately
# keeps going after such a failure -- the workflow deploy and connection bind are
# still worth doing -- but the run must not report success, or automation wrapping
# this script treats a broken deployment as a good one. The failure is ~200 lines
# above by now, so restate the cause here.
if [ "$ROLE_FAILED" -eq 1 ]; then
  echo
  echo "!! Exiting non-zero: one or more role assignments FAILED (see above)."
  echo "   The workflows are deployed but will 401 on Upload_Indicators_V2 and 403"
  echo "   on Log Analytics writes until both roles are assigned at workspace scope."
  exit 1
fi
