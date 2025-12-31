# Feedly

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Feedly Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://feedly.com/i/support/contactUs](https://feedly.com/i/support/contactUs) |
| **Categories** | domains |
| **First Published** | 2023-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Feedly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Feedly) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Feedly](../connectors/feedly.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`feedly_indicators_CL`](../tables/feedly-indicators-cl.md) | [Feedly](../connectors/feedly.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                              |
|-------------|--------------------------------|-----------------------------------------------------------------|
| 3.0.6       | 15-10-2025                     | Fix zip file and remove pandas dependency.    |
| 3.0.5       | 14-10-2025                     | Fix dependencies and default parameters.                                                                                                                                   |
| 3.0.4       | 11-10-2025                     | Migrated to Logs Ingestion API from deprecated HTTP Data Collector API. Now requires DCE, DCR, and Azure AD authentication. See deployment instructions for setup details. |
| 3.0.3       | 28-11-2023                     | Added missing python packages to the  **Data Connector**        |
| 3.0.2       | 10-11-2023                     | Fixed the app service plan                                      | 
| 3.0.1       | 25-10-2023                     | Fixed the runtime of the functionapp for the **Data Connector** | 
| 3.0.0       | 17-08-2023                     | Initial Solution Release 								                                |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
