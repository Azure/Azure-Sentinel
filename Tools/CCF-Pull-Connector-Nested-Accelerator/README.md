# CCF Pull Connector — Nested API Accelerator

This accelerator demonstrates the **CCF nested API polling pattern** in Microsoft Sentinel end-to-end. It provides:

- A **mock Contoso Incident API** (Azure Function App) with two HTTP endpoints  
- A **CCF RestApiPoller connector** that chains the two calls using nested steps  
- A fully working **`ContosoIncidents_CL`** table receiving enriched incident records

Use this accelerator to learn how the CCF nested polling pattern works, test connector configurations, or use it as a starting template for your own multi-call REST API connectors.

---

## GitHub Copilot Quick Deploy

### Before You Start

| Requirement | Details |
|---|---|
| **VS Code** | With the [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) extension installed and signed in |
| **Azure CLI** | Installed and logged in (`az login`). [Install guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) |
| **Azure subscription** | With Contributor role on the subscription where you'll deploy |
| **This repo cloned locally** | Agent reads `agent-instructions.md` and deploys `ContosoIncidents/Package/mainTemplate.json` from disk |

**What gets deployed:**

- **Azure Function App** — the mock Contoso Incident API (list + detail endpoints)
- **Log Analytics workspace** — new or existing; Sentinel is enabled on it
- **Data Collection Endpoint and Rule** — DCE and DCR with stream declaration and KQL transform
- **`ContosoIncidents_CL` table** — custom Log Analytics table for the ingested records
- **CCF connector** — the `RestApiPoller` data connector and connector UI definition

Paste the following into **GitHub Copilot Chat** in VS Code (Agent mode):

```
Load and follow the deployment instructions at Tools/CCF-Pull-Connector-Nested-Accelerator/agent-instructions.md. Let's deploy a CCF nested API connector.
```

The agent collects all required values, generating names you haven't specified, then deploys end-to-end and verifies data is flowing into `ContosoIncidents_CL`. The only manual step is clicking **Connect** once in the Sentinel portal.

> Full agent instructions: [`agent-instructions.md`](./agent-instructions.md)

---

## Architecture

```
Microsoft Sentinel (CCF RestApiPoller)
        │
        │  1. GET /incidents?startTime=...&endTime=...
        ▼
Contoso Mock API (Azure Function App)
        │  → { "incidents": [{ "incidentId": "INC-001" }, ...] }
        │
        │  2. GET /incidents/INC-001/details
        │  2. GET /incidents/INC-002/details  (one call per incidentId)
        │  ...
        ▼
Contoso Mock API
        │  → { "incidentId": "INC-001", "title": "...", "severity": "High", ... }
        │
        ▼
DCR transform → ContosoIncidents_CL table
```

The CCF engine extracts `incidentId` from each row returned by step 1 and substitutes it into the step 2 URL (`/incidents/$incidentId$/details`). The child response from each detail call is sent as a flat record to the DCR stream. The parent response is used only to extract the placeholder value.

---

## Components

| Component | Path | Description |
|---|---|---|
| Mock API Functions | `MockApi/` | Python Azure Functions serving the list and detail endpoints |
| Mock API ARM template | `MockApi/azuredeploy_MockApi.json` | Deploys Function App infrastructure (Storage, App Insights, Function App) |
| Table definition | `ContosoIncidents/Data Connectors/…/ContosoIncidents_Table.json` | Schema for `ContosoIncidents_CL` |
| DCR definition | `ContosoIncidents/Data Connectors/…/ContosoIncidents_DCR.json` | Stream declaration and transformKql |
| Poller config | `ContosoIncidents/Data Connectors/…/ContosoIncidents_PollerConfig.json` | RestApiPoller with nested step configuration |
| Connector UI | `ContosoIncidents/Data Connectors/…/ContosoIncidents_ConnectorDefinition.json` | Sentinel data connector UI definition |
| Solution template | `ContosoIncidents/Package/mainTemplate.json` | ARM template: deploys DCE, table, DCR, connector definition, and poller |

---

## Mock API Endpoints

