# Azure Web Application Firewall (WAF)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Web Application Firewall (WAF)](../connectors/waf.md)

**Publisher:** Microsoft

Connect to the Azure Web Application Firewall (WAF) for Application Gateway, Front Door, or CDN. This WAF protects your applications from common web vulnerabilities such as SQL injection and cross-site scripting, and lets you customize rules to reduce false positives. Follow these instructions to stream your Microsoft Web application firewall logs into Microsoft Sentinel. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223546&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [template_WAF.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Data%20Connectors/template_WAF.JSON) |

[→ View full connector details](../connectors/waf.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Web Application Firewall (WAF)](../connectors/waf.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.2       | 06-02-2025                     | Extracting transactionId_g and hostname_s from the AdditionalFields column using parse_json and Removing the now unavailable details_message_s and details_data_s fields from **Analytic Rules** App Gateway WAF - SQLi Detection and App Gateway WAF - XSS Detection.|
| 3.0.1       | 10-06-2024                     | Added new **Analytic Rules** [App Gateway WAF - SQLi Detection and App Gateway WAF - XSS Detection]    |  
| 3.0.0       | 21-12-2023                     | Added ResourceProvide condition as it is standard for Application Gateway WAF logs  |

[← Back to Solutions Index](../solutions-index.md)
