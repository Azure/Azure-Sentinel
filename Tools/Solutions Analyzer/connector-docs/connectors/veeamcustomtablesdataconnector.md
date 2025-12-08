# Veeam Data Connector (using Azure Functions)

| | |
|----------|-------|
| **Connector ID** | `VeeamCustomTablesDataConnector` |
| **Publisher** | Veeam |
| **Tables Ingested** | [`VeeamAuthorizationEvents_CL`](../tables-index.md#veeamauthorizationevents_cl), [`VeeamCovewareFindings_CL`](../tables-index.md#veeamcovewarefindings_cl), [`VeeamMalwareEvents_CL`](../tables-index.md#veeammalwareevents_cl), [`VeeamOneTriggeredAlarms_CL`](../tables-index.md#veeamonetriggeredalarms_cl), [`VeeamSecurityComplianceAnalyzer_CL`](../tables-index.md#veeamsecuritycomplianceanalyzer_cl), [`VeeamSessions_CL`](../tables-index.md#veeamsessions_cl) |
| **Used in Solutions** | [Veeam](../solutions/veeam.md) |
| **Connector Definition Files** | [Veeam_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Data%20Connectors/Veeam_API_FunctionApp.json) |

Veeam Data Connector allows you to ingest Veeam telemetry data from multiple custom tables into Microsoft Sentinel.



The connector supports integration with Veeam Backup & Replication, Veeam ONE and Coveware platforms to provide comprehensive monitoring and security analytics. The data is collected through Azure Functions and stored in custom Log Analytics tables with dedicated Data Collection Rules (DCR) and Data Collection Endpoints (DCE).



**Custom Tables Included:**

- **VeeamMalwareEvents_CL**: Malware detection events from Veeam Backup & Replication

- **VeeamSecurityComplianceAnalyzer_CL**: Security & Compliance Analyzer results collected from Veeam backup infrastructure components

- **VeeamAuthorizationEvents_CL**: Authorization and authentication events

- **VeeamOneTriggeredAlarms_CL**: Triggered alarms from Veeam ONE servers

- **VeeamCovewareFindings_CL**: Security findings from Coveware solution

- **VeeamSessions_CL**: Veeam sessions

[← Back to Connectors Index](../connectors-index.md)
