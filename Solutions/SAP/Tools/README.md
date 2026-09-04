# SAP Solution — Tools

This folder contains helper scripts and utilities that support the **agentless SAP data
connector** (SAP Integration Suite / SAPCC connector) and related SAP content in this
solution.

## Contents

| Folder | Description |
|--------|-------------|
| [`IntegrationSuite`](IntegrationSuite/README.md) | PowerShell scripts to connect Microsoft Sentinel to SAP Integration Suite runtime instances, creating Sentinel connections from destinations defined in a CSV file. Also includes the [audit log smoke test guide](IntegrationSuite/AUDIT-LOG-SMOKE-TEST.md). |
| [`LogExtractorStatistics`](LogExtractorStatistics/README.md) | ABAP script example to estimate key SAP log sizes (application log, change document, security audit log) between selected dates, to help with sizing/capacity planning. |

## Troubleshooting

If SAP Security Audit Log data (`ABAPAuditLog`) is missing or delayed in Microsoft
Sentinel, see the [Audit Log Smoke Test](IntegrationSuite/AUDIT-LOG-SMOKE-TEST.md) guide
under `IntegrationSuite` for manual steps to validate the audit log RFC on the SAP
backend before raising a support ticket with Microsoft and/or SAP.
