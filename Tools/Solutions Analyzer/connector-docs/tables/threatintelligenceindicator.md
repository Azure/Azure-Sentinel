# ThreatIntelligenceIndicator

Reference for ThreatIntelligenceIndicator table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Security |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/threatintelligenceindicator) |

## Solutions (27)

This table is used by the following solutions:

- [CofenseIntelligence](../solutions/cofenseintelligence.md)
- [CofenseTriage](../solutions/cofensetriage.md)
- [CognyteLuminar](../solutions/cognyteluminar.md)
- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md)
- [Datalake2Sentinel](../solutions/datalake2sentinel.md)
- [Forcepoint NGFW](../solutions/forcepoint-ngfw.md)
- [GitLab](../solutions/gitlab.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [Infoblox](../solutions/infoblox.md)
- [Infoblox Cloud Data Connector](../solutions/infoblox-cloud-data-connector.md)
- [LastPass](../solutions/lastpass.md)
- [MISP2Sentinel](../solutions/misp2sentinel.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Defender Threat Intelligence](../solutions/microsoft-defender-threat-intelligence.md)
- [MimecastTIRegional](../solutions/mimecasttiregional.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand%28pod%29-email-security.md)
- [SOC Handbook](../solutions/soc-handbook.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [ThreatConnect](../solutions/threatconnect.md)
- [Ubiquiti UniFi](../solutions/ubiquiti-unifi.md)
- [VMRay](../solutions/vmray.md)
- [Web Session Essentials](../solutions/web-session-essentials.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (14)

This table is ingested by the following connectors:

- [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md)
- [Cofense Triage Threat Indicators Ingestion](../connectors/cofensetriage.md)
- [Luminar IOCs and Leaked Credentials](../connectors/cognyteluminar.md)
- [CrowdStrike Falcon Adversary Intelligence ](../connectors/crowdstrikefalconadversaryintelligence.md)
- [Datalake2Sentinel](../connectors/datalake2sentinelconnector.md)
- [GreyNoise Threat Intelligence](../connectors/greynoise2sentinelapi.md)
- [MISP2Sentinel](../connectors/misp2sentinelconnector.md)
- [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)
- [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md)
- [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)
- [Threat Intelligence Platforms](../connectors/threatintelligence.md)
- [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)
- [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md)
- [VMRayThreatIntelligence](../connectors/vmray.md)

---

## Content Items Using This Table (79)

### Analytic Rules (58)

**In solution [GitLab](../solutions/gitlab.md):**
- [GitLab - TI - Connection from Malicious IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_MaliciousIP.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI Map IP Entity to CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_CustomSecurityLog.yaml)
- [GreyNoise TI Map IP Entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_DnsEvents.yaml)
- [GreyNoise TI Map IP Entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_SigninLogs.yaml)
- [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml)
- [GreyNoise TI map IP entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_OfficeActivity.yaml)

**In solution [Infoblox Cloud Data Connector](../solutions/infoblox-cloud-data-connector.md):**
- [Infoblox - TI - CommonSecurityLog Match Found - MalwareC2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-TI-CommonSecurityLogMatchFound-MalwareC2.yaml)
- [Infoblox - TI - InfobloxCDC Match Found - Lookalike Domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-TI-InfobloxCDCMatchFound-LookalikeDomains.yaml)
- [Infoblox - TI - Syslog Match Found - URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Analytic%20Rules/Infoblox-TI-SyslogMatchFound-URL.yaml)

**In solution [LastPass](../solutions/lastpass.md):**
- [TI map IP entity to LastPass data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Analytic%20Rules/TIMapIPEntityToLastPass.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - TI map IP to DataverseActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20TI%20map%20IP%20to%20DataverseActivity.yaml)
- [Dataverse - TI map URL to DataverseActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20TI%20map%20URL%20to%20DataverseActivity.yaml)

**In solution [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand%28pod%29-email-security.md):**
- [ProofpointPOD - Email sender IP in TI list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODEmailSenderIPinTIList.yaml)
- [ProofpointPOD - Email sender in TI list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODEmailSenderInTIList.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [Preview - TI map Domain entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_CloudAppEvents.yaml)
- [Preview - TI map Email entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_CloudAppEvents.yaml)
- [Preview - TI map IP entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_CloudAppEvents.yaml)
- [Preview - TI map URL entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_CloudAppEvents.yaml)
- [TI Map IP Entity to Azure SQL Security Audit Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureSQL.yaml)
- [TI Map IP Entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureActivity.yaml)
- [TI Map IP Entity to CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_CustomSecurityLog.yaml)
- [TI Map IP Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DeviceNetworkEvents.yaml)
- [TI Map IP Entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DnsEvents.yaml)
- [TI Map IP Entity to Duo Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DuoSecurity.yaml)
- [TI Map IP Entity to VMConnection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_VMConnection.yaml)
- [TI Map IP Entity to W3CIISLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_W3CIISLog.yaml)
- [TI Map URL Entity to PaloAlto Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_PaloAlto.yaml)
- [TI Map URL Entity to Syslog Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_Syslog.yaml)
- [TI map Domain entity to Dns Events (ASIM DNS Schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_DomainEntity_DnsEvents.yaml)
- [TI map Domain entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_DnsEvents.yaml)
- [TI map Domain entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_EmailUrlInfo.yaml)
- [TI map Domain entity to PaloAlto](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_PaloAlto.yaml)
- [TI map Domain entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_CommonSecurityLog.yaml)
- [TI map Domain entity to Syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_Syslog.yaml)
- [TI map Domain entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_imWebSession.yaml)
- [TI map Email entity to AzureActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_AzureActivity.yaml)
- [TI map Email entity to PaloAlto CommonSecurityLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_PaloAlto.yaml)
- [TI map Email entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_SecurityAlert.yaml)
- [TI map Email entity to SecurityEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_SecurityEvent.yaml)
- [TI map File Hash to CommonSecurityLog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/FileHashEntity_CommonSecurityLog.yaml)
- [TI map File Hash to DeviceFileEvents Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/FileHashEntity_DeviceFileEvents.yaml)
- [TI map File Hash to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/FileHashEntity_SecurityEvent.yaml)
- [TI map IP entity to AWSCloudTrail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AWSCloudTrail.yaml)
- [TI map IP entity to AppServiceHTTPLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AppServiceHTTPLogs.yaml)
- [TI map IP entity to Azure Key Vault logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureKeyVault.yaml)
- [TI map IP entity to AzureFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureFirewall.yaml)
- [TI map IP entity to AzureNetworkAnalytics_CL (NSG Flow Logs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureNetworkAnalytics.yaml)
- [TI map IP entity to DNS Events (ASIM DNS schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/imDns_IPEntity_DnsEvents.yaml)
- [TI map IP entity to GitHub_CL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/Threat%20Intel%20Matches%20to%20GitHub%20Audit%20Logs.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)
- [TI map IP entity to Web Session Events (ASIM Web Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imWebSession.yaml)
- [TI map IP entity to Workday(ASimAuditEventLogs)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_Workday.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [Threat Connect TI map Domain entity to DnsEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_DomainEntity_DnsEvents.yaml)
- [ThreatConnect TI Map URL Entity to OfficeActivity Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_URLEntity_OfficeActivity.yaml)
- [ThreatConnect TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_EmailEntity_OfficeActivity.yaml)
- [ThreatConnect TI map Email entity to SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_EmailEntity_SigninLogs.yaml)
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

**In solution [Ubiquiti UniFi](../solutions/ubiquiti-unifi.md):**
- [Ubiquiti - Connection to known malicious IP or C2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Analytic%20Rules/UbiquitiDestinationInTiList.yaml)

### Hunting Queries (5)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map File Entity to OfficeActivity Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_OfficeActivity.yaml)
- [TI Map File Entity to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_SecurityEvent.yaml)
- [TI Map File Entity to Syslog Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_Syslog.yaml)
- [TI Map File Entity to VMConnection Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_VMConnection.yaml)
- [TI Map File Entity to WireData Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_WireData.yaml)

### Workbooks (16)

**In solution [CofenseIntelligence](../solutions/cofenseintelligence.md):**
- [CofenseIntelligenceThreatIndicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence/Workbooks/CofenseIntelligenceThreatIndicators.json)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [Forcepoint NGFW](../solutions/forcepoint-ngfw.md):**
- [ForcepointNGFWAdvanced](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Workbooks/ForcepointNGFWAdvanced.json)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoiseOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Workbooks/GreyNoiseOverview.json)

**In solution [Infoblox](../solutions/infoblox.md):**
- [Infoblox_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Workbooks/Infoblox_Workbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Defender Threat Intelligence](../solutions/microsoft-defender-threat-intelligence.md):**
- [MicrosoftThreatIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20Threat%20Intelligence/Workbooks/MicrosoftThreatIntelligence.json)

**In solution [MimecastTIRegional](../solutions/mimecasttiregional.md):**
- [MimecastTIRegional](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MimecastTIRegional/Workbooks/MimecastTIRegional.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

**In solution [SOC Handbook](../solutions/soc-handbook.md):**
- [IntsightsIOCWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/IntsightsIOCWorkbook.json)
- [InvestigationInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [ThreatIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Workbooks/ThreatIntelligence.json)

**In solution [Web Session Essentials](../solutions/web-session-essentials.md):**
- [WebSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Workbooks/WebSessionEssentials.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
