# Cyera DSPM Azure Sentinel Data Connector

| | |
|----------|-------|
| **Connector ID** | `CyeraDSPMCCF` |
| **Publisher** | Cyera Inc |
| **Tables Ingested** | [`CyeraAssets_CL`](../tables-index.md#cyeraassets_cl), [`CyeraAssets_MS_CL`](../tables-index.md#cyeraassets_ms_cl), [`CyeraClassifications_CL`](../tables-index.md#cyeraclassifications_cl), [`CyeraIdentities_CL`](../tables-index.md#cyeraidentities_cl), [`CyeraIssues_CL`](../tables-index.md#cyeraissues_cl) |
| **Used in Solutions** | [CyeraDSPM](../solutions/cyeradspm.md) |
| **Connector Definition Files** | [CyeraDSPMLogs_ConnectorDefinitionCCF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM/Data%20Connectors/CyeraDSPM_CCF/CyeraDSPMLogs_ConnectorDefinitionCCF.json) |

The [Cyera DSPM](https://api.cyera.io/) data connector allows you to connect to your Cyera's DSPM tenant and ingesting Classifications, Assets, Issues, and Identity Resources/Definitions into Microsoft Sentinel. The data connector is built on Microsoft Sentinel's Codeless Connector Framework and uses the Cyera's API to fetch Cyera's [DSPM Telemetry](https://www.cyera.com/) once recieced can be correlated with security events creating custom columns so that queries don't need to parse it again, thus resulting in better performance.

[← Back to Connectors Index](../connectors-index.md)
