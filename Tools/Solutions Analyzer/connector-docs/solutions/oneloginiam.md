# OneLoginIAM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md)
- [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`OneLoginEventsV2_CL`](../tables/onelogineventsv2-cl.md) | [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md), [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md) | - |
| [`OneLoginUsersV2_CL`](../tables/oneloginusersv2-cl.md) | [OneLogin IAM Platform (via Codeless Connector Framework)](../connectors/oneloginiamlogsccpdefinition.md), [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md) | - |
| [`OneLogin_CL`](../tables/onelogin-cl.md) | [[DEPRECATED] OneLogin IAM Platform](../connectors/onelogin.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [OneLogin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneLoginIAM/Parsers/OneLogin.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 29-07-2025                     |  Removed Deprecated **Data Connector**. | 
| 3.0.2       | 30-06-2025                     |  OneLoginIAM **CCF Data Connector** moving to GA.  		                |
| 3.0.1       | 10-04-2025                     |  Migrated the **Function app** connector to **CCF Data Connector** and Updated **Parser**.<br/>Added Preview tag to **CCF Data Connector**.   		                |
| 3.0.0       | 25-09-2023                     |  Modified **Parser** for query optimization. 		                |
|             |                                |  Manual deployment instructions updated for **Data Connector**.     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
