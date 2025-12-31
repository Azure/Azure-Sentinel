# Threat Intelligence (NEW)

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-04-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29) |

## Data Connectors

This solution provides **6 data connector(s)**:

- [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)
- [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)
- [Threat Intelligence Platforms](../connectors/threatintelligence.md)
- [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)
- [Threat intelligence - TAXII Export (Preview)](../connectors/threatintelligencetaxiiexport.md)
- [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md)

## Tables Reference

This solution uses **52 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimAuditEventLogs`](../tables/asimauditeventlogs.md) | - | Analytics |
| [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md) | - | Analytics |
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | - | Analytics |
| [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) | - | Analytics |
| [`AWSCloudTrail`](../tables/awscloudtrail.md) | - | Analytics |
| [`AWSVPCFlow`](../tables/awsvpcflow.md) | - | Analytics |
| [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) | - | Analytics |
| [`AZFWDnsQuery`](../tables/azfwdnsquery.md) | - | Analytics |
| [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md) | - | Workbooks |
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | - | Analytics |
| [`AppServiceHTTPLogs`](../tables/appservicehttplogs.md) | - | Analytics |
| [`AzureActivity`](../tables/azureactivity.md) | - | Analytics |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | - | Analytics |
| [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) | - | Analytics |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | - | Analytics |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | - | Analytics |
| [`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md) | - | Analytics |
| [`CloudAppEvents`](../tables/cloudappevents.md) | - | Analytics |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [Threat Intelligence Platforms](../connectors/threatintelligence.md) | Analytics |
| [`Corelight_CL`](../tables/corelight-cl.md) | - | Analytics |
| [`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md) | - | Analytics |
| [`DeviceFileEvents_`](../tables/devicefileevents-.md) | - | Analytics |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | - | Analytics |
| [`DnsEvents`](../tables/dnsevents.md) | - | Analytics |
| [`Domain_Indicators`](../tables/domain-indicators.md) | - | Analytics |
| [`DuoSecurityAuthentication_CL`](../tables/duosecurityauthentication-cl.md) | - | Analytics |
| [`EmailUrlInfo`](../tables/emailurlinfo.md) | - | Analytics |
| [`Event`](../tables/event.md) | - | Analytics |
| [`EventsData`](../tables/eventsdata.md) | - | Analytics |
| [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) | - | Analytics |
| [`GitHubAudit`](../tables/githubaudit.md) | - | Analytics |
| [`IP_Indicators`](../tables/ip-indicators.md) | - | Analytics |
| [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md) | - | Analytics |
| [`NTANetAnalytics`](../tables/ntanetanalytics.md) | - | Analytics |
| [`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md) | - | Analytics |
| [`OfficeActivity`](../tables/officeactivity.md) | - | Analytics, Hunting |
| [`RawNetworkEvents`](../tables/rawnetworkevents.md) | - | Analytics |
| [`SecurityEvent`](../tables/securityevent.md) | - | Analytics, Hunting |
| [`SecurityIoTRawEvent`](../tables/securityiotrawevent.md) | - | Analytics |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | - | Analytics |
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | - | Analytics |
| [`Syslog`](../tables/syslog.md) | - | Analytics, Hunting |
| [`ThreatIntelExportOperation`](../tables/threatintelexportoperation.md) | [Threat intelligence - TAXII Export (Preview)](../connectors/threatintelligencetaxiiexport.md) | - |
| [`ThreatIntelObjects`](../tables/threatintelobjects.md) | [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md), [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md), [Threat Intelligence Platforms](../connectors/threatintelligence.md), [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md), [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md) | - |
| [`VMConnection`](../tables/vmconnection.md) | - | Analytics, Hunting |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | - | Analytics |
| [`W3CIISLog`](../tables/w3ciislog.md) | - | Analytics |
| [`WindowsEvent`](../tables/windowsevent.md) | - | Analytics |
| [`barracuda_CL`](../tables/barracuda-cl.md) | - | Analytics |
| [`meraki_CL`](../tables/meraki-cl.md) | - | Analytics |
| [`parsedData`](../tables/parseddata.md) | - | Analytics |
| [`todynamic`](../tables/todynamic.md) | - | Analytics |

