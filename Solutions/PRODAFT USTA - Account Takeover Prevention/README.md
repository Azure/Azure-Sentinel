# PRODAFT USTA - Account Takeover Prevention — Microsoft Sentinel Solution

Ingests **compromised corporate credentials** from the PRODAFT USTA Account Takeover
Prevention API into Microsoft Sentinel via a codeless (Codeless Connector Framework)
data connector. Plaintext passwords are never stored — the DCR transform drops them at
ingestion and retains only password strength signals (score and length).

## Contents

| Content | Items |
|---|---|
| Data connector (CCF) | `Data Connectors/PRODAFTUstaATP_ccp/` — ConnectorDefinition, PollingConfig, DCR, Table |
| Parser | `PRODAFTUstaCompromisedCredentials` — query-time dedup (one row per `TicketId`) |
| Analytic rules | Corporate credential compromised; Compromised credential used in successful sign-in |
| Hunting query | Infostealer exposure across corporate identities |
| Workbook | `PRODAFTUstaATPOverview` |
| Playbook | `PRODAFTUstaATP-Backfill` — on-demand historical backfill |

## Deployment

### From the portal (Content Hub)

1. Once published, install **PRODAFT USTA - Account Takeover Prevention** from
   **Microsoft Sentinel → Content hub**.
2. Open **Configuration → Data connectors → PRODAFT USTA - Account Takeover Prevention
   (via Codeless Connector Framework)**, enter the USTA base URL and your API key, and
   select **Connect**. The connector polls every minute going forward.
3. To load history, deploy and run the **PRODAFTUstaATP-Backfill** playbook once — see
   [Playbooks/PRODAFTUstaATP-Backfill/readme.md](Playbooks/PRODAFTUstaATP-Backfill/readme.md).

### Via scripts (this repository)

1. Generate the deployable package with the repo's packaging tool (creates
   `Package/mainTemplate.json` + `Package/createUiDefinition.json`). The tool is a
   PowerShell 7 script and runs the same on Windows, Linux, and macOS via `pwsh`.
   One-time setup (see `Tools/Create-Azure-Sentinel-Solution/README.md`):
   PowerShell 7.1+, Node.js, and the YAML module (`pwsh -Command 'Install-Module powershell-yaml -Scope CurrentUser'`).

   ```bash
   # from the repository root — pass the ABSOLUTE path to this solution's Data folder
   # (the tool rejects paths that start with "Solutions/")
   pwsh Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1 \
     -SolutionDataFolderPath "$(pwd)/Solutions/PRODAFT USTA - Account Takeover Prevention/Data" \
     -VersionMode local -VersionBump patch
   ```

   `-VersionMode local` versions from this solution's Data file and bumps it on every run
   (`patch`/`minor`/`major`), writing the new version back. The default `catalog` mode looks
   the offer up in the Content Hub catalog and, for unpublished solutions, falls back to
   3.0.0. Package versions must be **3.x**: the tool aborts on 1.x versions and 2.x
   builds only the deprecated templateSpec format, so the Content Hub packaging format
   (`contentSchemaVersion` 3) requires 3.x — which is why the initial release is 3.0.0.

2. Deploy from scratch — creates the resource group and the Log Analytics workspace,
   onboards the workspace to Microsoft Sentinel, then deploys the solution package into it:

   ```bash
   # ---- configuration ----
   SUB="<subscription-id>"
   RG="<usta-sentinel-resource-group>"
   WS="<usta-sentinel-workspace>"
   LOCATION="westeurope"

   az account set --subscription "$SUB"

   # 1. Resource group
   az group create --name "$RG" --location "$LOCATION"

   # 2. Log Analytics workspace
   az monitor log-analytics workspace create \
     --resource-group "$RG" \
     --workspace-name "$WS" \
     --location "$LOCATION"

   # 3. Onboard the workspace to Microsoft Sentinel
   az rest --method PUT \
     --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=2022-12-01-preview" \
     --body '{"properties": {}}'

   # 4. Deploy the solution package
   az deployment group create \
     --resource-group "$RG" \
     --template-file "Solutions/PRODAFT USTA - Account Takeover Prevention/Package/mainTemplate.json" \
     --parameters workspace="$WS" workspace-location="$LOCATION"
   ```

   Already have a Sentinel-enabled workspace? Set `RG`/`WS` to it and run only step 4.

3. Connect the data connector (portal step 2 above), then run the backfill playbook for
   history.

## Time semantics and deduplication

* `TimeGenerated` is set at **ingestion time** by the DCR; the true USTA event time is
  preserved in `Created` (and `StatusTimestamp`). All rules, the hunting query, and the
  workbook filter on `Created`, so backfilled history lands on the correct dates and does
  not trigger an alert storm.
* Log Analytics is append-only; the same `TicketId` can arrive more than once (backfill
  overlapping the poller, or a ticket re-fetched after a status change). Query the
  **`PRODAFTUstaCompromisedCredentials`** parser function instead of the raw `_CL` table —
  it returns exactly one row per ticket (the most recently ingested copy).
