# Forcepoint DLP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-05-09 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forcepoint DLP](../connectors/forcepoint-dlp.md)

**Publisher:** Forcepoint

The Forcepoint DLP (Data Loss Prevention) connector allows you to automatically export DLP incident data from Forcepoint DLP into Microsoft Sentinel in real-time. This enriches visibility into user activities and data loss incidents, enables further correlation with data from Azure workloads and other feeds, and improves monitoring capability with Workbooks inside Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `ForcepointDLPEvents_CL` |
| **Connector Definition Files** | [Forcepoint%20DLP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20DLP/Data%20Connectors/Forcepoint%20DLP.json) |

[→ View full connector details](../connectors/forcepoint-dlp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ForcepointDLPEvents_CL` | [Forcepoint DLP](../connectors/forcepoint-dlp.md) |

[← Back to Solutions Index](../solutions-index.md)
