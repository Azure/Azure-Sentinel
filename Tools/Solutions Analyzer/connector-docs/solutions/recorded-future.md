# Recorded Future

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Recorded Future Support Team |
| **Support Tier** | Partner |
| **Support Link** | [http://support.recordedfuture.com/](http://support.recordedfuture.com/) |
| **Categories** | domains |
| **First Published** | 2021-11-01 |
| **Last Updated** | 2023-09-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **48 table(s)** from its content items:

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
| [`RecordedFuturePlaybookAlerts_CL`](../tables/recordedfutureplaybookalerts-cl.md) | Playbooks (writes) |
| [`RecordedFuturePortalAlerts_CL`](../tables/recordedfutureportalalerts-cl.md) | Playbooks (writes) |
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

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`RecordedFutureThreatMapMalware_CL`](../tables/recordedfuturethreatmapmalware-cl.md) | Playbooks (writes), Workbooks |
| [`RecordedFutureThreatMap_CL`](../tables/recordedfuturethreatmap-cl.md) | Playbooks (writes), Workbooks |
| [`ThreatIntelIndicators`](../tables/threatintelindicators.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **37 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 21 |
| Workbooks | 8 |
| Analytic Rules | 4 |
| Hunting Queries | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingDomainAllActors.yaml) | Medium | InitialAccess, CommandAndControl | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingHashAllActors.yaml) | Medium | InitialAccess, Execution, Persistence | [`ASimFileEventLogs`](../tables/asimfileeventlogs.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`Event`](../tables/event.md)<br>[`EventParser`](../tables/eventparser.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`StorageBlobLogs`](../tables/storagebloblogs.md)<br>[`StorageFileLogs`](../tables/storagefilelogs.md)<br>[`StorageQueueLogs`](../tables/storagequeuelogs.md)<br>[`StorageTableLogs`](../tables/storagetablelogs.md)<br>[`Syslog`](../tables/syslog.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`WindowsEventParser`](../tables/windowseventparser.md)<br>[`parseddata`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml) | Medium | Exfiltration, CommandAndControl | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFuture Threat Hunting Url All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingUrlAllActors.yaml) | Medium | Persistence, PrivilegeEscalation, DefenseEvasion | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureDomainThreatActorHunt.yaml) | - | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureHashThreatActorHunt.yaml) | - | [`ASimFileEventLogs`](../tables/asimfileeventlogs.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`Event`](../tables/event.md)<br>[`EventParser`](../tables/eventparser.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`StorageBlobLogs`](../tables/storagebloblogs.md)<br>[`StorageFileLogs`](../tables/storagefilelogs.md)<br>[`StorageQueueLogs`](../tables/storagequeuelogs.md)<br>[`StorageTableLogs`](../tables/storagetablelogs.md)<br>[`Syslog`](../tables/syslog.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`WindowsEventParser`](../tables/windowseventparser.md)<br>[`parseddata`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml) | - | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFuture Threat Hunting URL All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureUrlThreatActorHunt.yaml) | - | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [RecordedFutureAlertOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureAlertOverview.json) | - |
| [RecordedFutureDomainCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureDomainCorrelation.json) | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFutureHashCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureHashCorrelation.json) | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFutureIPCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureIPCorrelation.json) | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [RecordedFutureMalwareThreatHunting](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureMalwareThreatHunting.json) | *Internal use:*<br>[`RecordedFutureThreatMapMalware_CL`](../tables/recordedfuturethreatmapmalware-cl.md) |
| [RecordedFuturePlaybookAlertOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFuturePlaybookAlertOverview.json) | - |
| [RecordedFutureThreatActorHunting](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureThreatActorHunting.json) | *Internal use:*<br>[`RecordedFutureThreatMap_CL`](../tables/recordedfuturethreatmap-cl.md) |
| [RecordedFutureURLCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureURLCorrelation.json) | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [RecordedFuture-ActorThreatHunt-IndicatorImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/ThreatHunting/RecordedFuture-ActorThreatHunt-IndicatorImport/azuredeploy.json) | This playbook will write Recorded Future threat hunting indicators to ThreatIntelligenceIndicator lo... | - |
| [RecordedFuture-Alert-Importer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Alerts/RecordedFuture-Alert-Importer/azuredeploy.json) | This playbook imports alerts from Recorded Future and stores them in a custom log in the log analyti... | [`RecordedFuturePortalAlerts_CL`](../tables/recordedfutureportalalerts-cl.md) *(read/write)* |
| [RecordedFuture-DOMAIN-C2_DNS_Name-TIProcessor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Deprecated/RecordedFuture-DOMAIN-C2_DNS_Name-IndicatorProcessor/azuredeploy.json) | **[Deprecated]** Deprecated due to changes in the Threat Intelligence Platform. Use the new Indicato... | - |
| [RecordedFuture-Domain-IndicatorImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/IndicatorImport/RecordedFuture-Domain-IndicatorImport/azuredeploy.json) | This playbook imports Domain risk lists from Recorded Future and stores them as Threat Intelligence ... | - |
| [RecordedFuture-HASH-Obs_in_Underground-TIProcessor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Deprecated/RecordedFuture-HASH-Observed_in_Underground_Virus_Test_Sites-IndicatorProcessor/azuredeploy.json) | **[Deprecated]** Deprecated due to changes in the Threat Intelligence Platform. Use the new Indicato... | - |
| [RecordedFuture-Hash-IndicatorImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/IndicatorImport/RecordedFuture-Hash-IndicatorImport/azuredeploy.json) | This playbook imports Hash risk lists from Recorded Future and stores them as Threat Intelligence In... | - |
| [RecordedFuture-IOC_Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Enrichment/RecordedFuture-IOC_Enrichment/azuredeploy.json) | This playbook leverages the Recorded Future API to enrich IP, Domain, Url & Hash indicators, found i... | - |
| [RecordedFuture-IP-Actively_Comm_C2_Server-TIProcessor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Deprecated/RecordedFuture-IP-Actively_Comm_C2_Server-IndicatorProcessor/azuredeploy.json) | **[Deprecated]** Deprecated due to changes in the Threat Intelligence Platform. Use the new Indicato... | - |
| [RecordedFuture-IP-IndicatorImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/IndicatorImport/RecordedFuture-IP-IndicatorImport/azuredeploy.json) | This playbook imports IP risk lists from Recorded Future and stores them as Threat Intelligence Indi... | - |
| [RecordedFuture-ImportToSentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Deprecated/RecordedFuture-ImportToSentinel/azuredeploy.json) | **[Deprecated]** Deprecated due to changes in the Threat Intelligence Platform. Use the new Indicato... | - |
| [RecordedFuture-MalwareThreatHunt-IndicatorImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/ThreatHunting/RecordedFuture-MalwareThreatHunt-IndicatorImport/azuredeploy.json) | This playbook will write Recorded Future threat hunting indicators to ThreatIntelligenceIndicator lo... | - |
| [RecordedFuture-Playbook-Alert-Importer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Alerts/RecordedFuture-Playbook-Alert-Importer/azuredeploy.json) | This playbook imports alerts from Recorded Future and stores them in a custom log in the log analyti... | [`RecordedFuturePlaybookAlerts_CL`](../tables/recordedfutureplaybookalerts-cl.md) *(write)* |
| [RecordedFuture-Sandbox_Enrichment-Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Sandboxing/RecordedFuture-Sandbox_Enrichment-Url/azuredeploy.json) | This playbook will enrich url entities in an incident and send them to Recorded Future Sandbox. The ... | - |
| [RecordedFuture-Sandbox_Outlook_Attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Sandboxing/RecordedFuture-Sandbox_Outlook_Attachment/azuredeploy.json) | This playbook will trigger on emails with attachmets and send them to Recorded Future Sandbox. The r... | - |
| [RecordedFuture-Sandbox_StorageAccount](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Sandboxing/RecordedFuture-Sandbox_StorageAccount/azuredeploy.json) | This playbook will trigger on files in a Storage Account and send them to Recorded Future Sandbox. T... | - |
| [RecordedFuture-ThreatIntelligenceImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/IndicatorImport/RecordedFuture-ThreatIntelligenceImport/azuredeploy.json) | This playbook will write indicators in batch to ThreatIntelligenceIndicator log analytics table. | - |
| [RecordedFuture-ThreatMap-Importer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/ThreatHunting/RecordedFuture-ThreatMap-Importer/azuredeploy.json) | This playbook will import Threat Map data from Recorded Future and store it in a custom log. | *Internal use:*<br>[`RecordedFutureThreatMap_CL`](../tables/recordedfuturethreatmap-cl.md) *(write)* |
| [RecordedFuture-ThreatMapMalware-Importer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/ThreatHunting/RecordedFuture-ThreatMapMalware-Importer/azuredeploy.json) | This playbook will import Threat Map data from Recorded Future and store it in a custom log. | *Internal use:*<br>[`RecordedFutureThreatMapMalware_CL`](../tables/recordedfuturethreatmapmalware-cl.md) *(write)* |
| [RecordedFuture-URL-IndicatorImport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/IndicatorImport/RecordedFuture-URL-IndicatorImport/azuredeploy.json) | This playbook imports URL risk lists from Recorded Future and stores them as Threat Intelligence Ind... | - |
| [RecordedFuture-URL-Recent_Rep_by_Insikt-TIProcessor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Deprecated/RecordedFuture-URL-Recent_Rep_by_Insikt_Group-IndicatorProcessor/azuredeploy.json) | **[Deprecated]** Deprecated due to changes in the Threat Intelligence Platform. Use the new Indicato... | - |
| [RecordedFuture-Ukraine-IndicatorProcessor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Playbooks/Deprecated/RecordedFuture-Ukraine-IndicatorProcessor/azuredeploy.json) | **[Deprecated]** Deprecated due to changes in the Threat Intelligence Platform. Use the new Indicato... | - |

