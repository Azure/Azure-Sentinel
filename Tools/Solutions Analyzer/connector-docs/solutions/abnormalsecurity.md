# AbnormalSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Abnormal Security |
| **Support Tier** | Partner |
| **Support Link** | [https://abnormalsecurity.com/contact](https://abnormalsecurity.com/contact) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbnormalSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbnormalSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [AbnormalSecurity ](../connectors/abnormalsecurity.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ABNORMAL_CASES_CL`](../tables/abnormal-cases-cl.md) | [AbnormalSecurity ](../connectors/abnormalsecurity.md) | - |
| [`ABNORMAL_THREAT_MESSAGES_CL`](../tables/abnormal-threat-messages-cl.md) | [AbnormalSecurity ](../connectors/abnormalsecurity.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.0.0       | 29-06-2023                     | Renaming Azure Function to Azure Functions in **Data Connector** Description and  Updated the python runtime version to 3.11      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
