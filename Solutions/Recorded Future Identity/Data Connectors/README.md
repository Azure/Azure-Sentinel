# Data Connectors

## Files

### `RFI_AlertImporter_ConnectorDefinition.json`
GenericUI connector definition for the **Recorded Future Identity - Playbook Alert Importer** tile.
Listed in `Data/Solution_RecordedFutureIdentity.json` and baked into `Package/mainTemplate.json`
by the packaging tool. This is what makes the connector appear in the Sentinel Data Connectors
gallery after a Content Hub / solution install.

### `azuredeploy-alert-importer.json`
Standalone ARM template that deploys the full infrastructure stack for the **Playbook Alert Importer** (PBA-based) solution:
- Data Collection Endpoint (DCE) — `recorded-future-identity-dce`
- Data Collection Rule (DCR) — `recorded-future-identity-dcr-playbook-alerts`
- Log Analytics custom table (`RFI_PlaybookAlertResults_V2_CL`)
- Connector definition tile (see duplication note below)

Used by the "Deploy to Azure" button in the Playbooks README and in the connector's instruction steps.
Deploy this before deploying the PBA playbook.

### `azuredeploy-v3.json`
Standalone ARM template that deploys the full infrastructure stack for the **v3.0 Identity API** (legacy) solution:
- Data Collection Endpoint (DCE) — `recorded-future-identity-dce` (same resource as above — see sync note below)
- Three Data Collection Rules (DCRs):
  - `recorded-future-identity-v3-dcr-lookup-results`
  - `recorded-future-identity-v3-dcr-malware-logs`
  - `recorded-future-identity-v3-dcr-credential-dumps`
- Three Log Analytics custom tables: `RFI_UsersLookupResults_V2_CL`, `RFI_MalwareLogs_V2_CL`, `RFI_CredentialDumps_V2_CL`

Used by the "Deploy to Azure" button in `Playbooks/v3.0/readme.md`.
Deploy this before deploying the v3.0 playbooks.

### `azuredeploy-incident-creation-analytic-rule.json`
Standalone ARM template equivalent of
`Analytic Rules/IncidentCreation/RecordedFutureIdentityExposure.yaml`.
Exists solely to support the "Deploy to Azure" button flow for users who prefer not to
create the rule manually via the Sentinel UI. See duplication note below.

## Known duplication

### DCE shared between `azuredeploy-alert-importer.json` and `azuredeploy-v3.json`

Both templates deploy a DCE named `recorded-future-identity-dce`. When deployed to the same
resource group, the second deployment updates the existing DCE in place (ARM is idempotent).
Any change to DCE properties (e.g. `networkAcls`, API version) **must be applied to both files**.

### Connector tile and analytic rule

Two pieces of content exist in two forms due to limitations of the packaging/deployment model:

| Content | Packager source | Standalone ARM |
|---|---|---|
| Connector UI tile | `RFI_AlertImporter_ConnectorDefinition.json` | `azuredeploy-alert-importer.json` |
| Analytic rule | `../Analytic Rules/IncidentCreation/RecordedFutureIdentityExposure.yaml` | `azuredeploy-incident-creation-analytic-rule.json` |

If you update either, update its counterpart. The Content Hub packaging format and standalone
ARM deployments require different file shapes, so a single source of truth is not currently
possible without a full CCP migration (for the connector) or dropping the "Deploy to Azure"
button flow (for the analytic rule).