## Additional Documentation

> 📄 *Source: [Recorded Future/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded Future/README.md)*

[<img alt="Recorded Future" src="Playbooks/Enrichment/RecordedFuture-IOC_Enrichment/images/RecordedFuture.png"  />](https://www.recordedfuture.com/)
# Recorded Future Intelligence for Microsoft Sentinel

Instructions how to install and use Recorded Future Solution for Microsoft Sentinel or how to install individual playbooks can be found in the main [readme.md](Playbooks/readme.md) in the Playbook sub directory in this repository.

Recorded Future also provide standalone Playbooks in this repository for EntraID (identity) and Defender for endpoints.

**Recorded Future Intelligence Solution**
- [Installation guide](Playbooks/readme.md)

**Recorded Future Defender Integrations**
- [Recorded Future Defender playbooks](../../Playbooks/RecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint/)
- [Recorded Future Defender SCF playbooks](../../Playbooks/RecordedFuture_IP_SCF/)

**Recorded Future for Identity**
- [Recorded Future Identity](../Recorded%20Future%20Identity/Playbooks/readme.md)

# About Recorded Future

Recorded Future is the world's largest provider of intelligence for enterprise security. By seamlessly combining automated data collection, pervasive analytics, and expert human analysis, Recorded Future delivers timely, accurate, and actionable intelligence.

**Benefits of Recorded Future integrations** 
- Detect indicators of compromise (IOCs) in your environment.
- Triage alerts faster with elite, real-time intelligence.
- Respond quickly with transparency and context around internal telemetry data.
- Maximize your investment in Microsoft Sentinel.

[Learn more about Recorded Future for Microsoft Sentinel](https://www.recordedfuture.com/microsoft-azure-sentinel-integration)

[Start a 30-day free trial of Recorded Future for Microsoft Sentinel from here!](https://go.recordedfuture.com/microsoft-azure-sentinel-free-trial?utm_campaign=&utm_source=microsoft&utm_medium=gta)

<a id="keyfeatures"></a>
# Key Features
Recorded Future for Microsoft Sentinel offers a range of powerful intelligence capabilities, some of the key features include:
## **IOC Detection (Detect)**

The TI-IndicatorImport playbooks pulls risk lists from Recorded Future and writes the contained indicators to the Microsoft Sentinel ThreatIntelligenceIndicator table via the RecordedFuture-ThreatIntelligenceImport playbook. 
![](Playbooks/Images/2023-04-19-17-08-46.png)\
Microsoft Sentinel analytic rules correlates threat intelligence indicators with logs provided to Microsoft Sentinel and creates alerts/incidents for matches found.\
![](Playbooks/Images/2023-04-19-17-46-32.png)

## **IOC Enrichment (Respond)**

Automation rules triggers on each incident and enriches incidents with Recorded Future intelligence. 
![](Playbooks/Images/2023-04-19-17-46-13.png)

## **Malware Sandbox Analysis (Sandbox)**


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
3.2.17       |  12-08-2025                    | Updated **Indicator imports** with deterministic **STIX ID** that should reduce the number duplicate IOCs. Updated `RecordedFuture-Playbook-Alert-Importer` to improve the description formatting. Updated documentation with typo fixes and clarifications.	|
3.2.16       |  08-05-2025                    | Updated **workbooks**, **analytic rules** and **hunting queries** to new `ThreatIntelIndicators` schema. Removed deprecated **analytic rules**. Updated documentation to reflect changes.	|
| 3.2.15       |  12-03-2025                    | Fixed description of **Playbooks**.	|
| 3.2.14       |  30-01-2025                    | Fix the name of `IntelligenceCloud` parameter in `RecordedFuture-CustomConnector` + other minor renames.	|
| 3.2.13       |  08-01-2025                    | Removed Custom Entity mappings from **Analytic rules**.	|
| 3.2.12       |  28-11-2024                    | Fix API connection bug in RecordedFuture-AlertImporter **Playbook**. |
| 3.2.11       |  31-10-2024                    | Fix API connection bug in RecordedFuture-ThreatMap-Importer **Playbook**, documentation improvements. |
| 3.2.10       |  01-10-2024                    | Updated install README for multiple **Playbooks**, added protocol check for URL enrichments in RecordedFuture-IOC_Enrichment **Playbook**, moved parameters from important to advanced and internal in RecordedFuture-CustomConnector.|
| 3.2.9       |  23-09-2024                    | Updated RecordedFuture-Alert-Importer **Playbook** improved text encoding and added utm links.  |
| 3.2.8       |  23-08-2024                    | Updated RecordedFuture-Alert-Importer **Playbook** added text encoding and latest_event_date bugfix.  |
| 3.2.7       |  01-08-2024                    | Updated **Analytic rules** for entity mappings.  |
| 3.2.6       |  03-08-2024                     | Added incident creation to RecordedFuture-Alert-Importer **Playbook**.<br/> Update concurrency in RecordedFuture-IOC_Enrichment **Playbook**.  |
| 3.2.5       |  24-06-2024                    | Added missing AMA **Data Connector** reference in **Analytic rules**.  |
| 3.2.4       |  08-03-2024                     | Change default Recurrence for pulling data in Fix parse json in RecordedFuture-ThreatMap-Importer **Playbook**.<br/> Update solution description, referencing release notes.  |
| 3.2.3       |  27-02-2024                     | Fix parsing in RecordedFuture-PlaybookAlert-Importer **Playbook**.<br/> Added Recorded Future AI Summary to Alert **workbook**.<br/> Added Statues to **Playbook** alert **Workbook**. |
| 3.2.1       |  08-02-2024                     | Fix parse json in RecordedFuture-Alert-Importer **Playbook**.<br/> Fixed broken links in readme.md |
| 3.2.0       |  27-12-2023                    | Added (Recorded Future Malware Threat Map) **Workbook**<br/> Added (ThreatMapMalware-Importer) **Playbook**.<br/> Added (MalwareThreatHunt-IndicatorImport) **Playbook**.<br/> Fix defaults on RecordedFuture-ActorThreatHunt-IndicatorImport **Playbook** <br/> Fixed description on RecordedFutureThreatHuntingDomainAllActors **Analytic Rules**.<br/> Fixed description on RecordedFutureThreatHuntingHashAllActors **Analytic Rules**. <br/> Added Malware endpoints to RecordedFuture-CustomConnector **Playbook**. <br/> Fixed defaults on Playbook-Alert-Importer **Playbook**.<br/> Updated API connection names for all **Playbooks** to ease API connection configuration. <br>Changed connectorId for Hunting **Analytic Rules**. <br/>Updated documentation. <br/> |
| 3.1.1       |  27-12-2023                    | Minor fix, added Release Notes to Solution description. |
| 3.1.0       |  01-12-2023                    | Added (Recorded Future Threat Actor Map) **Workbook**.<br/> Added (RecordedFuture-ThreatMap-Importer) **Playbook**.<br/> Added (RecordedFuture-ActorThreatHunt-IndicatorImport) **Playbook**.<br/> Added 4 **Analytic Rules** to be used for Recorded Future Threat Hunt. <br/> Documentation update.<br/> Removed 6 deprecated **Playbooks** from Solution package. |
| 3.0.2       | 02-11-2023                     | Encoding Fix to the (RecordedFuture-Alert-Importer) **Playbook**.<br/> Changed defaults in (RecordedFuture-Playbook-Alert-Importer). |
| 3.0.1       | 26-10-2023                     | Fix to the (RecordedFuture-ThreatIntelligenceImport) **Playbook**.  |
| 3.0.0       | 20-09-2023                     | Added **Workbooks** for correlating Recorded Future and logs containing IoC of type IP, DNS, URL and Hash <br/> Generate Markdown/HTML response for enrichment comments.<br/> (Recorded Future Playbook Alerts) **Playbook** and  **Workbook** for visualization.<br/> (Recorded Future Classic Alerts) **Playbook** and **Workbook** for visualization.<br/> Leveraging new API for importing threat indicators and deprecating old **Playbooks**. |
| 2.4.0       | 29-05-2023                     | (Sandbox URL enrichment) **Playbook** included in the solution. <br/> Sandbox( of outlook attachment Playbook) provided as an example outside the solution. <br/> Sandbox of files in Azure storage accounts provided as example outside the solution. <br/> Fix to (IOC enrichment playbook) don’t report 404 (not found) as an error. |
| 2.3.0       | 13-02-2023                     | Layout improvements to the (incident enrichment Playbook). <br/>Added **Detections** from collective insights to enrichment playbooks.<br/>IncidentId and MITRE Att&ck code added to collective insights.<br/>Fix for image in incident comment. |
| 2.2.2       | 23-01-2023                     | Fixes for all risk list import **Playbooks**. |
| 2.2.1       | 23-12-2022                     | Display severity for risk rules in enrichment of IOCs.<br/>Sorting of risk rules, showing very malicious rules first. |
| 2.2.0       | 14-12-2022                     | Improvements to the (incident enrichment playbook).<br/>Added Recorded Future links to enrichment comment.<br/> Improved layout of the enrichment, adding Recorded Future logo, table layout. |
| 2.1.0       | 20-09-2022                     | Updated all **Playbooks** to use RecordedFutureV2 connector, which requires new API keys. <br/>Added **Playbooks** for importing Ukraine Russia conflict risk lists. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
