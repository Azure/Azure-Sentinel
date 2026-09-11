# Data Connectors

## Files

### `RecordedFuture_ConnectorDefinition.json`
`Customizable` connector definition for the **Recorded Future - Log Ingestion** tile.
Listed in `../Data/Solution_RecordedFuture.json` and baked into `../Package/mainTemplate.json`
by the packaging tool. This is what makes the connector appear in the Sentinel Data Connectors
gallery after a Content Hub / solution install.

### `azuredeploy.json`
Standalone ARM template that deploys the full infrastructure stack shared by the Log Ingestion
API playbooks:
- Data Collection Endpoint (DCE)
- 5 Data Collection Rules (DCRs)
- 5 Log Analytics custom tables (`RecordedFuturePlaybookAlerts_V2_CL`, `RecordedFutureClassicAlerts_V2_CL`,
  `RecordedFutureThreatMap_V2_CL`, `RecordedFutureThreatMapMalware_V2_CL`, `RecordedFutureSandboxResults_V2_CL`)
- Connector definition tile (see duplication note below)

Used by the "Deploy to Azure" button in the [Playbooks README](../Playbooks/readme.md) and in the
connector's own instruction steps. Deploy this before deploying any of the 6 playbooks that use
the Log Ingestion API (`RecordedFuture-Alert-Importer`, `RecordedFuture-Playbook-Alert-Importer`,
`RecordedFuture-ThreatMap-Importer`, `RecordedFuture-ThreatMapMalware-Importer`,
`RecordedFuture-Sandbox_StorageAccount`, `RecordedFuture-Sandbox_Outlook_Attachment`).

## Known duplication

### Connector tile

The connector UI tile content exists in two forms due to limitations of the packaging/deployment model:

| Content | Packager source | Standalone ARM |
|---|---|---|
| Connector UI tile | `RecordedFuture_ConnectorDefinition.json` | `azuredeploy.json` (`Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions` resource, `kind: Customizable`) |

If you update one (queries, description, instruction steps, connectivity criteria, etc.), update
its counterpart.
