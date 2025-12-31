# Microsoft Defender For Identity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-04-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20For%20Identity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20For%20Identity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Defender for Identity](../connectors/azureadvancedthreatprotection.md)

## Tables Reference

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft Defender for Identity](../connectors/azureadvancedthreatprotection.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.0       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
