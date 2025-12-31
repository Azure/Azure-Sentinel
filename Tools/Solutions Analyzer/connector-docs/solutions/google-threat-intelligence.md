# Google Threat Intelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Google |
| **Support Tier** | Partner |
| **Support Link** | [https://www.virustotal.com/gui/contact-us](https://www.virustotal.com/gui/contact-us) |
| **Categories** | domains |
| **First Published** | 2024-10-26 |
| **Last Updated** | 2024-10-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **46 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md) | Analytics, Hunting |
| [`ASimFileEventLogs`](../tables/asimfileeventlogs.md) | Analytics, Hunting |
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | Analytics, Hunting |
| [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) | Analytics, Hunting |
| [`AWSVPCFlow`](../tables/awsvpcflow.md) | Analytics, Hunting |
| [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) | Analytics, Hunting |
| [`AZFWDnsQuery`](../tables/azfwdnsquery.md) | Analytics, Hunting |
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | Analytics, Hunting |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Analytics, Hunting |
| [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) | Analytics, Hunting |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | Analytics, Hunting |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | Analytics, Hunting |
| [`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md) | Analytics, Hunting |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Analytics, Hunting |
| [`Corelight_CL`](../tables/corelight-cl.md) | Analytics, Hunting |
| [`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md) | Analytics, Hunting |
| [`DeviceFileEvents`](../tables/devicefileevents.md) | Analytics, Hunting |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | Analytics, Hunting |
| [`DnsEvents`](../tables/dnsevents.md) | Analytics, Hunting |
| [`Event`](../tables/event.md) | Analytics, Hunting |
| [`EventParser`](../tables/eventparser.md) | Analytics, Hunting |
| [`EventsData`](../tables/eventsdata.md) | Analytics, Hunting |
| [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) | Analytics, Hunting |
| [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md) | Analytics, Hunting |
| [`NTANetAnalytics`](../tables/ntanetanalytics.md) | Analytics, Hunting |
| [`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md) | Analytics, Hunting |
| [`OfficeActivity`](../tables/officeactivity.md) | Analytics, Hunting |
| [`RawNetworkEvents`](../tables/rawnetworkevents.md) | Analytics, Hunting |
| [`SecurityEvent`](../tables/securityevent.md) | Analytics, Hunting |
| [`SecurityIoTRawEvent`](../tables/securityiotrawevent.md) | Analytics, Hunting |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | Analytics, Hunting |
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | Analytics, Hunting |
| [`StorageBlobLogs`](../tables/storagebloblogs.md) | Analytics, Hunting |
| [`StorageFileLogs`](../tables/storagefilelogs.md) | Analytics, Hunting |
| [`StorageQueueLogs`](../tables/storagequeuelogs.md) | Analytics, Hunting |
| [`StorageTableLogs`](../tables/storagetablelogs.md) | Analytics, Hunting |
| [`Syslog`](../tables/syslog.md) | Analytics, Hunting |
| [`VMConnection`](../tables/vmconnection.md) | Analytics, Hunting |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | Analytics, Hunting |
| [`W3CIISLog`](../tables/w3ciislog.md) | Analytics, Hunting |
| [`WindowsEvent`](../tables/windowsevent.md) | Analytics, Hunting |
| [`WindowsEventParser`](../tables/windowseventparser.md) | Analytics, Hunting |
| [`barracuda_CL`](../tables/barracuda-cl.md) | Analytics, Hunting |
| [`meraki_CL`](../tables/meraki-cl.md) | Analytics, Hunting |
| [`parsedData`](../tables/parseddata.md) | Analytics, Hunting |
| [`parseddata`](../tables/parseddata.md) | Analytics, Hunting |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`ThreatIntelIndicators`](../tables/threatintelindicators.md) | Analytics, Hunting |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 8 |
| Analytic Rules | 4 |
| Hunting Queries | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntDomain.yaml) | Medium | CommandAndControl | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntHash.yaml) | Medium | Execution | [`ASimFileEventLogs`](../tables/asimfileeventlogs.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`Event`](../tables/event.md)<br>[`EventParser`](../tables/eventparser.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`StorageBlobLogs`](../tables/storagebloblogs.md)<br>[`StorageFileLogs`](../tables/storagefilelogs.md)<br>[`StorageQueueLogs`](../tables/storagequeuelogs.md)<br>[`StorageTableLogs`](../tables/storagetablelogs.md)<br>[`Syslog`](../tables/syslog.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`WindowsEventParser`](../tables/windowseventparser.md)<br>[`parseddata`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml) | Medium | CommandAndControl | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntUrl.yaml) | Medium | InitialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntDomain.yaml) | - | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntHash.yaml) | - | [`ASimFileEventLogs`](../tables/asimfileeventlogs.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`Event`](../tables/event.md)<br>[`EventParser`](../tables/eventparser.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`StorageBlobLogs`](../tables/storagebloblogs.md)<br>[`StorageFileLogs`](../tables/storagefilelogs.md)<br>[`StorageQueueLogs`](../tables/storagequeuelogs.md)<br>[`StorageTableLogs`](../tables/storagetablelogs.md)<br>[`Syslog`](../tables/syslog.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`WindowsEventParser`](../tables/windowseventparser.md)<br>[`parseddata`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml) | - | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntUrl.yaml) | - | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Google Threat Intelligence - Domain Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIEnrichment/GTI-EnrichEntity/GTI-EnrichDomain/azuredeploy.json) | This playbook will enrich Domain entities. | - |
| [Google Threat Intelligence - FileHash Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIEnrichment/GTI-EnrichEntity/GTI-EnrichFilehash/azuredeploy.json) | This playbook will enrich FileHash entities. | - |
| [Google Threat Intelligence - IOC Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIEnrichment/GTI-EnrichAlert/azuredeploy.json) | This playbook will enrich IP, Hash, URL & Domain entities found in alerts. | - |
| [Google Threat Intelligence - IOC Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIEnrichment/GTI-EnrichIncident/azuredeploy.json) | This playbook will enrich IP, Hash, URL & Domain entities found in incidents. | - |
| [Google Threat Intelligence - IP Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIEnrichment/GTI-EnrichEntity/GTI-EnrichIP/azuredeploy.json) | This playbook will enrich IP entities. | - |
| [Google Threat Intelligence - IoC Stream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIIocStream/azuredeploy.json) | This playbook will ingest Google Threat Intelligence from your IoC Streams into Threat Intelligence ... | - |
| [Google Threat Intelligence - Threat List](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIThreatList/azuredeploy.json) | This playbook will ingest Google Threat Intelligence into Threat Intelligence Sentinel. | - |
| [Google Threat Intelligence - URL Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Playbooks/GTIEnrichment/GTI-EnrichEntity/GTI-EnrichURL/azuredeploy.json) | This playbook will enrich URL entities. | - |

## Additional Documentation

> 📄 *Source: [Google Threat Intelligence/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google Threat Intelligence/README.md)*

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/GoogleThreatIntelligence.svg" alt="Google Threat Intelligence" style="width:150px; height:150px"/>

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.2.2       | 02-12-2025                     | - Included new Analytics Rules and Hunting Queries to improve detection capabilities and support proactive investigation. <br/>- Filtering threat lists<br/>- Migrating to Upload STIX Objects |
| 3.2.1       | 25-08-2025                     | Fix IoC Stream ingestion bug for results with more than 40 items due to a cursor iteration error. |
| 3.2.0       | 20-05-2025                     | New **Playbook** added *IoC Stream Threat Intelligence*.<br/> Added x-tool header in **Playbook** Customer Connector. |
| 3.1.0       | 29-01-2025                     | New *Threat Intelligence Ingestion* **Playbook** added. |
| 3.0.0       | 05-12-2024                     | Initial Solution Release.                       |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