### Internal Tables

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Analytics |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |
| [`ThreatIntelIndicators`](../tables/threatintelindicators.md) | [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md), [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md), [Threat Intelligence Platforms](../connectors/threatintelligence.md), [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md), [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **58 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 51 |
| Hunting Queries | 5 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [TI Map Domain Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_DeviceNetworkEvents_Updated.yaml) | Medium | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) |
| [TI Map IP Entity to Azure SQL Security Audit Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureSQL.yaml) | Medium | CommandAndControl | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureActivity.yaml) | Medium | CommandAndControl | [`AzureActivity`](../tables/azureactivity.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_CustomSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DeviceNetworkEvents_Updated.yaml) | Medium | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to Duo Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DuoSecurity.yaml) | Medium | CommandAndControl | [`DuoSecurityAuthentication_CL`](../tables/duosecurityauthentication-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_SigninLogs_Updated.yaml) | Medium | CommandAndControl | - |
| [TI Map IP Entity to VMConnection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_VMConnection.yaml) | Medium | CommandAndControl | [`VMConnection`](../tables/vmconnection.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map IP Entity to W3CIISLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_W3CIISLog.yaml) | Medium | CommandAndControl | [`W3CIISLog`](../tables/w3ciislog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map URL Entity to AuditLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_AuditLogs.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_DeviceNetworkEvents_Updated.yaml) | Medium | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) |
| [TI Map URL Entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_EmailUrlInfo_Updated.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to PaloAlto Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_PaloAlto.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map URL Entity to SecurityAlert Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_SecurityAlerts.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to Syslog Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_Syslog.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map URL Entity to UrlClickEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_UrlClickEvents_Updated.yaml) | Medium | CommandAndControl | - |
| [TI map Domain entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_CloudAppEvents_Updated.yaml) | Medium | CommandAndControl | [`CloudAppEvents`](../tables/cloudappevents.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to EmailEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_EmailEvents_Updated.yaml) | Medium | InitialAccess | - |
| [TI map Domain entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_EmailUrlInfo_Updated.yaml) | Medium | InitialAccess | [`EmailUrlInfo`](../tables/emailurlinfo.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to PaloAlto](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_PaloAlto.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_CommonSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_SecurityAlert.yaml) | Medium | CommandAndControl | [`Domain_Indicators`](../tables/domain-indicators.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [TI map Domain entity to Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_Syslog.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_imWebSession.yaml) | Medium | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`todynamic`](../tables/todynamic.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Email entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_AzureActivity.yaml) | Medium | InitialAccess | [`AzureActivity`](../tables/azureactivity.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Email entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_CloudAppEvents_Updated.yaml) | Medium | InitialAccess | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Email entity to EmailEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_EmailEvents_Updated.yaml) | Medium | InitialAccess | - |
| [TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_OfficeActivity.yaml) | Medium | InitialAccess | [`OfficeActivity`](../tables/officeactivity.md) |
| [TI map Email entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_PaloAlto.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Email entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_SecurityAlert.yaml) | Medium | InitialAccess | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Email entity to SecurityEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_SecurityEvent.yaml) | Medium | InitialAccess | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map Email entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_SigninLogs.yaml) | Medium | InitialAccess | - |
| [TI map File Hash to CommonSecurityLog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/FileHashEntity_CommonSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map File Hash to DeviceFileEvents Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/FileHashEntity_DeviceFileEvents_Updated.yaml) | Medium | CommandAndControl | [`DeviceFileEvents_`](../tables/devicefileevents-.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map File Hash to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/FileHashEntity_SecurityEvent.yaml) | Medium | CommandAndControl | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to AWSCloudTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AWSCloudTrail.yaml) | Medium | CommandAndControl | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to AppServiceHTTPLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AppServiceHTTPLogs.yaml) | Medium | CommandAndControl | [`AppServiceHTTPLogs`](../tables/appservicehttplogs.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to Azure Key Vault logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureKeyVault.yaml) | Medium | CommandAndControl | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to AzureFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureFirewall.yaml) | Medium | CommandAndControl | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to AzureNetworkAnalytics_CL (NSG Flow Logs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureNetworkAnalytics.yaml) | Medium | CommandAndControl | [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_CloudAppEvents_Updated.yaml) | Medium | CommandAndControl | [`CloudAppEvents`](../tables/cloudappevents.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to GitHub_CL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/Threat%20Intel%20Matches%20to%20GitHub%20Audit%20Logs.yaml) | Medium | CommandAndControl | [`GitHubAudit`](../tables/githubaudit.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml) | Medium | CommandAndControl | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_OfficeActivity.yaml) | Medium | CommandAndControl | [`IP_Indicators`](../tables/ip-indicators.md) |
| [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imWebSession.yaml) | Medium | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map IP entity to Workday(ASimAuditEventLogs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_Workday_Updated.yaml) | Medium | CommandAndControl | [`ASimAuditEventLogs`](../tables/asimauditeventlogs.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI map URL entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_CloudAppEvents_Updated.yaml) | Medium | CommandAndControl | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [TI Map File Entity to OfficeActivity Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_OfficeActivity.yaml) | Impact | [`OfficeActivity`](../tables/officeactivity.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map File Entity to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_SecurityEvent.yaml) | Impact | [`SecurityEvent`](../tables/securityevent.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map File Entity to Syslog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_Syslog.yaml) | Impact | [`Syslog`](../tables/syslog.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map File Entity to VMConnection Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_VMConnection.yaml) | Impact | [`VMConnection`](../tables/vmconnection.md)<br>*Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |
| [TI Map File Entity to WireData Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_WireData.yaml) | Impact | *Internal use:*<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ThreatIntelligenceNew](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Workbooks/ThreatIntelligenceNew.json) | [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md)<br>*Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md)<br>[`ThreatIntelIndicators`](../tables/threatintelindicators.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ThreatIntelIndicatorsv2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Parsers/ThreatIntelIndicatorsv2.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.12      | 23-12-2025                     | Replaces the 'AlertPriority' field with 'Severity' in the IPEntity_AppServiceHTTPLogs analytic rule and updates all related references.            |
| 3.0.11      | 02-12-2025                     | Update Threat Intelligence package and release notes 	 |
| 3.0.10      | 20-11-2025                     | Update Syntax for IPEntity_CloudAppEvents_Updated.yaml Rule		 |
| 3.0.9       | 07-11-2025                     | Updated EmailEntity_CloudAppEvents_Updated.yaml to adjust lookback periods to match the query period and frequency. |
| 3.0.8       | 18-10-2025                     | Update IPEntity_AzureFirewall.yaml to use Resource specific tables rather than AzureDiagnostics |
| 3.0.7       | 16-10-2025                     | Added new connector for **Threat Intelligence TAXII** export and now available in public preview.				|
| 3.0.6       | 08-09-2025                     | Fixed the problem related to the **Workbook** query					 |
| 3.0.5       | 03-09-2025                     | Support for a new data type, `ThreatIntelObjects`, across multiple Threat Intelligence **Data Connector** templates					 |
| 3.0.4       | 08-08-2025                     | Updated **Data Connectors** and **Analytic Rules** to ensures consistency and likely aligns with updated connector schemas or naming conventions|
| 3.0.3       | 25-07-2025                     | Added several new **Data Connectors** for Microsoft Sentinel, aimed at enhancing threat intelligence integration capabilities|
| 3.0.2       | 10-07-2025                     | Improve kql query efficiency and accuracy|
| 3.0.1       | 17-04-2025                     | Updated entity mappings of **Analytic Rules**|
| 3.0.0       | 02-04-2025                     | Initial solution release					 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
