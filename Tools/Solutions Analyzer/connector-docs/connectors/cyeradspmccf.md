# Cyera DSPM Microsoft Sentinel Data Connector

| | |
|----------|-------|
| **Connector ID** | `CyeraDSPMCCF` |
| **Publisher** | Cyera Inc |
| **Used in Solutions** | [CyeraDSPM](../solutions/cyeradspm.md) |
| **Connector Definition Files** | [CyeraDSPMLogs_ConnectorDefinitionCCF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM/Data%20Connectors/CyeraDSPM_CCF/CyeraDSPMLogs_ConnectorDefinitionCCF.json) |

The [Cyera DSPM](https://api.cyera.io/) data connector allows you to connect to your Cyera's DSPM tenant and ingesting Classifications, Assets, Issues, and Identity Resources/Definitions into Microsoft Sentinel. The data connector is built on Microsoft Sentinel's Codeless Connector Framework and uses the Cyera's API to fetch Cyera's [DSPM Telemetry](https://www.cyera.com/) once received can be correlated with security events creating custom columns so that queries don't need to parse it again, thus resulting in better performance.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`CyeraAssets_CL`](../tables/cyeraassets-cl.md) | — | — |
| [`CyeraAssets_MS_CL`](../tables/cyeraassets-ms-cl.md) | — | — |
| [`CyeraClassifications_CL`](../tables/cyeraclassifications-cl.md) | — | — |
| [`CyeraIdentities_CL`](../tables/cyeraidentities-cl.md) | — | — |
| [`CyeraIssues_CL`](../tables/cyeraissues-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Cyera DSPM Authentication**

Connect to your Cyera DSPM tenenant via Personal Access Tokens
- **Cyera Personal Access Token Client ID**: client_id
- **Cyera Personal Access Token Secret Key**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
