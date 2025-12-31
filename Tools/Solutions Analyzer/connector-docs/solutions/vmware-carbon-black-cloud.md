# VMware Carbon Black Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md)
- [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md)

## Tables Reference

This solution uses **10 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimAuthenticationEventLogs`](../tables/asimauthenticationeventlogs.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |
| [`ASimFileEventLogs`](../tables/asimfileeventlogs.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |
| [`ASimProcessEventLogs`](../tables/asimprocesseventlogs.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |
| [`ASimRegistryEventLogs`](../tables/asimregistryeventlogs.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |
| [`CarbonBlackAuditLogs_CL`](../tables/carbonblackauditlogs-cl.md) | [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md) | - |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md) | Analytics, Workbooks |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | [VMware Carbon Black Cloud](../connectors/vmwarecarbonblack.md) | Analytics |
| [`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |
| [`CarbonBlack_Watchlist_CL`](../tables/carbonblack-watchlist-cl.md) | [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md) | - |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Critical Threat Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Analytic%20Rules/CriticalThreatDetected.yaml) | Medium | LateralMovement | [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) |
| [Known Malware Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Analytic%20Rules/KnownMalwareDetected.yaml) | Medium | Execution | [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [VMwareCarbonBlack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Workbooks/VMwareCarbonBlack.json) | [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Endpoint enrichment - Carbon Black](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Playbooks/CarbonBlack-DeviceEnrichment/azuredeploy.json) | This playbook will collect device information from Carbon Black and post a report on the incident. | - |
| [Endpoint take action from Teams - Carbon Black](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Playbooks/CarbonBlack-TakeDeviceActionFromTeams/azuredeploy.json) | This playbook sends an adaptive card to the SOC Teams channel, lets the analyst decide on action: Qu... | - |
| [Isolate endpoint - Carbon Black](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20Carbon%20Black%20Cloud/Playbooks/CarbonBlack-QuarantineDevice/azuredeploy.json) | This playbook will quarantine the host in Carbon Black. | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                        |
|-------------|--------------------------------|-----------------------------------------------------------|
| 3.0.5       | 22-01-2025                     | Removed Custom Entity mappings from **Analytic rules**	   |
| 3.0.4       | 19-11-2024                     | Modified TransformKQL queries of CCP **Data Connector**   |
| 3.0.3       | 28-10-2024                     | Added Sample Queries to the CCP **Data Connector** template   |
| 3.0.2       | 15-10-2024                     | Added new CCP **Data Connector** to the Solution   |
| 3.0.1       | 17-04-2024                     | Added Azure Deploy button for government portal deployments in **Data connectors**   |
| 3.0.0       | 19-02-2024                     | Alterts API integration done in Carbon Black **Function App**   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
