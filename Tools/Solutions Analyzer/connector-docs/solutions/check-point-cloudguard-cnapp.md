# Check Point CloudGuard CNAPP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Check Point |
| **Support Tier** | Partner |
| **Support Link** | [https://www.checkpoint.com/support-services/contact-support/](https://www.checkpoint.com/support-services/contact-support/) |
| **Categories** | domains |
| **First Published** | 2024-11-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20CloudGuard%20CNAPP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20CloudGuard%20CNAPP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Check Point CloudGuard CNAPP Connector for Microsoft Sentinel](../connectors/cloudguardccpdefinition.md)

**Publisher:** CheckPoint

The [CloudGuard](https://sc1.checkpoint.com/documents/CloudGuard_Dome9/Documentation/Overview/CloudGuard-CSPM-Introduction.htm?cshid=help_center_documentation) data connector enables the ingestion of security events from the CloudGuard API into Microsoft Sentinel™, using Microsoft Sentinel’s Codeless Connector Platform. The connector supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) which parses incoming security event data into custom columns. This pre-parsing process eliminates the need for query-time parsing, resulting in improved performance for data queries.

| | |
|--------------------------|---|
| **Tables Ingested** | `CloudGuard_SecurityEvents_CL` |
| **Connector Definition Files** | [CloudGuard_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point%20CloudGuard%20CNAPP/Data%20Connectors/CloudGuard_ccp/CloudGuard_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cloudguardccpdefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CloudGuard_SecurityEvents_CL` | [Check Point CloudGuard CNAPP Connector for Microsoft Sentinel](../connectors/cloudguardccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
