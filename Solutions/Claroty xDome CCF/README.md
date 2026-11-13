# Claroty xDome CCF Solution

This solution ingests Claroty xDome data into Microsoft Sentinel by using the Codeless Connector Framework (CCF) pull model.

## What this solution includes

- One CCF data connector
- Seven dedicated Log Analytics tables
- Parsers
- Workbook
- Analytic rules
- Hunting queries
- Sample data

## Data types and tables

| Data type | API endpoint | Table |
|---|---|---|
| Alerts | /api/v1/alerts/ | ClarotyXDomeAlert_CL |
| Device-Alert relations | /api/v1/device_alert_relations/ | ClarotyXDomeDeviceAlert_CL |
| OT Activity Events | /api/v1/ot_activity_events/ | ClarotyXDomeOTEvent_CL |
| Vulnerabilities | /api/v1/vulnerabilities/ | ClarotyXDomeVulnerability_CL |
| Device-Vulnerability relations | /api/v1/device_vulnerability_relations/ | ClarotyXDomeDeviceVulnerability_CL |
| Devices | /api/v1/devices/ | ClarotyXDomeDevice_CL |
| Audit Log | /api/v1/audit_log/get | ClarotyXDomeAuditLog_CL |

## Deploy to Azure

Use the Microsoft Learn Deploy to Azure button format:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FClaroty%2520xDome%2520CCF%2FPackage%2FmainTemplate.json)

Direct file links:

- mainTemplate (Azure-Sentinel master): [https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Claroty%20xDome%20CCF/Package/mainTemplate.json](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Claroty%20xDome%20CCF/Package/mainTemplate.json)
- createUiDefinition (Azure-Sentinel master): [https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Claroty%20xDome%20CCF/Package/createUiDefinition.json](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Claroty%20xDome%20CCF/Package/createUiDefinition.json)

## Connect in Sentinel

1. Open Microsoft Sentinel.
2. Go to Configuration, then Data connectors.
3. Open Claroty xDome CCF.
4. Add a connection with:
   - Connection Name
   - API Root URL (for example, https://<region>.api.claroty.com)
   - API Token
   - Data types to ingest
   - Optional filters and polling windows

## Quick validation queries

```kusto
ClarotyXDomeAlert_CL | take 20
ClarotyXDomeOTEvent_CL | summarize count() by EventType
ClarotyXDomeVulnerability_CL | where IsKnownExploited == true | sort by CvssV3Score desc
ClarotyXDomeDevice_CL | summarize arg_max(TimeGenerated, *) by DeviceUid
ClarotyXDomeAuditLog_CL | where Action == 'User Logged In'
```
