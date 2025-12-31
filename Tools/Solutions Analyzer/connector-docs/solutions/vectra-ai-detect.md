# Vectra AI Detect

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Vectra AI |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2022-05-24 |
| **Last Updated** | 2023-04-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Vectra AI Detect via Legacy Agent](../connectors/aivectradetect.md)
- [[Deprecated] Vectra AI Detect via AMA](../connectors/aivectradetectama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Vectra AI Detect via AMA](../connectors/aivectradetectama.md), [[Deprecated] Vectra AI Detect via Legacy Agent](../connectors/aivectradetect.md) | Analytics, Workbooks |

## Content Items

This solution includes **8 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 7 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Vectra AI Detect - Detections with High Severity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-HighSeverityDetection-by-Tactics.yaml) | High | CredentialAccess, Discovery, LateralMovement, Collection, CommandAndControl, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Vectra AI Detect - New Campaign Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-NewCampaign.yaml) | Medium | LateralMovement, CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Vectra AI Detect - Suspected Compromised Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Account-by-Severity.yaml) | Informational | CredentialAccess, Discovery, LateralMovement, Collection, CommandAndControl, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Vectra AI Detect - Suspected Compromised Host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Host-by-Severity.yaml) | Informational | CredentialAccess, Discovery, LateralMovement, Collection, CommandAndControl, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Vectra AI Detect - Suspicious Behaviors by Category](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Suspected-Behavior-by-Tactics.yaml) | Informational | CredentialAccess, Discovery, LateralMovement, Collection, CommandAndControl, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Vectra Account's Behaviors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Account-Detections.yaml) | Informational | CredentialAccess, Discovery, LateralMovement, Collection, CommandAndControl, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Vectra Host's Behaviors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Host-Detections.yaml) | Informational | CredentialAccess, Discovery, LateralMovement, Collection, CommandAndControl, Exfiltration, Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AIVectraDetectWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Workbooks/AIVectraDetectWorkbook.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.2       | 02-12-2024                     | Removed Deprecated **Data Connectors**                      |
| 3.0.1       | 27-06-2024                     | Deprecating **Data Connectors**                             |
| 3.0.0       | 16-02-2024                     | Addition of new  Vectra AI Detect AMA **Data Connector**    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
