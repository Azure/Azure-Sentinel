# Citrix ADC

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Citrix ADC (former NetScaler)](../connectors/citrixadc.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Citrix ADC (former NetScaler)](../connectors/citrixadc.md) | - |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 2 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CitrixADCEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC/Parsers/CitrixADCEvent.yaml) | - | - |
| [CitrixADCEventOld](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC/Parsers/CitrixADCEventOld.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 09-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.2       | 30-07-2024                     | Update **Parser** as part of Syslog migration  |
|             |                                | Deprecating data connectors                    |
| 3.0.1       | 18-08-2023                     | Modified the **Parser** with correct watchlist alias|
| 3.0.0       | 14-07-2023                     | Modified the **Data Connector** with improved onboarding instructions \| v 1.0.1
|             |                                | Modified the **Parser** to process the logs coming from Citrix ADC to Syslog table

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