The mock API returns static data and requires API key authentication via the `x-functions-key` request header. The key is retrieved automatically during deployment.

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/incidents?startTime={t}&endTime={t}` | Returns a list of 5 incident identifiers |
| `GET` | `/api/incidents/{incidentId}/details` | Returns the full record for a given incident |

**Sample list response:**
```json
{
  "incidents": [
    { "incidentId": "INC-001" },
    { "incidentId": "INC-002" },
    { "incidentId": "INC-003" },
    { "incidentId": "INC-004" },
    { "incidentId": "INC-005" }
  ]
}
```

**Sample detail response:**
```json
{
  "incidentId": "INC-001",
  "title": "Suspicious login attempt",
  "severity": "High",
  "status": "Active",
  "affectedUser": "alice@contoso.com",
  "sourceIp": "198.51.100.42",
  "createdAt": "2026-05-30T14:22:00Z"
}
```

---

## Output Table Schema — `ContosoIncidents_CL`

| Column | Type | Source |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time, set to `now()` by the DCR transform |
| `IncidentId` | string | `incidentId` from the API response |
| `Title` | string | `title` from the API response |
| `Severity` | string | `severity` from the API response. Values: Critical, High, Medium, Low |
| `Status` | string | `status` from the API response. Values: Active, Investigating, Resolved, Closed |
| `AffectedUser` | string | `affectedUser` from the API response |
| `SourceIp` | string | `sourceIp` from the API response |

---

## Manual Deployment

### Step 1 — Deploy the Mock API

Deploy the Function App infrastructure:

```powershell
az group create \
  --name contoso-mock-api-rg \
  --location eastus

az deployment group create \
  --resource-group contoso-mock-api-rg \
  --template-file "Tools/CCF-Pull-Connector-Nested-Accelerator/MockApi/azuredeploy_MockApi.json" \
  --parameters FunctionAppName=ContosoMockApi \
  --output table
```

Note the `mockApiBaseUrl` and `functionAppName` from the deployment output.

### Step 2 — Deploy the Mock API Code

Zip the `MockApi/` folder and deploy it:

```powershell
# From the workspace root
Compress-Archive -Path "Tools/CCF-Pull-Connector-Nested-Accelerator/MockApi/*" -DestinationPath contosoapi.zip -Force

az functionapp deployment source config-zip `
  --name <functionAppName> `
  --resource-group contoso-mock-api-rg `
  --src contosoapi.zip
```

Verify the endpoints respond:

```powershell
$base = "<mockApiBaseUrl>"
Invoke-RestMethod "$base/incidents" | ConvertTo-Json
Invoke-RestMethod "$base/incidents/INC-001/details" | ConvertTo-Json
```

### Step 3 — Deploy the Sentinel Connector

```powershell
# Write parameters file (the hyphen in workspace-location causes az CLI issues when passed inline)
@{
  '$schema'      = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#'
  contentVersion = '1.0.0.0'
  parameters     = @{
    workspace            = @{ value = '<workspace-name>' }
    'workspace-location' = @{ value = '<region>' }
  }
} | ConvertTo-Json -Depth 5 | Out-File deploy-params.json -Encoding utf8

az deployment group create `
  --resource-group <sentinel-workspace-rg> `
  --template-file "Tools/CCF-Pull-Connector-Nested-Accelerator/ContosoIncidents/Package/mainTemplate.json" `
  --parameters "@deploy-params.json" `
  --output table
```

### Step 4 — Verify Data

After clicking **Connect** in the Sentinel portal (Step 4 in the connector UI), allow 5–15 minutes for the first poll cycle, then query in Sentinel Logs:

```kql
ContosoIncidents_CL
| sort by TimeGenerated desc
| take 10
```

You should see 5 rows, one per mock incident, with all columns populated.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ContosoIncidents_CL` table not found | ARM deployment failed or table not created | Re-run `mainTemplate.json` and check `provisioningState` |
| No rows after 15 minutes | Mock API not reachable | Test endpoints manually with `Invoke-RestMethod`; check Function App is running |
| All rows show `TimeGenerated = now()` | Expected: the DCR transform sets `TimeGenerated = now()` for all records | No action needed |
| ARM deployment fails on `dataConnectors` resource | Connector definition not yet provisioned | Re-run the template. This is a transient race condition. |
| Function App returns 404 for `/api/incidents` | Code not deployed or route not registered | Re-run the zip deploy step; confirm `SCM_DO_BUILD_DURING_DEPLOYMENT=true` in app settings |
| `workspace-location` mismatch error | Parameter passed with wrong region | Must exactly match `az monitor log-analytics workspace show --query location` |

---

## Security Notes

The mock API uses **Azure Functions API key authentication** (`x-functions-key` header). The key is retrieved at deploy time and passed to the connector as a parameter; the CCF poller sends it with every request. For production connectors, configure the appropriate `auth` block in the `RestApiPoller` (API Key, OAuth2, Basic, etc.) with matching `authLevel` on your Function App or API endpoint.

---

## Related

- [CCF Blob Connector Accelerator](../CCF-Blob-Connector-Accelerator/)
- [Nested API polling reference](https://learn.microsoft.com/azure/sentinel/ccf-nested-api-polling)
- [Create a codeless connector](https://learn.microsoft.com/azure/sentinel/create-codeless-connector)
