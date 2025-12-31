# Zscaler Internet Access

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Zscaler |
| **Support Tier** | Partner |
| **Support Link** | [https://help.zscaler.com/submit-ticket-links](https://help.zscaler.com/submit-ticket-links) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Zscaler via Legacy Agent](../connectors/zscaler.md)
- [[Deprecated] Zscaler via AMA](../connectors/zscalerama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Zscaler via AMA](../connectors/zscalerama.md), [[Deprecated] Zscaler via Legacy Agent](../connectors/zscaler.md) | Analytics, Workbooks |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 4 |
| Playbooks | 4 |
| Analytic Rules | 2 |
| Parsers | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Discord CDN Risky File Download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Analytic%20Rules/DiscordCDNRiskyDownload.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Request for single resource on domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Analytic%20Rules/Zscaler-LowVolumeDomainRequests.yaml) | Low | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ZscalerFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerFirewall.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ZscalerOffice365Apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerOffice365Apps.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ZscalerThreats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerThreats.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [ZscalerWebOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerWebOverview.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block URL - Zscaler](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Playbooks/Add-Url-To-Category/azuredeploy.json) | This playbook allows blocks URLs in Zscaler by adding them to categories | - |
| [FileHash Enrichment - Zscaler](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Playbooks/Get-Sandbox-Report-For-Hash/azuredeploy.json) | This playbook post a Zscaler Sandbox report for each FileHash found in the incident. | - |
| [FunctionApp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Playbooks/Zscaler%20API%20authentication/FunctionApp/azuredeploy.json) | - | - |
| [Zscaler API authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Playbooks/Zscaler%20API%20authentication/azuredeploy.json) | This playbook generates access token in Zscaler API. Call this playbook as a step in functional Zsca... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ZScalerFW_Parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Parsers/ZScalerFW_Parser.yaml) | - | - |
| [ZScalerWeb_Parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Parsers/ZScalerWeb_Parser.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.3       | 28-11-2024                     | Removed Deprecated **Data Connectors**         |
| 3.0.2       | 28-06-2024                     | Deprecating data connectors                    |
| 3.0.1       | 03-05-2024                     | Repackaged for parser issue fix on reinstall   |
| 3.0.0       | 16-02-2024                     | Addition of new Zscaler AMA **Data Connector** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
