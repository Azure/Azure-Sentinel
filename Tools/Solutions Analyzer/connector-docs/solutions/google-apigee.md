# Google Apigee

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Google ApigeeX](../connectors/apigeexdataconnector.md)
- [Google ApigeeX (via Codeless Connector Framework)](../connectors/googleapigeexlogsccpdefinition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ApigeeX_CL`](../tables/apigeex-cl.md) | [[DEPRECATED] Google ApigeeX](../connectors/apigeexdataconnector.md) | - |
| [`GCPApigee`](../tables/gcpapigee.md) | [Google ApigeeX (via Codeless Connector Framework)](../connectors/googleapigeexlogsccpdefinition.md) | - |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 3 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ApigeeX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee/Parsers/ApigeeX.yaml) | - | - |
| [ApigeeXV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee/Parsers/ApigeeXV2.yaml) | - | - |
| [Unified_ApigeeX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Apigee/Parsers/Unified_ApigeeX.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.1       | 20-08-2025                     | Moving Google Apigee **CCF Data Connector** to GA					 |
| 3.1.0       | 20-05-2025                     | Migrated the Function app connector to **CCF Data Connector** and Updated the **Parser** |
| 3.1.0       | 28-02-2025                     | Added new CCP **Data Connector** to the Solution                                 |
| 3.0.0       | 05-09-2024                     | Updated the python runtime version to 3.11 in **Data Connector** Function APP    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
