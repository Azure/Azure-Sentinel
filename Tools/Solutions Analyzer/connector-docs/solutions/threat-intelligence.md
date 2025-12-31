# Threat Intelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence) |

## Data Connectors

This solution provides **5 data connector(s)**:

- [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)
- [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)
- [Threat Intelligence Platforms](../connectors/threatintelligence.md)
- [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)
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
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md), [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md), [Threat Intelligence Platforms](../connectors/threatintelligence.md), [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md), [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md) | Analytics, Hunting, Workbooks |
| [`VMConnection`](../tables/vmconnection.md) | - | Analytics, Hunting |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | - | Analytics |
| [`W3CIISLog`](../tables/w3ciislog.md) | - | Analytics |
| [`WindowsEvent`](../tables/windowsevent.md) | - | Analytics |
| [`WireData`](../tables/wiredata.md) | - | Hunting |
| [`barracuda_CL`](../tables/barracuda-cl.md) | - | Analytics |
| [`meraki_CL`](../tables/meraki-cl.md) | - | Analytics |
| [`parsedData`](../tables/parseddata.md) | - | Analytics |
| [`todynamic`](../tables/todynamic.md) | - | Analytics |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Analytics |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |

## Content Items

This solution includes **58 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 52 |
| Hunting Queries | 5 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Preview - TI map Domain entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_CloudAppEvents.yaml) | Medium | CommandAndControl | [`CloudAppEvents`](../tables/cloudappevents.md)<br>[`Domain_Indicators`](../tables/domain-indicators.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Preview - TI map Email entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_CloudAppEvents.yaml) | Medium | InitialAccess | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Preview - TI map IP entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_CloudAppEvents.yaml) | Medium | CommandAndControl | [`CloudAppEvents`](../tables/cloudappevents.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Preview - TI map URL entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_CloudAppEvents.yaml) | Medium | CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map Domain Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_DeviceNetworkEvents.yaml) | Medium | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) |
| [TI Map IP Entity to Azure SQL Security Audit Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureSQL.yaml) | Medium | CommandAndControl | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map IP Entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureActivity.yaml) | Medium | CommandAndControl | [`AzureActivity`](../tables/azureactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map IP Entity to CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_CustomSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map IP Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DeviceNetworkEvents.yaml) | Medium | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map IP Entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map IP Entity to Duo Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DuoSecurity.yaml) | Medium | CommandAndControl | [`DuoSecurityAuthentication_CL`](../tables/duosecurityauthentication-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map IP Entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_SigninLogs.yaml) | Medium | CommandAndControl | - |
| [TI Map IP Entity to VMConnection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_VMConnection.yaml) | Medium | CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VMConnection`](../tables/vmconnection.md) |
| [TI Map IP Entity to W3CIISLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_W3CIISLog.yaml) | Medium | CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`W3CIISLog`](../tables/w3ciislog.md) |
| [TI Map URL Entity to AuditLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_AuditLogs.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_DeviceNetworkEvents.yaml) | Medium | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) |
| [TI Map URL Entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_EmailUrlInfo.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to OfficeActivity Data [Deprecated]](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_OfficeActivity.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to PaloAlto Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_PaloAlto.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map URL Entity to SecurityAlert Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_SecurityAlerts.yaml) | Medium | CommandAndControl | - |
| [TI Map URL Entity to Syslog Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_Syslog.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map URL Entity to UrlClickEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_UrlClickEvents.yaml) | Medium | CommandAndControl | - |
| [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md) |
| [TI map Domain entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`DnsEvents`](../tables/dnsevents.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Domain entity to EmailEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_EmailEvents.yaml) | Medium | InitialAccess | - |
| [TI map Domain entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_EmailUrlInfo.yaml) | Medium | InitialAccess | [`EmailUrlInfo`](../tables/emailurlinfo.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Domain entity to PaloAlto](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_PaloAlto.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Domain entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_CommonSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Domain entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_SecurityAlert.yaml) | Medium | CommandAndControl | [`Domain_Indicators`](../tables/domain-indicators.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [TI map Domain entity to Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_Syslog.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_imWebSession.yaml) | Medium | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`todynamic`](../tables/todynamic.md) |
| [TI map Email entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_AzureActivity.yaml) | Medium | InitialAccess | [`AzureActivity`](../tables/azureactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Email entity to EmailEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_EmailEvents.yaml) | Medium | InitialAccess | - |
| [TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_OfficeActivity.yaml) | Medium | InitialAccess | [`OfficeActivity`](../tables/officeactivity.md) |
| [TI map Email entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_PaloAlto.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Email entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_SecurityAlert.yaml) | Medium | InitialAccess | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [TI map Email entity to SecurityEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_SecurityEvent.yaml) | Medium | InitialAccess | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map Email entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_SigninLogs.yaml) | Medium | InitialAccess | - |
| [TI map File Hash to CommonSecurityLog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/FileHashEntity_CommonSecurityLog.yaml) | Medium | CommandAndControl | [`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map File Hash to DeviceFileEvents Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/FileHashEntity_DeviceFileEvents.yaml) | Medium | CommandAndControl | [`DeviceFileEvents_`](../tables/devicefileevents-.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map File Hash to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/FileHashEntity_SecurityEvent.yaml) | Medium | CommandAndControl | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to AWSCloudTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AWSCloudTrail.yaml) | Medium | CommandAndControl | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to AppServiceHTTPLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AppServiceHTTPLogs.yaml) | Medium | CommandAndControl | [`AppServiceHTTPLogs`](../tables/appservicehttplogs.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to Azure Key Vault logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureKeyVault.yaml) | Medium | CommandAndControl | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to AzureFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureFirewall.yaml) | Medium | CommandAndControl | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to AzureNetworkAnalytics_CL (NSG Flow Logs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureNetworkAnalytics.yaml) | Medium | CommandAndControl | [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml) | Medium | CommandAndControl | [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`Event`](../tables/event.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md) |
| [TI map IP entity to GitHub_CL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/Threat%20Intel%20Matches%20to%20GitHub%20Audit%20Logs.yaml) | Medium | CommandAndControl | [`GitHubAudit`](../tables/githubaudit.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml) | Medium | CommandAndControl | [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md) |
| [TI map IP entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_OfficeActivity.yaml) | Medium | CommandAndControl | [`IP_Indicators`](../tables/ip-indicators.md) |
| [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imWebSession.yaml) | Medium | CommandAndControl | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [TI map IP entity to Workday(ASimAuditEventLogs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_Workday.yaml) | Medium | CommandAndControl | [`ASimAuditEventLogs`](../tables/asimauditeventlogs.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [TI Map File Entity to OfficeActivity Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_OfficeActivity.yaml) | Impact | [`OfficeActivity`](../tables/officeactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map File Entity to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_SecurityEvent.yaml) | Impact | [`SecurityEvent`](../tables/securityevent.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map File Entity to Syslog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_Syslog.yaml) | Impact | [`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [TI Map File Entity to VMConnection Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_VMConnection.yaml) | Impact | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`VMConnection`](../tables/vmconnection.md) |
| [TI Map File Entity to WireData Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_WireData.yaml) | Impact | [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`WireData`](../tables/wiredata.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ThreatIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Workbooks/ThreatIntelligence.json) | [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>*Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.3       | 19-11-2025                     | Updated **Analytical Rule** to include the missing column. |
| 3.1.2       | 26-06-2025                     | Updated TI Map IP Entity to CommonSecurityLog **Analytical Rules** to exclude private ips |
| 3.1.1       | 22-01-2025                     | Fixed feature flag configs for PMDTI, MDTI, and UploadAPI based on the new FeatureStates. Fix api-version and documentation link for UploadAPI. |
| 3.1.0       | 15-01-2025                     | Updated feature flags for PMDTI and MDTI for GA, and Upload API for PP. |
| 3.0.9		  | 04-12-2024					   | Modified DomainEntity_EmailUrlInfo **Analytic Rule** to resolve memory issues |
| 3.0.8		  | 28-11-2024					   | Removed (Preview) from name for **Data Connectors** Microsoft Defender Threat Intelligence and Premium Microsoft Defender Threat Intelligence, make the MDTI and PMDTI data connctors available in gov solution, and update descriptions of data connectors. |
| 3.0.7		  | 24-10-2024					   | Updated Columns of **Analytical Rules** 				 			  |
| 3.0.6		  | 24-09-2024					   | Updated Entity Mappings of **Analytical Rules** 				 			  |
| 3.0.5       | 19-08-2024                     | Updated isConnectedQuery for **Data Connector** of "Threat Intelligence Upload Indicators API". |
| 3.0.4       | 22-05-2024                     | Updated connectivity criteria for **Data Connector** and added New **Data Connector** for Premium Microsoft Defender Threat Intelligence (Preview)   					  |
| 3.0.3		  | 21-03-2024					   | Updated Entity Mappings of **Analytical Rules**				 			  |
| 3.0.2       | 23-10-2023                     | Updated KQL of analytic rules to improve performance in large datasets 	  |
| 3.0.1       | 22-08-2023                     | Removed (Preview) from Name field in **Analytical Rules** |
| 3.0.0       | 14-08-2023                     | Modified **Analytical Rule** (TI map Domain entity to SecurityAlert). Updated dynamic([1]) to dynamic([1,1]) so as to make result array of array consistent.   |
|             |                                | Updated **Hunting Queries** to have descriptions that meet the 255 characters limit.      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
