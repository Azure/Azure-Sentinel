# WithSecureElementsViaFunction

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | WithSecure |
| **Support Tier** | Partner |
| **Support Link** | [https://www.withsecure.com/en/support](https://www.withsecure.com/en/support) |
| **Categories** | domains |
| **First Published** | 2024-02-22 |
| **Last Updated** | 2025-04-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [WithSecure Elements API (Azure Function)](../connectors/withsecureelementsviafunction.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`WsSecurityEvents_CL`](../tables/wssecurityevents-cl.md) | [WithSecure Elements API (Azure Function)](../connectors/withsecureelementsviafunction.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [WithSecureTopComputersByInfections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaFunction/Workbooks/WithSecureTopComputersByInfections.json) | [`WsSecurityEvents_CL`](../tables/wssecurityevents-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| 3.0.2       | 08-05-2025                     | Fix major incident connected to wrong deployment of version 3.0.1                                                            |
| 3.0.1       | 28-03-2025                     | Memory overflow fix - process events via batches<br/>Fix wrong workspace name in sentinel connector installation instruction |
| 3.0.0       | 22-02-2024                     | Initial commit - Data Connector based on Azure Function and "Top computers by infections" Workbook                           |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
