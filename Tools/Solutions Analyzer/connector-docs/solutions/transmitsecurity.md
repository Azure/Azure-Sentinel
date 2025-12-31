# TransmitSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Transmit Security |
| **Support Tier** | Partner |
| **Support Link** | [https://transmitsecurity.com/support](https://transmitsecurity.com/support) |
| **Categories** | domains |
| **First Published** | 2024-06-10 |
| **Last Updated** | 2024-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/TransmitSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Transmit Security Connector](../connectors/transmitsecurity.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`TransmitSecurityActivity_CL`](../tables/transmitsecurityactivity-cl.md) | [Transmit Security Connector](../connectors/transmitsecurity.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** |                 **Change History**                  |
|-------------|--------------------------------|-----------------------------------------------------|
| 3.0.2       | 20-11-2024                     | Change Functions to support one endpoint at a time  | 
| 3.0.1       | 03-09-2024                     | Updated the python runtime version to 3.11          |
| 3.0.0       | 11-07-2024                     | Initial Solution Release                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
