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

This solution provides **1 data connector(s)**:

- [Azure Web Application Firewall (WAF)](../connectors/waf.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AGWAccessLogs`](../tables/agwaccesslogs.md) | - | Analytics |
| [`AGWFirewallLogs`](../tables/agwfirewalllogs.md) | - | Analytics |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [Azure Web Application Firewall (WAF)](../connectors/waf.md) | Analytics, Workbooks |
| [`FakeData`](../tables/fakedata.md) | - | Workbooks |

## Content Items

This solution includes **14 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Workbooks | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [A potentially malicious web request was executed against a web server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/MaliciousWAFSessions.yaml) | Medium | InitialAccess | [`AGWAccessLogs`](../tables/agwaccesslogs.md)<br>[`AGWFirewallLogs`](../tables/agwfirewalllogs.md) |
| [AFD WAF - Code Injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-WAF-Code-Injection.yaml) | High | DefenseEvasion, Execution, InitialAccess, PrivilegeEscalation | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [AFD WAF - Path Traversal Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-WAF-Path-Traversal-Attack.yaml) | High | DefenseEvasion, Execution, InitialAccess, PrivilegeEscalation, Discovery | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [App GW WAF - Code Injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/App-GW-WAF-Code-Injection.yaml) | High | DefenseEvasion, Execution, InitialAccess, PrivilegeEscalation | [`AGWFirewallLogs`](../tables/agwfirewalllogs.md) |
| [App GW WAF - Path Traversal Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/App-GW-WAF-Path-Traversal-Attack.yaml) | High | DefenseEvasion, Execution, InitialAccess, PrivilegeEscalation, Discovery | [`AGWFirewallLogs`](../tables/agwfirewalllogs.md) |
| [App Gateway WAF - SQLi Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/App-GW-WAF-SQLiDetection.yaml) | High | DefenseEvasion, Execution, InitialAccess, PrivilegeEscalation | [`AGWFirewallLogs`](../tables/agwfirewalllogs.md) |
| [App Gateway WAF - Scanner Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/App-GW-WAF-Scanner-detection.yaml) | High | DefenseEvasion, Execution, InitialAccess, Reconnaissance, Discovery | [`AGWFirewallLogs`](../tables/agwfirewalllogs.md) |
| [App Gateway WAF - XSS Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/App-GW-WAF-XSSDetection.yaml) | High | InitialAccess, Execution | [`AGWFirewallLogs`](../tables/agwfirewalllogs.md) |
| [Front Door Premium WAF - SQLi Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-Premium-WAF-SQLiDetection.yaml) | High | DefenseEvasion, Execution, InitialAccess, PrivilegeEscalation | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Front Door Premium WAF - XSS Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-Premium-WAF-XSSDetection.yaml) | High | InitialAccess, Execution | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [WebApplicationFirewallFirewallEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallFirewallEvents.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [WebApplicationFirewallGatewayAccessEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallGatewayAccessEvents.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [WebApplicationFirewallOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallOverview.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [WebApplicationFirewallWAFTypeEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallWAFTypeEvents.json) | [`FakeData`](../tables/fakedata.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.2       | 06-02-2025                     | Extracting transactionId_g and hostname_s from the AdditionalFields column using parse_json and Removing the now unavailable details_message_s and details_data_s fields from **Analytic Rules** App Gateway WAF - SQLi Detection and App Gateway WAF - XSS Detection.|
| 3.0.1       | 10-06-2024                     | Added new **Analytic Rules** [App Gateway WAF - SQLi Detection and App Gateway WAF - XSS Detection]    |  
| 3.0.0       | 21-12-2023                     | Added ResourceProvide condition as it is standard for Application Gateway WAF logs  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
