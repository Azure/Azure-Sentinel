# Lookout Cloud Security Platform for Microsoft Sentinel

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Lookout |
| **Support Tier** | Partner |
| **Support Link** | [https://www.lookout.com/support](https://www.lookout.com/support) |
| **Categories** | domains |
| **First Published** | 2023-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Lookout Cloud Security for Microsoft Sentinel

**Publisher:** Lookout

This connector uses a Agari REST API connection to push data into Microsoft Sentinel Log Analytics.

**Tables Ingested:**

- `LookoutCloudSecurity_CL`

**Connector Definition Files:**

- [LookoutCloudSecurityConnector_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout%20Cloud%20Security%20Platform%20for%20Microsoft%20Sentinel/Data%20Connectors/LookoutCSConnector/LookoutCloudSecurityConnector_API_FunctionApp.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `LookoutCloudSecurity_CL` | Lookout Cloud Security for Microsoft Sentinel |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n