# ThreatConnect

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ThreatConnect, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://threatconnect.com/contact/](https://threatconnect.com/contact/) |
| **Categories** | domains |
| **First Published** | 2023-09-11 |
| **Last Updated** | 2023-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **30 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | Analytics |
| [`AWSVPCFlow`](../tables/awsvpcflow.md) | Analytics |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Analytics |
| [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) | Analytics |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | Analytics |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | Analytics |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Analytics |
| [`Corelight_CL`](../tables/corelight-cl.md) | Analytics |
| [`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md) | Analytics |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | Analytics |
| [`DnsEvents`](../tables/dnsevents.md) | Analytics |
| [`Event`](../tables/event.md) | Analytics |
| [`EventsData`](../tables/eventsdata.md) | Analytics |
| [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md) | Analytics |
| [`NTANetAnalytics`](../tables/ntanetanalytics.md) | Analytics |
| [`OfficeActivity`](../tables/officeactivity.md) | Analytics |
| [`RawNetworkEvents`](../tables/rawnetworkevents.md) | Analytics |
| [`SecurityEvent`](../tables/securityevent.md) | Analytics |
| [`SecurityIoTRawEvent`](../tables/securityiotrawevent.md) | Analytics |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | Analytics |
| [`Syslog`](../tables/syslog.md) | Analytics |
| [`ThreatIntelIndicatorsv2`](../tables/threatintelindicatorsv2.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Analytics |
| [`VMConnection`](../tables/vmconnection.md) | Analytics |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | Analytics |
| [`WindowsEvent`](../tables/windowsevent.md) | Analytics |
| [`aadFunc`](../tables/aadfunc.md) | Analytics |
| [`barracuda_CL`](../tables/barracuda-cl.md) | Analytics |
| [`meraki_CL`](../tables/meraki-cl.md) | Analytics |
| [`parsedData`](../tables/parseddata.md) | Analytics |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Threat Connect TI map Domain entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_DomainEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [ThreatConnect TI Map URL Entity to OfficeActivity Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_URLEntity_OfficeActivity.yaml) | Medium | CommandAndControl | [`OfficeActivity`](../tables/officeactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [ThreatConnect TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_EmailEntity_OfficeActivity.yaml) | Medium | CommandAndControl | [`OfficeActivity`](../tables/officeactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [ThreatConnect TI map Email entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_EmailEntity_SigninLogs.yaml) | Medium | CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`aadFunc`](../tables/aadfunc.md) |
| [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml) | Medium | CommandAndControl | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ThreatConnectOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Workbooks/ThreatConnectOverview.json) | [`ThreatIntelIndicatorsv2`](../tables/threatintelindicatorsv2.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             									|
|-------------|--------------------------------|------------------------------------------------------------------------------------|
| 3.0.1       | 02-07-2025                     | Updated ThreatConnect **Workbook** to ThreatIntelIndicators table references.	   	|
| 3.0.1       | 10-06-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules**   			|
| 3.0.0       | 12-10-2023                     | Initial Solution Release.	                      									|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
