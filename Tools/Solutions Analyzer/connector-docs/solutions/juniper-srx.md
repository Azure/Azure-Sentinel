# Juniper SRX

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Juniper SRX](../connectors/junipersrx.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Juniper SRX](../connectors/junipersrx.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [JuniperSRX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX/Parsers/JuniperSRX.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                               |
|-------------|--------------------------------|--------------------------------------------------|
| 3.0.2       | 18-12-2024                     | Removed Deprecated **Data connector**            |
| 3.0.1       | 19-07-2024                     | Deprecated Data connectors                       | 
| 3.0.0       | 29-08-2023                     | Modified the **Parser** to process Zone Details  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
