# SOC Handbook

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/Azure/Azure-Sentinel/issues](https://github.com/Azure/Azure-Sentinel/issues) |
| **Categories** | domains |
| **First Published** | 2022-11-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **19 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`DeviceEvents`](../tables/deviceevents.md) | Workbooks |
| [`DnsEvents`](../tables/dnsevents.md) | Workbooks |
| [`HuntingBookmark`](../tables/huntingbookmark.md) | Workbooks |
| [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) | Workbooks |
| [`LogonEvents`](../tables/logonevents.md) | Workbooks |
| [`MITRE_DEF_TABLE`](../tables/mitre-def-table.md) | Workbooks |
| [`MSFTBuiltinAlerts`](../tables/msftbuiltinalerts.md) | Workbooks |
| [`Network_MetaParser`](../tables/network-metaparser.md) | Workbooks |
| [`ProcessCreationEvents`](../tables/processcreationevents.md) | Workbooks |
| [`ProtectionStatus`](../tables/protectionstatus.md) | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | Workbooks |
| [`SentinelGithub`](../tables/sentinelgithub.md) | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Workbooks |
| [`Usage`](../tables/usage.md) | Workbooks |
| [`alertEntity`](../tables/alertentity.md) | Workbooks |
| [`getAmountOfIncedentForRuleId`](../tables/getamountofincedentforruleid.md) | Workbooks |
| [`getAmountOfIncidentForRuleId`](../tables/getamountofincidentforruleid.md) | Workbooks |
| [`uniqueIncidentIdList`](../tables/uniqueincidentidlist.md) | Workbooks |

### Internal Tables

The following **4 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`Anomalies`](../tables/anomalies.md) | Workbooks |
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **13 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 13 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AnalyticsEfficiency](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AnalyticsEfficiency.json) | [`MITRE_DEF_TABLE`](../tables/mitre-def-table.md)<br>[`getAmountOfIncedentForRuleId`](../tables/getamountofincedentforruleid.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [AnomaliesVisualization](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AnomaliesVisualization.json) | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [AnomalyData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AnomalyData.json) | [`uniqueIncidentIdList`](../tables/uniqueincidentidlist.md)<br>*Internal use:*<br>[`Anomalies`](../tables/anomalies.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [AttackSurfaceReduction](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AttackSurfaceReduction.json) | [`DeviceEvents`](../tables/deviceevents.md) |
| [AzureSentinelCost](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AzureSentinelCost.json) | [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md)<br>[`Usage`](../tables/usage.md) |
| [AzureSentinelSecurityAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AzureSentinelSecurityAlerts.json) | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [IncidentOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/IncidentOverview.json) | [`getAmountOfIncidentForRuleId`](../tables/getamountofincidentforruleid.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [IntsightsIOCWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/IntsightsIOCWorkbook.json) | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`alertEntity`](../tables/alertentity.md) |
| [InvestigationInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json) | [`DnsEvents`](../tables/dnsevents.md)<br>[`HuntingBookmark`](../tables/huntingbookmark.md)<br>[`LogonEvents`](../tables/logonevents.md)<br>[`Network_MetaParser`](../tables/network-metaparser.md)<br>[`ProcessCreationEvents`](../tables/processcreationevents.md)<br>[`ProtectionStatus`](../tables/protectionstatus.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [MITREAttack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/MITREAttack.json) | [`MSFTBuiltinAlerts`](../tables/msftbuiltinalerts.md)<br>[`SentinelGithub`](../tables/sentinelgithub.md)<br>[`Usage`](../tables/usage.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [SecurityOperationsEfficiency](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/SecurityOperationsEfficiency.json) | *Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md) |
| [SecurityStatus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/SecurityStatus.json) | [`SecurityEvent`](../tables/securityevent.md) |
| [SentinelCentral](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/SentinelCentral.json) | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                  |
|-------------|--------------------------------|-------------------------------------------------------------------------------------|
| 3.0.5       | 24-09-2025                     | Updated *SecurityOperationsEfficiency* to fix Mean time to triage |
| 3.0.4       | 22-04-2025                     | Updated *Azure to Sentinel Cost* - **Workbook**.            |
| 3.0.3       | 28-11-2023                     | Changes for rebranding from Azure Active Directory to Microsoft Entra ID.            |
| 3.0.2       | 21-11-2023                     | Updated SecurityOperationsEfficiency **Workbook** to run the query on "set in query".|
| 3.0.1       | 14-07-2023                     | Updated **Workbook** to correctly get the drop down for Subscription and Workspace.  |
| 3.0.0       | 07-07-2023                     | Initial Solution Release.                                                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
