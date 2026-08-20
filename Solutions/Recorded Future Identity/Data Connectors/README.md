# Data Connectors

## Files

### `RFI_AlertImporter_ConnectorDefinition.json`
GenericUI connector definition for the **Recorded Future Identity - Playbook Alert Importer** tile.
Listed in `Data/Solution_RecordedFutureIdentity.json` and baked into `Package/mainTemplate.json`
by the packaging tool. This is what makes the connector appear in the Sentinel Data Connectors
gallery after a Content Hub / solution install.

### `azuredeploy-alert-importer.json`
Standalone ARM template that deploys the full infrastructure stack:
- Data Collection Endpoint (DCE)
- Data Collection Rule (DCR)
- Log Analytics custom table (`RFI_PlaybookAlertResults_V2_CL`)
- Connector definition tile (see duplication note below)

Used by the "Deploy to Azure" button in the README and in the connector's instruction steps.
Deploy this before deploying the playbook.

### `azuredeploy-incident-creation-analytic-rule.json`
Standalone ARM template equivalent of
`Analytic Rules/IncidentCreation/RecordedFutureIdentityExposure.yaml`.
Exists solely to support the "Deploy to Azure" button flow for users who prefer not to
create the rule manually via the Sentinel UI. See duplication note below.

## Known duplication

Two pieces of content exist in two forms due to limitations of the packaging/deployment model:

| Content | Packager source | Standalone ARM |
|---|---|---|
| Connector UI tile | `RFI_AlertImporter_ConnectorDefinition.json` | `azuredeploy-alert-importer.json` |
| Analytic rule | `../Analytic Rules/IncidentCreation/RecordedFutureIdentityExposure.yaml` | `azuredeploy-incident-creation-analytic-rule.json` |

If you update either, update its counterpart. The Content Hub packaging format and standalone
ARM deployments require different file shapes, so a single source of truth is not currently
possible without a full CCP migration (for the connector) or dropping the "Deploy to Azure"
button flow (for the analytic rule).
