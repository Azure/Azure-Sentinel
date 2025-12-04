# Veeam

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Veeam Software |
| **Support Tier** | Partner |
| **Support Link** | [https://helpcenter.veeam.com/docs/security_plugins_microsoft_sentinel/guide/](https://helpcenter.veeam.com/docs/security_plugins_microsoft_sentinel/guide/) |
| **Categories** | domains |
| **Version** | 3.0.2 |
| **First Published** | 2025-08-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md)

**Publisher:** Veeam

Veeam Data Connector allows you to ingest Veeam telemetry data from multiple custom tables into Microsoft Sentinel.



The connector supports integration with Veeam Backup & Replication, Veeam ONE and Coveware platforms to provide comprehensive monitoring and security analytics. The data is collected through Azure Functions and stored in custom Log Analytics tables with dedicated Data Collection Rules (DCR) and Data Collection Endpoints (DCE).



**Custom Tables Included:**

- **VeeamMalwareEvents_CL**: Malware detection events from Veeam Backup & Replication

- **VeeamSecurityComplianceAnalyzer_CL**: Security & Compliance Analyzer results collected from Veeam backup infrastructure components

- **VeeamAuthorizationEvents_CL**: Authorization and authentication events

- **VeeamOneTriggeredAlarms_CL**: Triggered alarms from Veeam ONE servers

- **VeeamCovewareFindings_CL**: Security findings from Coveware solution

- **VeeamSessions_CL**: Veeam sessions

| | |
|--------------------------|---|
| **Tables Ingested** | `VeeamAuthorizationEvents_CL` |
| | `VeeamCovewareFindings_CL` |
| | `VeeamMalwareEvents_CL` |
| | `VeeamOneTriggeredAlarms_CL` |
| | `VeeamSecurityComplianceAnalyzer_CL` |
| | `VeeamSessions_CL` |
| **Connector Definition Files** | [Veeam_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Data%20Connectors/Veeam_API_FunctionApp.json) |

[→ View full connector details](../connectors/veeamcustomtablesdataconnector.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `VeeamAuthorizationEvents_CL` | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) |
| `VeeamCovewareFindings_CL` | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) |
| `VeeamMalwareEvents_CL` | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) |
| `VeeamOneTriggeredAlarms_CL` | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) |
| `VeeamSecurityComplianceAnalyzer_CL` | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) |
| `VeeamSessions_CL` | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
