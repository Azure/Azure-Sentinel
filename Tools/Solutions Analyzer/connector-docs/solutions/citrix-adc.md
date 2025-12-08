# Citrix ADC

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_CitrixADC_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20ADC/Data%20Connectors/Connector_CitrixADC_syslog.json) |

[→ View full connector details](../connectors/citrixadc.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Citrix ADC (former NetScaler)](../connectors/citrixadc.md) |

[← Back to Solutions Index](../solutions-index.md)
