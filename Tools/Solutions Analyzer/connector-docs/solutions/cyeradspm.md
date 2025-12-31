# CyeraDSPM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cyera Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cyera.io](https://support.cyera.io) |
| **Categories** | domains |
| **First Published** | 2025-10-15 |
| **Last Updated** | 2025-10-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyeraDSPM) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md)
- [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyeraAssets_CL`](../tables/cyeraassets-cl.md) | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) | - |
| [`CyeraAssets_MS_CL`](../tables/cyeraassets-ms-cl.md) | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) | - |
| [`CyeraClassifications_CL`](../tables/cyeraclassifications-cl.md) | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) | - |
| [`CyeraIdentities_CL`](../tables/cyeraidentities-cl.md) | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) | - |
| [`CyeraIssues_CL`](../tables/cyeraissues-cl.md) | [Cyera DSPM Azure Functions Microsoft Sentinel Data Connector](../connectors/cyerafunctionsconnector.md), [Cyera DSPM Microsoft Sentinel Data Connector](../connectors/cyeradspmccf.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                    |
|-------------|--------------------------------|-------------------------------------------------------|
| 3.0.0       | 29-10-2025                     | Initial Creation of CCF and Azure Functions Connector |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
