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

This solution provides **1 data connector(s)**.

### [[Deprecated] Citrix ADC (former NetScaler)](../connectors/citrixadc.md)

**Publisher:** Citrix

The [Citrix ADC (former NetScaler)](https://www.citrix.com/products/citrix-adc/) data connector provides the capability to ingest Citrix ADC logs into Microsoft Sentinel. If you want to ingest Citrix WAF logs into Microsoft Sentinel, refer this [documentation](https://learn.microsoft.com/azure/sentinel/data-connectors/citrix-waf-web-app-firewall)

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_CitrixADC_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC/Data%20Connectors/Connector_CitrixADC_syslog.json) |

[→ View full connector details](../connectors/citrixadc.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Citrix ADC (former NetScaler)](../connectors/citrixadc.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 09-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.2       | 30-07-2024                     | Update **Parser** as part of Syslog migration  |
|             |                                | Deprecating data connectors                    |
| 3.0.1       | 18-08-2023                     | Modified the **Parser** with correct watchlist alias|
| 3.0.0       | 14-07-2023                     | Modified the **Data Connector** with improved onboarding instructions \| v 1.0.1
|             |                                | Modified the **Parser** to process the logs coming from Citrix ADC to Syslog table

[← Back to Solutions Index](../solutions-index.md)
