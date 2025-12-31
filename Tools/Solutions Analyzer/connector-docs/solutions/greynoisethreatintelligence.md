# GreyNoiseThreatIntelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | GreyNoise |
| **Support Tier** | Partner |
| **Support Link** | [https://www.greynoise.io/contact/general](https://www.greynoise.io/contact/general) |
| **Categories** | domains |
| **First Published** | 2023-09-05 |
| **Last Updated** | 2025-07-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [GreyNoise Threat Intelligence](../connectors/greynoise2sentinelapi.md)

## Tables Reference

This solution uses **30 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | - | Analytics |
| [`AWSVPCFlow`](../tables/awsvpcflow.md) | - | Analytics |
| [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md) | - | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | - | Analytics |
| [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) | - | Analytics |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | - | Analytics |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | - | Analytics |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | - | Analytics |
| [`Corelight_CL`](../tables/corelight-cl.md) | - | Analytics |
| [`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md) | - | Analytics |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | - | Analytics |
| [`DnsEvents`](../tables/dnsevents.md) | - | Analytics |
| [`Event`](../tables/event.md) | - | Analytics |
| [`EventsData`](../tables/eventsdata.md) | - | Analytics |
| [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md) | - | Analytics |
| [`NTANetAnalytics`](../tables/ntanetanalytics.md) | - | Analytics |
| [`OfficeActivity`](../tables/officeactivity.md) | - | Analytics |
| [`RawNetworkEvents`](../tables/rawnetworkevents.md) | - | Analytics |
| [`SecurityEvent`](../tables/securityevent.md) | - | Analytics |
| [`SecurityIoTRawEvent`](../tables/securityiotrawevent.md) | - | Analytics |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | - | Analytics |
| [`Syslog`](../tables/syslog.md) | - | Analytics |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | [GreyNoise Threat Intelligence](../connectors/greynoise2sentinelapi.md) | Analytics, Workbooks |
| [`VMConnection`](../tables/vmconnection.md) | - | Analytics |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | - | Analytics |
| [`WindowsEvent`](../tables/windowsevent.md) | - | Analytics |
| [`aadFunc`](../tables/aadfunc.md) | - | Analytics |
| [`barracuda_CL`](../tables/barracuda-cl.md) | - | Analytics |
| [`meraki_CL`](../tables/meraki-cl.md) | - | Analytics |
| [`parsedData`](../tables/parseddata.md) | - | Analytics |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [GreyNoise TI Map IP Entity to CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_CustomSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [GreyNoise TI Map IP Entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [GreyNoise TI Map IP Entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_SigninLogs.yaml) | Medium | CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`aadFunc`](../tables/aadfunc.md) |
| [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml) | Medium | CommandAndControl | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md) |
| [GreyNoise TI map IP entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_OfficeActivity.yaml) | Medium | CommandAndControl | [`OfficeActivity`](../tables/officeactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [GreyNoiseOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Workbooks/GreyNoiseOverview.json) | [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3      | 17-07-2025                     | Updated to use GreyNoise Python SDK v3.0.1, use new Threat Intel API, updated requirements.txt, updated Data Connector instructions |
| 3.0.2       | 30-05-2024                     | Added missing AMA **Data Connector** reference in **Analytic rules**  |
| 3.0.1       | 29-11-2023                     | Updated the **Data Connector** Instructions, Fixed a Data Connector bug with Benign Indicator Ingest|
| 3.0.0       | 21-09-2023                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
