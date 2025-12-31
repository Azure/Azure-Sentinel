# ThreatIntelIndicators

Reference for ThreatIntelIndicators table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Internal |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/threatintelindicators) |

## Solutions (5)

This table is used by the following solutions:

- [DORA Compliance](../solutions/dora-compliance.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [Recorded Future](../solutions/recorded-future.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

## Connectors (6)

This table is ingested by the following connectors:

- [Lumen Defender Threat Feed Data Connector](../connectors/lumenthreatfeedconnector.md)
- [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)
- [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)
- [Threat Intelligence Platforms](../connectors/threatintelligence.md)
- [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)
- [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md)

---

## Content Items Using This Table (74)

### Analytic Rules (54)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntDomain.yaml)
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntHash.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)
- [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntUrl.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress in CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_CommonSecurityLog.yaml)
- [Lumen TI IPAddress in DeviceEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_DeviceEvents.yaml)
- [Lumen TI IPAddress in IdentityLogonEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_IdentityLogonEvents.yaml)
- [Lumen TI IPAddress in OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_OfficeActivity.yaml)
- [Lumen TI IPAddress in SecurityEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_SecurityEvent.yaml)
- [Lumen TI IPAddress in SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_SigninLogs.yaml)
- [Lumen TI IPAddress in WindowsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_WindowsEvents.yaml)
- [Lumen TI domain in DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_DomainEntity_DNS.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingDomainAllActors.yaml)
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingHashAllActors.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml)
- [RecordedFuture Threat Hunting Url All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingUrlAllActors.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map IP Entity to Azure SQL Security Audit Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureSQL.yaml)
- [TI Map IP Entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureActivity.yaml)
- [TI Map IP Entity to CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_CustomSecurityLog.yaml)
- [TI Map IP Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DeviceNetworkEvents_Updated.yaml)
- [TI Map IP Entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DnsEvents.yaml)
- [TI Map IP Entity to Duo Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DuoSecurity.yaml)
- [TI Map IP Entity to VMConnection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_VMConnection.yaml)
- [TI Map IP Entity to W3CIISLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_W3CIISLog.yaml)
- [TI Map URL Entity to PaloAlto Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_PaloAlto.yaml)
- [TI Map URL Entity to Syslog Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_Syslog.yaml)
- [TI map Domain entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_CloudAppEvents_Updated.yaml)
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map Domain entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_DnsEvents.yaml)
- [TI map Domain entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_EmailUrlInfo_Updated.yaml)
- [TI map Domain entity to PaloAlto](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_PaloAlto.yaml)
- [TI map Domain entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_CommonSecurityLog.yaml)
- [TI map Domain entity to Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_Syslog.yaml)
- [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_imWebSession.yaml)
- [TI map Email entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_AzureActivity.yaml)
- [TI map Email entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_CloudAppEvents_Updated.yaml)
- [TI map Email entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_PaloAlto.yaml)
- [TI map Email entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_SecurityAlert.yaml)
- [TI map Email entity to SecurityEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_SecurityEvent.yaml)
- [TI map File Hash to CommonSecurityLog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/FileHashEntity_CommonSecurityLog.yaml)
- [TI map File Hash to DeviceFileEvents Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/FileHashEntity_DeviceFileEvents_Updated.yaml)
- [TI map File Hash to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/FileHashEntity_SecurityEvent.yaml)
- [TI map IP entity to AWSCloudTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AWSCloudTrail.yaml)
- [TI map IP entity to AppServiceHTTPLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AppServiceHTTPLogs.yaml)
- [TI map IP entity to Azure Key Vault logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureKeyVault.yaml)
- [TI map IP entity to AzureFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureFirewall.yaml)
- [TI map IP entity to AzureNetworkAnalytics_CL (NSG Flow Logs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureNetworkAnalytics.yaml)
- [TI map IP entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_CloudAppEvents_Updated.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)
- [TI map IP entity to GitHub_CL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/Threat%20Intel%20Matches%20to%20GitHub%20Audit%20Logs.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)
- [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imWebSession.yaml)
- [TI map IP entity to Workday(ASimAuditEventLogs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_Workday_Updated.yaml)
- [TI map URL entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_CloudAppEvents_Updated.yaml)

### Hunting Queries (14)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntDomain.yaml)
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntHash.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)
- [Google Threat Intelligence - Threat Hunting Url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntUrl.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress indicator in CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Hunting%20Queries/Lumen_IPIndicator_CommonSecurityLog.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Domain All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureDomainThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureHashThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting URL All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureUrlThreatActorHunt.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map File Entity to OfficeActivity Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_OfficeActivity.yaml)
- [TI Map File Entity to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_SecurityEvent.yaml)
- [TI Map File Entity to Syslog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_Syslog.yaml)
- [TI Map File Entity to VMConnection Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_VMConnection.yaml)
- [TI Map File Entity to WireData Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_WireData.yaml)

### Workbooks (6)

**In solution [DORA Compliance](../solutions/dora-compliance.md):**
- [DORACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance/Workbooks/DORACompliance.json)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFutureDomainCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureDomainCorrelation.json)
- [RecordedFutureHashCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureHashCorrelation.json)
- [RecordedFutureIPCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureIPCorrelation.json)
- [RecordedFutureURLCorrelation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Workbooks/RecordedFutureURLCorrelation.json)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [ThreatIntelligenceNew](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Workbooks/ThreatIntelligenceNew.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/threatintelligence`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
