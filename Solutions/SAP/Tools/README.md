# SAP Solution — Tools

This folder contains helper scripts and utilities that support the **agentless SAP data
connector** (SAP Integration Suite / SAPCC connector) and related SAP content in this
solution.

## Contents

| Folder | Description |
|--------|-------------|
| [`IntegrationSuite`](IntegrationSuite/README.md) | PowerShell scripts to connect Microsoft Sentinel to SAP Integration Suite runtime instances, creating Sentinel connections from destinations defined in a CSV file. Also includes the [audit log smoke test guide](IntegrationSuite/AUDIT-LOG-SMOKE-TEST.md). |
| [`TimeSliceBackfill`](TimeSliceBackfill/README.md) | PowerShell REST client that loads selected historic time slices through the SAP Integration Suite iFlow. Use it for initial loads, or to fill gaps after intermittent failures or log pipeline downtime. The connector itself starts at *now*. Includes sizing guidance to avoid overloading SAP Integration Suite, SAP Cloud Connector and SAP ERP. |
| [`LogExtractorStatistics`](LogExtractorStatistics/README.md) | ABAP script example to estimate key SAP log sizes (application log, change document, security audit log) between selected dates, to help with sizing/capacity planning. |

## Analyze SAP ingestion volume and peaks

See [SAP ingestion analysis and exclusion candidates](TimeSliceBackfill/README.md#sap-ingestion-analysis-and-exclusion-candidates)
for seven copyable KQL queries covering truncation events, daily volume, average daily
and projected monthly volume, hourly peaks, highest-volume accounts, user exclusion
impact, and a per-minute threshold chart. This guidance is independent of backfill;
no script execution is needed. Review security coverage before excluding accounts.

## Troubleshooting

If SAP Security Audit Log data (`ABAPAuditLog`) is missing or delayed in Microsoft
Sentinel, see the [Audit Log Smoke Test](IntegrationSuite/AUDIT-LOG-SMOKE-TEST.md) guide
under `IntegrationSuite` for manual steps to validate the audit log RFC on the SAP
backend before raising a support ticket with Microsoft and/or SAP.

To reload windows that were missed after the root cause is fixed, use
[`TimeSliceBackfill`](TimeSliceBackfill/README.md).
