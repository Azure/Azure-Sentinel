# Azure Web Application Firewall (WAF)

## Solution Information

| | |
|------------------------|-------|
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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Azure WAF to Microsoft Sentinel**

Go to each WAF resource type and choose your WAF.
- **Configure Web Application Firewall**
- **Configure Azure Front Door**
- **Configure CDN Profile**

Inside your WAF resource:

1.  Select **Diagnostic logs.​**
2.  Select **+ Add diagnostic setting.​**
3.  In the **Diagnostic setting** blade:
    -   Type a **Name**.
    -   Select **Send to Log Analytics**.
    -   Choose the log destination workspace.​
    -   Select the categories that you want to analyze (recommended: ApplicationGatewayAccessLog, ApplicationGatewayFirewallLog, FrontdoorAccessLog, FrontdoorWebApplicationFirewallLog, WebApplicationFirewallLogs).​
    -   Click **Save**.

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [template_WAF.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Data%20Connectors/template_WAF.JSON) |

[→ View full connector details](../connectors/waf.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Web Application Firewall (WAF)](../connectors/waf.md) |

[← Back to Solutions Index](../solutions-index.md)
