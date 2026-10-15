#!/usr/bin/env bash
#
# Group-IB TI → Microsoft Sentinel — convert custom tables from the legacy
# HTTP Data Collector API ("classic") to DCR-based, so they can receive data
# through the Logs Ingestion API.
#
# ARM cannot do this: `migrate` is a POST action on the table, not a resource
# property. Hence a script rather than a step in azuredeploy-GIBTIA_LogsIngestion_Infrastructure.json.
#
# Usage:
#   ./migrate-tables.sh <resource-group> <workspace-name> [table ...]
#
# With no table names it migrates every GIB* table that exists in the workspace
# (the shared cursor table plus the 14 context tables); missing ones are skipped.
# This is the one-command upgrade step for a workspace that ran the pre-release
# (Data Collector) playbooks: run it once, then redeploy the playbooks.
#
# Example:
#   ./migrate-tables.sh sentinel-gibtia-rg sentinel-gibtia-ws
#   ./migrate-tables.sh sentinel-gibtia-rg sentinel-gibtia-ws GIBAPTThreat_CL GIBOSIGitRepository_CL
#
# READ THIS BEFORE RUNNING
#
#   * `migrate` CANNOT BE UNDONE. There is no reverse operation and no way to
#     turn a DCR-based table back into a classic one.
#
#   * After migration the legacy Data Collector API keeps writing to columns
#     that already exist, so pre-release playbooks you have not redeployed yet
#     keep working. That stops for a table the moment its schema changes, which
#     the new playbook templates do for the context tables (they add the Record
#     column) — so redeploy each collector right after converting its table, and
#     do not leave a pre-release collector running against a converted table for
#     long. The cursor table's schema never changes, so it is safe indefinitely.
#
#   * Existing data is preserved. Migration converts the table, it does not
#     recreate it.
#
# Prerequisites:
#   - Azure CLI ≥ 2.50, signed in (`az login`)
#   - Log Analytics Contributor on the workspace (the migrate action needs
#     Microsoft.OperationalInsights/workspaces/tables/migrate/action)
#
set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <resource-group> <workspace-name> [table ...]" >&2
    echo "       With no table names, migrates every existing GIB* table (cursor + 14 context tables)." >&2
    exit 2
fi

RG="$1"; shift
WS="$1"; shift

# Every table the 26 collectors write. Tables that do not exist in the workspace are
# skipped, so the default is safe on any deployment, however many collectors it runs.
ALL_TABLES=(
    GIBCollectionTracking_CL
    GIBAPTThreat_CL GIBAPTThreatActor_CL
    GIBHIThreat_CL GIBHIThreatActor_CL GIBHIOpenThreat_CL
    GIBOSIVulnerability_CL GIBOSIPublicLeak_CL GIBOSIGitRepository_CL
    GIBMalwareReport_CL
    GIBCompromisedAccount_CL GIBCompromisedBreachedDB_CL GIBCompromisedBankCard_CL
    GIBCompromisedMaskedCard_CL GIBCompromisedSPD_CL
)
if [ $# -gt 0 ]; then
    TABLES=("$@")
else
    TABLES=("${ALL_TABLES[@]}")
fi

command -v az >/dev/null 2>&1 || { echo "ERROR: Azure CLI (az) not found on PATH." >&2; exit 1; }
az account show >/dev/null 2>&1 || { echo "ERROR: not signed in. Run 'az login'." >&2; exit 1; }

echo "Workspace : $WS  (resource group: $RG)"
echo "Tables    : ${TABLES[*]}"
echo

# ---- Survey first, act second. Nothing is changed in this pass. -------------
declare -a TO_MIGRATE=()
SURVEY_FAILED=0

for t in "${TABLES[@]}"; do
    subtype=$(az monitor log-analytics workspace table show \
                --resource-group "$RG" --workspace-name "$WS" --name "$t" \
                --query "schema.tableSubType" -o tsv 2>/dev/null || echo "__MISSING__")

    case "$subtype" in
        Classic)
            echo "  $t — classic, WILL BE MIGRATED"
            TO_MIGRATE+=("$t")
            ;;
        DataCollectionRuleBased)
            echo "  $t — already DCR-based, skipping"
            ;;
        __MISSING__)
            # Not an error for a fresh workspace: the table is created by ARM
            # (CreateTrackingTable) or on first ingestion instead.
            echo "  $t — does not exist, skipping (create it via the ARM template)"
            ;;
        *)
            echo "  $t — UNEXPECTED tableSubType '$subtype', skipping" >&2
            SURVEY_FAILED=1
            ;;
    esac
done

if [ "$SURVEY_FAILED" -ne 0 ]; then
    echo >&2
    echo "ERROR: at least one table reported an unrecognised subtype. Nothing was migrated." >&2
    echo "       Investigate before re-running — migrate cannot be undone." >&2
    exit 1
fi

if [ ${#TO_MIGRATE[@]} -eq 0 ]; then
    echo
    echo "Nothing to do — no classic tables among the ones requested."
    exit 0
fi

echo
echo "About to migrate ${#TO_MIGRATE[@]} table(s): ${TO_MIGRATE[*]}"
echo "This CANNOT be undone."
printf 'Type the word MIGRATE to continue: '
read -r CONFIRM
if [ "$CONFIRM" != "MIGRATE" ]; then
    echo "Aborted — nothing was changed."
    exit 1
fi
echo

# ---- Act -------------------------------------------------------------------
FAILED=0
for t in "${TO_MIGRATE[@]}"; do
    printf '  migrating %s ... ' "$t"
    if az monitor log-analytics workspace table migrate \
            --resource-group "$RG" --workspace-name "$WS" --table-name "$t" >/dev/null 2>&1; then
        echo "done"
    else
        echo "FAILED"
        FAILED=1
    fi
done

echo
echo "Verifying:"
for t in "${TO_MIGRATE[@]}"; do
    subtype=$(az monitor log-analytics workspace table show \
                --resource-group "$RG" --workspace-name "$WS" --name "$t" \
                --query "schema.tableSubType" -o tsv 2>/dev/null || echo "__ERROR__")
    printf '  %-32s %s\n' "$t" "$subtype"
    [ "$subtype" = "DataCollectionRuleBased" ] || FAILED=1
done

if [ "$FAILED" -ne 0 ]; then
    echo >&2
    echo "ERROR: at least one table did not reach DataCollectionRuleBased." >&2
    exit 1
fi

echo
echo "All requested tables are DCR-based."
echo "Your existing playbooks keep working — do not change these tables' schemas."
