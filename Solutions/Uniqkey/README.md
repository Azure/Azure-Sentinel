# Uniqkey Solution for Microsoft Sentinel

This solution ingests security and audit events from the Uniqkey business password management platform into Microsoft Sentinel using the Codeless Connector Framework (CCF).

## Contents

| Component | Path | Purpose |
|-----------|------|---------|
| Connector definition | `Data Connectors/UniqkeyAuditLogs_ccf/Uniqkey_ConnectorDefinition.json` | Connector page UI in the Sentinel portal |
| Poller config | `Data Connectors/UniqkeyAuditLogs_ccf/Uniqkey_PollerConfig.json` | REST API polling (bearer auth, cursor paging, time windows) |
| Data collection rule | `Data Connectors/UniqkeyAuditLogs_ccf/Uniqkey_DCR.json` | Raw event to `UniqkeyEvents_CL` schema transformation |
| Table schema | `Data Connectors/UniqkeyAuditLogs_ccf/Uniqkey_Table.json` | Custom table `UniqkeyEvents_CL` |
| Packaging manifest | `Data/Solution_Uniqkey.json` | Input for the V3 packaging tool |
| Analytic rules | `Analytic Rules/*.yaml` | 9 scheduled detections (anomalous sign-in, export/exfiltration patterns, insider privilege escalation, policy changes, platform threat detections, ingestion health) |
| Workbook | `Workbooks/Uniqkey.json` | Uniqkey Security Events dashboard (volume, sign-in map, client systems, top users, exports, threat detections) |

## Open items before PR submission

- [x] **API endpoint**: the poller points at the production endpoint `https://siem-integration.production.uniqkey.eu`.
- [x] **Logo**: `Logos/Uniqkey.svg` added and embedded in the connector definition.
- [x] **Instruction steps**: token generation path (Settings > Integrations > SIEM) documented in the connector definition.
- [x] **SolutionMetadata publisherId**: `publisherId: "uniqkey"` matches the Commercial Marketplace publisher ID registered in Partner Center. Support email confirmed as support@uniqkey.eu.
- [ ] **ASIM**: obtain the official EventVendor/EventProduct designation from Microsoft and add an `ASimAuthentication` parser under `Parsers/`.
- [x] **Analytic rule action names**: the rules "Departing employee credential export" and "Credential export from newly created account" filter on the exact action-type GUIDs from the Uniqkey audit-log catalog (Const.cs, verified 25-08-2026), with a name-based fallback. Re-verify against live sample data during the test deployment, including that the account_management event's target employee id matches the exporting actor's id.
- [ ] **Workbook preview images**: `Workbooks/Images/Preview/UniqkeyEvents{Black,White}.png` at the repository root are generated placeholders. Replace them with real screenshots (dark and light theme) of the deployed workbook.
- [ ] **Content**: consider adding Hunting Queries to raise solution quality further (see https://aka.ms/SentinelSolutionQuality). Note: failed sign-ins are not audited by Uniqkey, so do not build authentication-failure detections on `Outcome`.

## Build & validate

```powershell
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "Uniqkey"
```
