# Filter Fields Extraction Report

This report summarizes the filter field values extracted from queries across connectors, content items, and ASIM parsers.

## Summary

| Source Type | Total Items | With Filter Fields | Percentage |
|-------------|-------------|-------------------|------------|
| Connectors | 530 | 95 | 17.9% |
| Content Items | 4864 | 300 | 6.2% |
| ASIM Parsers | 191 | 74 | 38.7% |

## Filter Field Patterns Found

The following table.field combinations were detected in queries:

| Table.Field | Occurrences |
|-------------|-------------|
| CommonSecurityLog.DeviceVendor | 192 |
| CommonSecurityLog.DeviceProduct | 137 |
| Syslog.SyslogMessage | 96 |
| SecurityEvent.EventID | 85 |
| AzureDiagnostics.Category | 58 |
| Syslog.ProcessName | 29 |
| AzureDiagnostics.ResourceType | 27 |
| Event.EventID | 26 |
| Event.Source | 22 |
| WindowsEvent.EventID | 19 |
| Syslog.Facility | 15 |
| WindowsEvent.Provider | 9 |
| ASimAuditEventLogs.EventVendor | 2 |
| ASimDnsActivityLogs.EventProduct | 1 |
| ASimDnsActivityLogs.EventVendor | 1 |
| ASimNetworkSessionLogs.EventProduct | 1 |

## Filter Field Format

Filter fields are stored in the format:
```
table.field operator "value(s)" | table.field operator "value" | ...
```

Supported operators:
- Equality: `==`, `=~` (case-insensitive), `!=`
- Set membership: `in`, `in~` (case-insensitive), `!in`, `!in~`
- String matching: `has`, `has_cs`, `contains`, `contains_cs`, `startswith`, `startswith_cs`, `endswith`, `endswith_cs`
- Multi-value string: `has_any`, `has_all`
- Negative string: `!has`, `!contains`, `!startswith`, `!endswith`
- Regex: `matches regex`

Multiple values for in/has_any/has_all operators are comma-separated inside the quotes.

## Fields Extracted

The following fields are extracted from queries:

| Field | Typical Table | Purpose |
|-------|---------------|--------|
| DeviceVendor | CommonSecurityLog | CEF source vendor |
| DeviceProduct | CommonSecurityLog | CEF source product |
| EventVendor | ASIM tables | Normalized source vendor |
| EventProduct | ASIM tables | Normalized source product |
| ResourceType | AzureDiagnostics | Azure resource type |
| Category | AzureDiagnostics | Log category |
| EventID | WindowsEvent/SecurityEvent/Event | Windows event identifier |
| Source | Event | Event log source (e.g., Service Control Manager) |
| Provider | WindowsEvent | Windows event provider |
| Facility | Syslog | Syslog facility (e.g., auth, authpriv, cron) |
| ProcessName | Syslog | Process that generated the log |
| ProcessID | Syslog | Process ID |
| SyslogMessage | Syslog | Message content (uses string operators: has, contains, etc.) |

---

# Full Listings

## Connectors with Filter Fields

Total: 95 connectors

| Connector ID | Title | Filter Fields | File |
|--------------|-------|---------------|------|
| AIVectraDetect | [Deprecated] Vectra AI Detect via Legacy Agent | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Data%20Connectors/AIVectraDetect.json) |
| AIVectraDetectAma | [Deprecated] Vectra AI Detect via AMA | CommonSecurityLog.DeviceProduct =~ "X Series"  \|  CommonSecurityLog.DeviceVendor =~ "Vectra Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Data%20Connectors/template_AIVectraDetectAma.json) |
| ASimDnsActivityLogs | Windows DNS Events via AMA | ASimDnsActivityLogs.EventProduct == "DNS Server"  \|  ASimDnsActivityLogs.EventVendor == "Microsoft" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Data%20Connectors/template_ASimDnsActivityLogs.JSON) |
| AkamaiSecurityEvents | [Deprecated] Akamai Security Events via Legacy Agent | CommonSecurityLog.DeviceProduct == "akamai_siem"  \|  CommonSecurityLog.DeviceVendor == "Akamai" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events/Data%20Connectors/Connector_CEF_Akamai.json) |
| AkamaiSecurityEventsAma | [Deprecated] Akamai Security Events via AMA | CommonSecurityLog.DeviceProduct =~ "akamai_siem"  \|  CommonSecurityLog.DeviceVendor =~ "Akamai" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Akamai%20Security%20Events/Data%20Connectors/template_AkamaiSecurityEventsAMA.json) |
| AristaAwakeSecurity | [Deprecated] Awake Security via Legacy Agent | CommonSecurityLog.DeviceProduct == "Awake Security"  \|  CommonSecurityLog.DeviceVendor == "Arista Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Data%20Connectors/Connector_AristaAwakeSecurity_CEF.json) |
| ArubaClearPass | [Deprecated] Aruba ClearPass via Legacy Agent | CommonSecurityLog.DeviceProduct == "ClearPass"  \|  CommonSecurityLog.DeviceVendor == "Aruba Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass/Data%20Connectors/Connector_Syslog_ArubaClearPass.json) |
| ArubaClearPassAma | [Deprecated] Aruba ClearPass via AMA | CommonSecurityLog.DeviceProduct =~ "ClearPass"  \|  CommonSecurityLog.DeviceVendor =~ "Aruba Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass/Data%20Connectors/template_ArubaClearPassAMA.json) |
| AutomatedLogicWebCTRL | Automated Logic WebCTRL  | Event.Source == "ALCWebCTRL" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ALC-WebCTRL/Data%20Connectors/Connector_WindowsEvents_WebCTRL.json) |
| AzureFirewall | Azure Firewall | AzureDiagnostics.ResourceType == "AZUREFIREWALLS" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Data%20Connectors/AzureFirewall.JSON) |
| AzureKubernetes | Azure Kubernetes Service (AKS) | AzureDiagnostics.Category in "cluster-autoscaler,guard,kube-apiserver,kube-audit,kube-audit-admin,kube-controller-manager,kube-scheduler" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Data%20Connectors/AzureKubernetes.JSON) |
| AzureNSG | Network Security Groups | AzureDiagnostics.Category in "NetworkSecurityGroupEvent,NetworkSecurityGroupRuleCounter" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Network%20Security%20Groups/Data%20Connectors/AzureNSG.JSON) |
| AzureSql | Azure SQL Databases | AzureDiagnostics.Category in "AutomaticTuning,Basic,Blocks,DatabaseWaitStatistics,Deadlocks,DevOpsOperationsAudit,Errors,InstanceAndAppAdvanced,QueryStoreWaitStatistics,SQLInsights,SQLSecurityAuditEvents,Timeouts,WorkloadManagement"  \|  AzureDiagnostics.Category contains "SQLSecurityAuditEvents"  \|  AzureDiagnostics.ResourceType == "SERVERS/DATABASES" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Data%20Connectors/template_AzureSql.JSON) |
| Barracuda | [Deprecated] Barracuda Web Application Firewall via Legacy A | CommonSecurityLog.DeviceVendor == "Barracuda" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20WAF/Data%20Connectors/template_Barracuda.json) |
| BroadcomSymantecDLP | [Deprecated] Broadcom Symantec DLP via Legacy Agent | CommonSecurityLog.DeviceProduct == "DLP"  \|  CommonSecurityLog.DeviceVendor == "Symantec" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Data%20Connectors/Connector_Syslog_SymantecDLP.json) |
| BroadcomSymantecDLPAma | [Deprecated] Broadcom Symantec DLP via AMA | CommonSecurityLog.DeviceProduct =~ "DLP"  \|  CommonSecurityLog.DeviceVendor =~ "Symantec" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Broadcom%20SymantecDLP/Data%20Connectors/template_SymantecDLPAMA.json) |
| CEF | Common Event Format (CEF) | CommonSecurityLog.DeviceVendor !in "Cisco,Check Point,Palo Alto Networks,Fortinet,F5,Barracuda,ExtraHop,OneIdentity,Zscaler,ForgeRock Inc,Cyber-Ark,illusive,Vectra Networks,Citrix,Darktrace,Akamai,Aruba Networks,CrowdStrike,Symantec,Claroty,Contrast Security,Delinea Software,Thycotic Software,FireEye,Forcepoint CSG,Forcepoint,Forcepoint CASB,iboss,Illumio,Imperva Inc.,Infoblox,Morphisec,Netwrix,Nozomi,Onapsis,OSSEC,PingFederate,RidgeSecurity,SonicWall,Trend Micro,vArmour"  \|  CommonSecurityLog.DeviceVendor !in "Cisco,Check Point,Palo Alto Networks,Fortinet,F5,Barracuda,ExtraHop,OneIdentity,Zscaler,ForgeRock Inc,Cyber-Ark,illusive,Vectra Networks,Citrix,Darktrace,Akamai,Aruba Networks,CrowdStrike,Symantec,Claroty,Contrast Security,Delinea Software,Thycotic Software,FireEye,Forcepoint CSG,Forcepoint,Forcepoint CASB,iboss,Illumio,Imperva Inc.,Infoblox,Morphisec,Netwrix,Nozomi,Onapsis,OSSEC,PingFederate,RidgeSecurity,SonicWall,Trend Micro,vArmour,Votiro" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format/Data%20Connectors/CEF.JSON) |
| CTERA | CTERA Syslog | Syslog.ProcessName == "gw-audit"  \|  Syslog.SyslogMessage contains "gw-audit[-]:"  \|  Syslog.SyslogMessage contains "portal portal[-]:" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Data%20Connectors/CTERA_Data_Connector.json) |
| CiscoASA | Cisco ASA via Legacy Agent | CommonSecurityLog.DeviceProduct == "ASA"  \|  CommonSecurityLog.DeviceVendor =~ "Cisco" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/CiscoASA.JSON) |
| CiscoAsaAma | Cisco ASA/FTD via AMA | CommonSecurityLog.DeviceProduct in "ASA,FTD"  \|  CommonSecurityLog.DeviceVendor == "Cisco" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Data%20Connectors/template_CiscoAsaAma.JSON) |
| CiscoFirepowerEStreamer | [Deprecated] Cisco Firepower eStreamer via Legacy Agent | CommonSecurityLog.DeviceProduct == "Firepower"  \|  CommonSecurityLog.DeviceVendor == "Cisco" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Data%20Connectors/CiscoFirepowerEStreamerCollector.json) |
| CiscoFirepowerEStreamerAma | [Deprecated] Cisco Firepower eStreamer via AMA | CommonSecurityLog.DeviceProduct =~ "Firepower"  \|  CommonSecurityLog.DeviceVendor =~ "Cisco" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Data%20Connectors/template_CiscoFirepowerEStreamerAMA.json) |
| CiscoSEGAma | [Deprecated] Cisco Secure Email Gateway via AMA | CommonSecurityLog.DeviceProduct =~ "ESA_CONSOLIDATED_LOG_EVENT"  \|  CommonSecurityLog.DeviceVendor =~ "Cisco" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Data%20Connectors/template_CiscoSEGAMA.json) |
| CitrixWAF | [Deprecated] Citrix WAF (Web App Firewall) via Legacy Agent | CommonSecurityLog.DeviceProduct == "NetScaler"  \|  CommonSecurityLog.DeviceVendor == "Citrix" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall/Data%20Connectors/Citrix_WAF.json) |
| CitrixWAFAma | [Deprecated] Citrix WAF (Web App Firewall) via AMA | CommonSecurityLog.DeviceProduct =~ "NetScaler"  \|  CommonSecurityLog.DeviceVendor =~ "Citrix" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall/Data%20Connectors/template_Citrix_WAFAMA.json) |
| ClarotyAma | [Deprecated] Claroty via AMA | CommonSecurityLog.DeviceVendor =~ "Claroty" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Data%20Connectors/template_ClarotyAMA.json) |
| ClarotyxDome | Claroty xDome | CommonSecurityLog.DeviceVendor in "Claroty,Medigate" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty%20xDome/Data%20Connectors/Claroty_xDome.json) |
| ContrastProtect | [Deprecated] Contrast Protect via Legacy Agent | CommonSecurityLog.DeviceVendor == "Contrast Security" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Data%20Connectors/ContrastProtect.json) |
| ContrastProtectAma | [Deprecated] Contrast Protect via AMA | CommonSecurityLog.DeviceVendor =~ "Contrast Security" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Data%20Connectors/template_ContrastProtectAMA.json) |
| CrowdStrikeFalconEndpointProtection | [Deprecated] CrowdStrike Falcon Endpoint Protection via Lega | CommonSecurityLog.DeviceProduct == "FalconHost"  \|  CommonSecurityLog.DeviceVendor == "CrowdStrike" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/Connector_Syslog_CrowdStrikeFalconEndpointProtection.json) |
| CrowdStrikeFalconEndpointProtectionAma | [Deprecated] CrowdStrike Falcon Endpoint Protection via AMA | CommonSecurityLog.DeviceProduct =~ "FalconHost"  \|  CommonSecurityLog.DeviceVendor =~ "CrowdStrike" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/template_CrowdStrikeFalconEndpointProtectionAma.json) |
| CyberArk | [Deprecated] CyberArk Enterprise Password Vault (EPV) Events | CommonSecurityLog.DeviceProduct == "Vault"  \|  CommonSecurityLog.DeviceVendor == "Cyber-Ark" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Data%20Connectors/CyberArk%20Data%20Connector.json) |
| CyberArkAma | [Deprecated] CyberArk Privilege Access Manager (PAM) Events  | CommonSecurityLog.DeviceProduct =~ "Vault"  \|  CommonSecurityLog.DeviceVendor =~ "Cyber-Ark" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Data%20Connectors/template_CyberArkAMA.json) |
| DDOS | Azure DDoS Protection | AzureDiagnostics.Category == "DDoSMitigationReports"  \|  AzureDiagnostics.ResourceType == "PUBLICIPADDRESSES" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Data%20Connectors/DDOS.JSON) |
| Darktrace | [Deprecated] AI Analyst Darktrace via Legacy Agent | CommonSecurityLog.DeviceVendor == "Darktrace" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace/Data%20Connectors/AIA-Darktrace.json) |
| DarktraceAma | [Deprecated] AI Analyst Darktrace via AMA | CommonSecurityLog.DeviceVendor =~ "Darktrace" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace/Data%20Connectors/template_AIA-DarktraceAMA.json) |
| DelineaSecretServerAma | [Deprecated] Delinea Secret Server via AMA | CommonSecurityLog.DeviceProduct =~ "Secret Server"  \|  CommonSecurityLog.DeviceVendor in~ "Delinea Software,Thycotic Software" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/template_DelineaSecretServerAMA.json) |
| DelineaSecretServer_CEF | [Deprecated] Delinea Secret Server via Legacy Agent | CommonSecurityLog.DeviceProduct == "Secret Server"  \|  CommonSecurityLog.DeviceVendor in "Delinea Software,Thycotic Software" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Data%20Connectors/DelineaSecretServer_CEF.json) |
| ExtraHopNetworks | [Deprecated] ExtraHop Reveal(x) via Legacy Agent | CommonSecurityLog.DeviceVendor == "ExtraHop" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopNetworks.json) |
| ExtraHopNetworksAma | [Deprecated] ExtraHop Reveal(x) via AMA | CommonSecurityLog.DeviceVendor =~ "ExtraHop" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Data%20Connectors/template_ExtraHopReveal%28x%29AMA.json) |
| F5 | [Deprecated] F5 Networks via Legacy Agent | CommonSecurityLog.DeviceVendor == "F5" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks/Data%20Connectors/template_F5.json) |
| F5Ama | [Deprecated] F5 Networks via AMA | CommonSecurityLog.DeviceVendor =~ "F5" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20Networks/Data%20Connectors/template_F5NetworksAMA.json) |
| FireEyeNXAma | [Deprecated] FireEye Network Security (NX) via AMA | CommonSecurityLog.DeviceVendor =~ "FireEye" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/template_FireEyeNX_CEFAMA.json) |
| ForcepointCSG | [Deprecated] Forcepoint CSG via Legacy Agent | CommonSecurityLog.DeviceProduct in "Email,Web"  \|  CommonSecurityLog.DeviceVendor == "Forcepoint CSG" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/ForcepointCloudSecurityGateway.json) |
| ForcepointCSGAma | [Deprecated] Forcepoint CSG via AMA | CommonSecurityLog.DeviceProduct in~ "Email,Web"  \|  CommonSecurityLog.DeviceVendor =~ "Forcepoint CSG" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Data%20Connectors/template_ForcepointCloudSecurityGatewayAMA.json) |
| ForcepointCasb | [Deprecated] Forcepoint CASB via Legacy Agent | CommonSecurityLog.DeviceVendor == "Forcepoint CASB" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/Forcepoint%20CASB.json) |
| ForcepointCasbAma | [Deprecated] Forcepoint CASB via AMA | CommonSecurityLog.DeviceVendor =~ "Forcepoint CASB" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Data%20Connectors/template_Forcepoint%20CASBAMA.json) |
| ForcepointNgfw | [Deprecated] Forcepoint NGFW via Legacy Agent | CommonSecurityLog.DeviceProduct == "NGFW"  \|  CommonSecurityLog.DeviceVendor == "Forcepoint" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Data%20Connectors/FORCEPOINT_NGFW.json) |
| ForcepointNgfwAma | [Deprecated] Forcepoint NGFW via AMA | CommonSecurityLog.DeviceProduct =~ "NGFW"  \|  CommonSecurityLog.DeviceVendor =~ "Forcepoint" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Data%20Connectors/template_FORCEPOINT_NGFWAMA.json) |
| ForgeRock | [Deprecated] ForgeRock Identity Platform | CommonSecurityLog.DeviceProduct == "IDM"  \|  CommonSecurityLog.DeviceVendor == "ForgeRock Inc" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF/Data%20Connectors/ForgeRock_CEF.json) |
| Fortinet | [Deprecated] Fortinet via Legacy Agent | CommonSecurityLog.DeviceProduct startswith "Fortigate"  \|  CommonSecurityLog.DeviceVendor == "Fortinet" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/Fortinet-FortiGate.json) |
| FortinetAma | [Deprecated] Fortinet via AMA | CommonSecurityLog.DeviceProduct =~ "Fortigate"  \|  CommonSecurityLog.DeviceProduct startswith "Fortigate"  \|  CommonSecurityLog.DeviceVendor =~ "Fortinet" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_Fortinet-FortiGateAma.json) |
| FortinetFortiWeb | [Deprecated] Fortinet FortiWeb Web Application Firewall via  | CommonSecurityLog.DeviceProduct == "Fortiweb"  \|  CommonSecurityLog.DeviceVendor == "Fortinet" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/Fortiweb.json) |
| FortinetFortiWebAma | Fortinet FortiWeb Web Application Firewall via AMA | CommonSecurityLog.DeviceProduct contains "Fortiweb"  \|  CommonSecurityLog.DeviceVendor contains "Fortinet" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_FortiwebAma.json) |
| IllumioCoreAma | [Deprecated] Illumio Core via AMA | CommonSecurityLog.DeviceVendor =~ "Illumio" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core/Data%20Connectors/template_IllumioCoreAMA.json) |
| ImpervaWAFGateway | Imperva WAF Gateway | CommonSecurityLog.DeviceProduct == "WAF Gateway"  \|  CommonSecurityLog.DeviceVendor in "Imperva,Imperva Inc." | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Imperva%20WAF%20Gateway/Data%20Connectors/Connector_Imperva_WAF_Gateway.json) |
| InfobloxCloudDataConnector | [Deprecated] Infoblox Cloud Data Connector via Legacy Agent | CommonSecurityLog.DeviceProduct == "Data Connector"  \|  CommonSecurityLog.DeviceVendor == "Infoblox" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Data%20Connectors/InfobloxCloudDataConnector.json) |
| InfobloxCloudDataConnectorAma | [Recommended] Infoblox Cloud Data Connector via AMA | CommonSecurityLog.DeviceProduct =~ "Data Connector"  \|  CommonSecurityLog.DeviceVendor =~ "Infoblox" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxCEFDataConnector/template_InfobloxCloudDataConnectorAma.JSON) |
| InfobloxSOCInsightsDataConnector_AMA | [Recommended] Infoblox SOC Insight Data Connector via AMA | CommonSecurityLog.DeviceProduct =~ "Data Connector"  \|  CommonSecurityLog.DeviceVendor =~ "Infoblox" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_AMA.json) |
| InfobloxSOCInsightsDataConnector_Legacy | [Deprecated] Infoblox SOC Insight Data Connector via Legacy  | CommonSecurityLog.DeviceProduct == "Data Connector"  \|  CommonSecurityLog.DeviceVendor == "Infoblox" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_Legacy.json) |
| IronNetIronDefense | IronNet IronDefense | CommonSecurityLog.DeviceProduct in "IronDefense,IronDome"  \|  CommonSecurityLog.DeviceVendor == "IronNet" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Data%20Connectors/IronNetIronDefense.json) |
| MicrosoftSysmonForLinux | [Deprecated] Microsoft Sysmon For Linux | Syslog.ProcessName == "sysmon" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Sysmon%20For%20Linux/Data%20Connectors/SysmonForLinux.json) |
| NasuniEdgeAppliance | [Deprecated] Nasuni Edge Appliance | Syslog.Facility != "cron" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni/Data%20Connectors/Nasuni%20Data%20Connector.json) |
| NetwrixAma | [Deprecated] Netwrix Auditor via AMA | CommonSecurityLog.DeviceVendor =~ "Netwrix" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Data%20Connectors/template_NetwrixAuditorAMA.json) |
| NozomiNetworksN2OSAma | [Deprecated] Nozomi Networks N2OS via AMA | CommonSecurityLog.DeviceVendor has "Nozomi" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NozomiNetworks/Data%20Connectors/template_NozomiNetworksN2OSAMA.json) |
| OSSECAma | [Deprecated] OSSEC via AMA | CommonSecurityLog.DeviceVendor =~ "OSSEC" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC/Data%20Connectors/template_OSSECAMA.json) |
| OnapsisPlatform | [Deprecated] Onapsis Platform | CommonSecurityLog.DeviceProduct == "OSP"  \|  CommonSecurityLog.DeviceVendor == "Onapsis" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform/Data%20Connectors/OnapsisPlatform.json) |
| OneIdentity | One Identity Safeguard | CommonSecurityLog.DeviceProduct == "SPS"  \|  CommonSecurityLog.DeviceVendor == "OneIdentity" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneIdentity/Data%20Connectors/OneIdentity.JSON) |
| PaloAltoCDLAma | [Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via A | CommonSecurityLog.DeviceProduct =~ "LF"  \|  CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Data%20Connectors/template_PaloAlto_CDLAMA.json) |
| PaloAltoNetworks | [Deprecated] Palo Alto Networks (Firewall) via Legacy Agent | CommonSecurityLog.DeviceProduct has "PAN-OS"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Data%20Connectors/PaloAltoNetworks.json) |
| PaloAltoNetworksAma | [Deprecated] Palo Alto Networks (Firewall) via AMA | CommonSecurityLog.DeviceProduct =~ "PAN-OS"  \|  CommonSecurityLog.DeviceProduct has "PAN-OS"  \|  CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Data%20Connectors/template_PaloAltoNetworksAMA.json) |
| PaloAltoNetworksCortex | Palo Alto Networks Cortex XDR | CommonSecurityLog.DeviceProduct == "Cortex XDR"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29/Data%20Connectors/Connector_PaloAlto_XDR_CEF.json) |
| PingFederateAma | [Deprecated] PingFederate via AMA | CommonSecurityLog.DeviceProduct has "PingFederate" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Data%20Connectors/template_PingFederateAMA.json) |
| RadiflowIsid | Radiflow iSID via AMA | CommonSecurityLog.DeviceProduct =~ "iSID" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Data%20Connectors/RadiflowIsid.json) |
| RidgeBotDataConnector | [Deprecated] RIDGEBOT - data connector for Microsoft Sentine | CommonSecurityLog.DeviceVendor == "RidgeSecurity" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RidgeSecurity/Data%20Connectors/RidgeSecurity.json) |
| SilverfortAma | Silverfort Admin Console | CommonSecurityLog.DeviceProduct == "Admin Console"  \|  CommonSecurityLog.DeviceProduct has "Admin Console"  \|  CommonSecurityLog.DeviceVendor == "Silverfort"  \|  CommonSecurityLog.DeviceVendor has "Silverfort" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Data%20Connectors/SilverfortAma.json) |
| SonicWallFirewall | [Deprecated] SonicWall Firewall via Legacy Agent | CommonSecurityLog.DeviceVendor == "SonicWall" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Data%20Connectors/SonicwallFirewall.json) |
| SonicWallFirewallAma | [Deprecated] SonicWall Firewall via AMA | CommonSecurityLog.DeviceVendor =~ "SonicWall" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Data%20Connectors/template_SonicwallFirewallAMA.json) |
| Syslog | Syslog via Legacy Agent | Syslog.Facility != "cron" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_Syslog.json) |
| SyslogAma | Syslog via AMA | Syslog.Facility != "cron" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Data%20Connectors/template_SyslogAma.json) |
| TrendMicroApexOneAma | [Deprecated] Trend Micro Apex One via AMA | CommonSecurityLog.DeviceProduct =~ "Apex Central"  \|  CommonSecurityLog.DeviceVendor =~ "Trend Micro" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Data%20Connectors/template_TrendMicro_ApexOneAMA.json) |
| Votiro | [Deprecated] Votiro Sanitization Engine Logs | CommonSecurityLog.DeviceProduct == "Votiro cloud"  \|  CommonSecurityLog.DeviceVendor == "Votiro" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Votiro/Data%20Connectors/VotiroEvents.json) |
| WAF | Azure Web Application Firewall (WAF) | AzureDiagnostics.ResourceType in "APPLICATIONGATEWAYS,CDNWEBAPPLICATIONFIREWALLPOLICIES,FRONTDOORS" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Data%20Connectors/template_WAF.JSON) |
| WindowsFirewallAma | Windows Firewall Events via AMA | ASimNetworkSessionLogs.EventProduct == "Windows Firewall" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Data%20Connectors/template_WindowsFirewallAma.JSON) |
| WireX_Systems_NFP | [Deprecated] WireX Network Forensics Platform via Legacy Age | CommonSecurityLog.DeviceProduct == "WireX NFP"  \|  CommonSecurityLog.DeviceVendor == "WireX" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WireX%20Network%20Forensics%20Platform/Data%20Connectors/WireXsystemsNFP%281b%29.json) |
| WireX_Systems_NFPAma | [Deprecated] WireX Network Forensics Platform via AMA | CommonSecurityLog.DeviceProduct =~ "WireX NFP"  \|  CommonSecurityLog.DeviceVendor =~ "WireX" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WireX%20Network%20Forensics%20Platform/Data%20Connectors/template_WireXsystemsNFPAMA.json) |
| WithSecureElementsViaConnector | [Deprecated] WithSecure Elements via Connector | CommonSecurityLog.DeviceVendor == "WithSecure™" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WithSecureElementsViaConnector/Data%20Connectors/WithSecureElementsViaConnector.json) |
| Zscaler | [Deprecated] Zscaler via Legacy Agent | CommonSecurityLog.DeviceVendor == "Zscaler" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Data%20Connectors/template_Zscaler.JSON) |
| ZscalerAma | [Deprecated] Zscaler via AMA | CommonSecurityLog.DeviceVendor =~ "Zscaler" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Data%20Connectors/template_ZscalerAma.JSON) |
| iboss | [Deprecated] iboss via Legacy Agent | CommonSecurityLog.DeviceVendor =~ "iboss" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Data%20Connectors/iboss_cef.json) |
| ibossAma | iboss via AMA | CommonSecurityLog.DeviceVendor =~ "iboss" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Data%20Connectors/template_ibossAMA.json) |
| illusiveAttackManagementSystem | [Deprecated] Illusive Platform via Legacy Agent | CommonSecurityLog.DeviceProduct == "illusive"  \|  CommonSecurityLog.DeviceVendor == "illusive" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Data%20Connectors/illusive%20Attack%20Management%20System.json) |
| illusiveAttackManagementSystemAma | [Deprecated] Illusive Platform via AMA | CommonSecurityLog.DeviceProduct =~ "illusive"  \|  CommonSecurityLog.DeviceVendor =~ "illusive" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Data%20Connectors/template_IllusivePlatformAMA.json) |
| vArmourAC | [Deprecated] vArmour Application Controller via Legacy Agent | CommonSecurityLog.DeviceProduct == "AC"  \|  CommonSecurityLog.DeviceVendor == "vArmour" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Data%20Connectors/Connector_vArmour_AppController_CEF.json) |
| vArmourACAma | [Deprecated] vArmour Application Controller via AMA | CommonSecurityLog.DeviceProduct =~ "AC"  \|  CommonSecurityLog.DeviceVendor =~ "vArmour" | [Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Data%20Connectors/template_vArmour_AppControllerAMA.json) |

## Content Items with Filter Fields

Total: 300 content items

### AI Analyst Darktrace

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | AIA-Darktrace | CommonSecurityLog.DeviceProduct in "AI Analyst,Enterprise Immune System"  \|  CommonSecurityLog.DeviceVendor == "Darktrace" | [AIA-Darktrace.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace/Workbooks/AIA-Darktrace.json) |

### Acronis Cyber Protect Cloud

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Acronis - Login from Abnormal IP - Low Occurrence | CommonSecurityLog.DeviceVendor == "Acronis audit" | [AcronisLoginFromAbnormalIPLowOccurrence.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisLoginFromAbnormalIPLowOccurrence.yaml) |
| analytic_rule | Acronis - Multiple Endpoints Accessing Malicious U | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisMultipleEndpointsAccessingMaliciousURLs.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisMultipleEndpointsAccessingMaliciousURLs.yaml) |
| analytic_rule | Acronis - Multiple Endpoints Infected by Ransomwar | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisMultipleEndpointsInfectedByRansomware.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisMultipleEndpointsInfectedByRansomware.yaml) |
| analytic_rule | Acronis - Multiple Inboxes with Malicious Content  | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisMultipleInboxesWithMaliciousContentDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Analytic%20Rules/AcronisMultipleInboxesWithMaliciousContentDetected.yaml) |
| hunting_query | Acronis - ASZ defence: Unauthorized operation is d | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisUnauthorizedOperationIsDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisUnauthorizedOperationIsDetected.yaml) |
| hunting_query | Acronis - Agent failed updating more than twice in | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisAgentFailedUpdatingMoreThanTwiceInADay.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisAgentFailedUpdatingMoreThanTwiceInADay.yaml) |
| hunting_query | Acronis - Agents offline for 2 days or more | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisAgentsOfflineFor2DaysOrMore.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisAgentsOfflineFor2DaysOrMore.yaml) |
| hunting_query | Acronis - Audit Log | CommonSecurityLog.DeviceVendor == "Acronis audit" | [AcronisAuditLog.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisAuditLog.yaml) |
| hunting_query | Acronis - Cloud Connection Errors | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisCloudConnectionErrors.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisCloudConnectionErrors.yaml) |
| hunting_query | Acronis - Endpoints Accessing Malicious URLs | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisEndpointsAccessingMaliciousURLs.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsAccessingMaliciousURLs.yaml) |
| hunting_query | Acronis - Endpoints Infected by Ransomware | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisEndpointsInfectedByRansomware.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsInfectedByRansomware.yaml) |
| hunting_query | Acronis - Endpoints with Backup issues | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisEndpointsWithBackupIssues.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsWithBackupIssues.yaml) |
| hunting_query | Acronis - Endpoints with EDR Incidents | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisEndpointsWithEDRIncidents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsWithEDRIncidents.yaml) |
| hunting_query | Acronis - Endpoints with high failed login attempt | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisEndpointsWithHighFailedLoginAttempts.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisEndpointsWithHighFailedLoginAttempts.yaml) |
| hunting_query | Acronis - Inboxes with Malicious Content | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisInboxesWithMaliciousContentDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisInboxesWithMaliciousContentDetected.yaml) |
| hunting_query | Acronis - Login from Abnormal IP - Low Occurrence | CommonSecurityLog.DeviceVendor == "Acronis audit" | [AcronisLoginFromAbnormalIPLowOccurrence.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisLoginFromAbnormalIPLowOccurrence.yaml) |
| hunting_query | Acronis - Protection Service Errors | CommonSecurityLog.DeviceVendor == "Acronis" | [AcronisProtectionServiceErrors.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Acronis%20Cyber%20Protect%20Cloud/Hunting%20Queries/AcronisProtectionServiceErrors.yaml) |

### Apache Log4j Vulnerability Detection

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Azure WAF matching for Log4j vuln(CVE-2021-44228) | AzureDiagnostics.Category in "ApplicationGatewayFirewallLog,FrontdoorWebApplicationFirewallLog" | [AzureWAFmatching_log4j_vuln.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/AzureWAFmatching_log4j_vuln.yaml) |
| analytic_rule | Log4j vulnerability exploit aka Log4Shell IP IOC | AzureDiagnostics.Category in "AzureFirewallApplicationRule,AzureFirewallNetworkRule"  \|  AzureDiagnostics.ResourceType =~ "AZUREFIREWALLS" | [Log4J_IPIOC_Dec112021.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml) |
| hunting_query | Azure WAF Log4j CVE-2021-44228 hunting | AzureDiagnostics.Category in~ "ApplicationGatewayAccessLog,ApplicationGatewayFirewallLog,FrontdoorAccessLog,FrontdoorWebApplicationFirewallLog" | [WAF_log4j_vulnerability.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/WAF_log4j_vulnerability.yaml) |
| hunting_query | Linux security related process termination activit | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [Process_Termination_Activity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Process_Termination_Activity.yaml) |
| hunting_query | Possible Container Miner related artifacts detecte | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [Container_Miner_Activity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Container_Miner_Activity.yaml) |
| hunting_query | Possible Linux attack toolkit detected via Syslog  | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [Linux_Toolkit_Detected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Linux_Toolkit_Detected.yaml) |
| hunting_query | Possible exploitation of Apache log4j component de | Syslog.SyslogMessage has "AUOMS_EXECVE"  \|  Syslog.SyslogMessage has "jndi"  \|  Syslog.SyslogMessage has_any "corba,dns,iiop,ldap,nds,nis,rmi" | [Apache_log4j_Vulnerability.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Apache_log4j_Vulnerability.yaml) |
| hunting_query | Suspicious Base64 download activity detected | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [Base64_Download_Activity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Base64_Download_Activity.yaml) |
| hunting_query | Suspicious Shell script detected | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [Suspicious_ShellScript_Activity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Suspicious_ShellScript_Activity.yaml) |
| hunting_query | Suspicious manipulation of firewall detected via S | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [Firewall_Disable_Activity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Hunting%20Queries/Firewall_Disable_Activity.yaml) |
| workbook | Log4jPostCompromiseHunting | AzureDiagnostics.Category in "ApplicationGatewayAccessLog,ApplicationGatewayFirewallLog,FrontdoorAccessLog,FrontdoorWebApplicationFirewallLog"  \|  Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE"  \|  Syslog.SyslogMessage has "jndi"  \|  Syslog.SyslogMessage has_any "corba,dns,iiop,ldap,nds,nis,rmi" | [Log4jPostCompromiseHunting.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Workbooks/Log4jPostCompromiseHunting.json) |

### AristaAwakeSecurity

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Awake Security - High Match Counts By Device | CommonSecurityLog.DeviceProduct == "Awake Security"  \|  CommonSecurityLog.DeviceVendor == "Arista Networks" | [HighMatchCountsByDevice.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Analytic%20Rules/HighMatchCountsByDevice.yaml) |
| analytic_rule | Awake Security - High Severity Matches By Device | CommonSecurityLog.DeviceProduct == "Awake Security"  \|  CommonSecurityLog.DeviceVendor == "Arista Networks" | [HighSeverityMatchesByDevice.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Analytic%20Rules/HighSeverityMatchesByDevice.yaml) |
| analytic_rule | Awake Security - Model With Multiple Destinations | CommonSecurityLog.DeviceProduct == "Awake Security"  \|  CommonSecurityLog.DeviceVendor == "Arista Networks" | [ModelMatchesWithMultipleDestinationsByDevice.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Analytic%20Rules/ModelMatchesWithMultipleDestinationsByDevice.yaml) |
| workbook | AristaAwakeSecurityWorkbook | CommonSecurityLog.DeviceProduct == "Awake Security"  \|  CommonSecurityLog.DeviceVendor == "Arista Networks" | [AristaAwakeSecurityWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Workbooks/AristaAwakeSecurityWorkbook.json) |

### Attacker Tools Threat Protection Essentials

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Credential Dumping Tools - File Artifacts | Event.EventID == "11" | [CredentialDumpingToolsFileArtifacts.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/CredentialDumpingToolsFileArtifacts.yaml) |
| analytic_rule | Credential Dumping Tools - Service Installation | Event.EventID == "7045"  \|  Event.Source == "Service Control Manager" | [CredentialDumpingServiceInstallation.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/CredentialDumpingServiceInstallation.yaml) |

### Azure DDoS Protection

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | DDoS Attack IP Addresses - PPS Threshold | AzureDiagnostics.Category == "DDoSMitigationFlowLogs"  \|  AzureDiagnostics.ResourceType == "PUBLICIPADDRESSES" | [AttackSourcesPPSThreshold.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Analytic%20Rules/AttackSourcesPPSThreshold.yaml) |
| workbook | AzDDoSStandardWorkbook | AzureDiagnostics.Category in "DDoSMitigationFlowLogs,DDoSMitigationReports,DDoSProtectionNotifications" | [AzDDoSStandardWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Workbooks/AzDDoSStandardWorkbook.json) |

### Azure Firewall

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | AzureFirewallWorkbook | AzureDiagnostics.Category in "AzureFirewallApplicationRule,AzureFirewallDnsProxy,AzureFirewallNetworkRule"  \|  AzureDiagnostics.ResourceType == "AZUREFIREWALLS" | [AzureFirewallWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Firewall/Workbooks/AzureFirewallWorkbook.json) |

### Azure Key Vault

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Azure Key Vault access TimeSeries anomaly | AzureDiagnostics.ResourceType =~ "VAULTS" | [TimeSeriesKeyvaultAccessAnomaly.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/TimeSeriesKeyvaultAccessAnomaly.yaml) |
| analytic_rule | Mass secret retrieval from Azure Key Vault | AzureDiagnostics.ResourceType =~ "VAULTS" | [KeyvaultMassSecretRetrieval.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/KeyvaultMassSecretRetrieval.yaml) |
| analytic_rule | NRT Sensitive Azure Key Vault operations | AzureDiagnostics.ResourceType =~ "VAULTS" | [NRT_KeyVaultSensitiveOperations.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/NRT_KeyVaultSensitiveOperations.yaml) |
| analytic_rule | Sensitive Azure Key Vault operations | AzureDiagnostics.ResourceType =~ "VAULTS" | [KeyVaultSensitiveOperations.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Analytic%20Rules/KeyVaultSensitiveOperations.yaml) |
| workbook | AzureKeyVaultWorkbook | AzureDiagnostics.Category == "AuditEvent"  \|  AzureDiagnostics.ResourceType =~ "VAULTS" | [AzureKeyVaultWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Workbooks/AzureKeyVaultWorkbook.json) |

### Azure SQL Database solution for sentinel

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Affected rows stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Credential errors stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-ErrorsCredentialStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsCredentialStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Drop attempts stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-HotwordsDropStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsDropStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Execution attempts stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-HotwordsExecutionStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsExecutionStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Firewall errors stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-ErrorsFirewallStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsFirewallStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Firewall rule manipulation attempts stateful anoma | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-HotwordsFirewallRuleStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsFirewallRuleStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | OLE object manipulation attempts stateful anomaly  | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-HotwordsOLEObjectStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsOLEObjectStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Outgoing connection attempts stateful anomaly on d | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-HotwordsOutgoingStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsOutgoingStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Response rows stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml) |
| analytic_rule | Syntax errors stateful anomaly on database | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [Detection-ErrorsSyntaxStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsSyntaxStatefulAnomalyOnDatabase.yaml) |
| hunting_query | Affected rows stateful anomaly on database - hunti | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml) |
| hunting_query | Anomalous Query Execution Time | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-AffectedRowAnomaly.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-AffectedRowAnomaly.yaml) |
| hunting_query | Anomalous Query Execution Time | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-ExecutionTimeAnomaly.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-ExecutionTimeAnomaly.yaml) |
| hunting_query | Boolean Blind SQL Injection | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-BooleanBlindSQLi.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-BooleanBlindSQLi.yaml) |
| hunting_query | Prevalence Based SQL Query Size Anomaly | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-PrevalenceBasedQuerySizeAnomaly.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-PrevalenceBasedQuerySizeAnomaly.yaml) |
| hunting_query | Response rows stateful anomaly on database - hunti | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml) |
| hunting_query | Suspicious SQL Stored Procedures | AzureDiagnostics.Category =~ "SQLSecurityAuditEvents" | [HuntingQuery-SuspiciousStoredProcedures.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-SuspiciousStoredProcedures.yaml) |
| hunting_query | Time Based SQL Query Size Anomaly | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [HuntingQuery-TimeBasedQuerySizeAnomaly.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-TimeBasedQuerySizeAnomaly.yaml) |
| workbook | Workbook-AzureSQLSecurity | AzureDiagnostics.Category == "SQLSecurityAuditEvents"  \|  AzureDiagnostics.ResourceType == "SERVERS/DATABASES" | [Workbook-AzureSQLSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Workbooks/Workbook-AzureSQLSecurity.json) |

### Azure Web Application Firewall (WAF)

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | AFD WAF - Code Injection | AzureDiagnostics.Category =~ "FrontDoorWebApplicationFirewallLog" | [AFD-WAF-Code-Injection.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-WAF-Code-Injection.yaml) |
| analytic_rule | AFD WAF - Path Traversal Attack | AzureDiagnostics.Category =~ "FrontDoorWebApplicationFirewallLog" | [AFD-WAF-Path-Traversal-Attack.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-WAF-Path-Traversal-Attack.yaml) |
| analytic_rule | Front Door Premium WAF - SQLi Detection | AzureDiagnostics.Category =~ "FrontDoorWebApplicationFirewallLog" | [AFD-Premium-WAF-SQLiDetection.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-Premium-WAF-SQLiDetection.yaml) |
| analytic_rule | Front Door Premium WAF - XSS Detection | AzureDiagnostics.Category =~ "FrontDoorWebApplicationFirewallLog" | [AFD-Premium-WAF-XSSDetection.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/AFD-Premium-WAF-XSSDetection.yaml) |
| workbook | WebApplicationFirewallFirewallEvents | AzureDiagnostics.ResourceType == "APPLICATIONGATEWAYS" | [WebApplicationFirewallFirewallEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallFirewallEvents.json) |
| workbook | WebApplicationFirewallGatewayAccessEvents | AzureDiagnostics.ResourceType == "APPLICATIONGATEWAYS" | [WebApplicationFirewallGatewayAccessEvents.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallGatewayAccessEvents.json) |
| workbook | WebApplicationFirewallOverview | AzureDiagnostics.ResourceType == "APPLICATIONGATEWAYS" | [WebApplicationFirewallOverview.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Workbooks/WebApplicationFirewallOverview.json) |

### Azure kubernetes Service

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| hunting_query | Azure RBAC AKS created role details | AzureDiagnostics.Category == "kube-audit" | [AKS-Rbac.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Hunting%20Queries/AKS-Rbac.yaml) |
| hunting_query | Determine users with cluster admin role | AzureDiagnostics.Category == "kube-audit" | [AKS-clusterrolebinding.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Hunting%20Queries/AKS-clusterrolebinding.yaml) |
| workbook | AksSecurity | AzureDiagnostics.Category == "kube-audit" | [AksSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Workbooks/AksSecurity.json) |

### AzureSecurityBenchmark

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | AzureSecurityBenchmark | AzureDiagnostics.Category in "All,AzureFirewallNetworkRule,NetworkSecurityGroupRuleCounter"  \|  AzureDiagnostics.ResourceType == "AZUREFIREWALLS"  \|  SecurityEvent.EventID in "2889,3000,4624,4768,4769,4776" | [AzureSecurityBenchmark.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json) |

### Barracuda CloudGen Firewall

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | Barracuda | CommonSecurityLog.DeviceVendor == "Barracuda" | [Barracuda.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Barracuda%20CloudGen%20Firewall/Workbooks/Barracuda.json) |

### CTERA

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Antivirus Detected an Infected File | Syslog.SyslogMessage contains "found an infected file" | [InfectedFileDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/InfectedFileDetected.yaml) |
| analytic_rule | CTERA Mass Access Denied Detection Analytic | Syslog.ProcessName == "gw-audit" | [MassAccessDenied.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/MassAccessDenied.yaml) |
| analytic_rule | CTERA Mass Deletions Detection Analytic | Syslog.ProcessName == "gw-audit" | [MassDeletions.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/MassDeletions.yaml) |
| analytic_rule | CTERA Mass Permissions Changes Detection Analytic | Syslog.ProcessName == "gw-audit" | [MassPermissionChanges.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/MassPermissionChanges.yaml) |
| analytic_rule | Ransom Protect Detected a Ransomware Attack | Syslog.SyslogMessage contains "Ransomware incident detected" | [RansomwareDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/RansomwareDetected.yaml) |
| analytic_rule | Ransom Protect User Blocked | Syslog.SyslogMessage contains "Ransom Protect mechanism blocked" | [RansomwareUserBlocked.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Analytic%20Rules/RansomwareUserBlocked.yaml) |
| hunting_query | CTERA Batch Access Denied Detection | Syslog.ProcessName == "gw-audit" | [AccessDenied.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Hunting%20Queries/AccessDenied.yaml) |
| hunting_query | CTERA Batch File Deletions Detection | Syslog.ProcessName == "gw-audit" | [BatchDeletions.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Hunting%20Queries/BatchDeletions.yaml) |
| hunting_query | CTERA Permission Change Detection | Syslog.ProcessName == "gw-audit" | [BatchPermissionChanges.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Hunting%20Queries/BatchPermissionChanges.yaml) |
| workbook | CTERA_Workbook | Syslog.ProcessName == "gw-audit"  \|  Syslog.SyslogMessage contains "ctera_audit"  \|  Syslog.SyslogMessage contains "op=delete" | [CTERA_Workbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Workbooks/CTERA_Workbook.json) |

### Check Point

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | CheckPoint | CommonSecurityLog.DeviceProduct in~ "Anti Malware,Anti-Bot,Anti-Virus,Application Control,DDoS Protector,IPS,Threat Emulation,URL Filtering"  \|  CommonSecurityLog.DeviceVendor == "Check Point" | [CheckPoint.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Check%20Point/Workbooks/CheckPoint.json) |

### CiscoASA

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | Cisco | CommonSecurityLog.DeviceProduct =~ "ASA"  \|  CommonSecurityLog.DeviceVendor =~ "Cisco" | [Cisco.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoASA/Workbooks/Cisco.json) |

### Citrix Web App Firewall

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | CitrixWAF | CommonSecurityLog.DeviceProduct == "NetScaler"  \|  CommonSecurityLog.DeviceVendor == "Citrix" | [CitrixWAF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Web%20App%20Firewall/Workbooks/CitrixWAF.json) |

### Cloud Service Threat Protection Essentials

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| hunting_query | Azure Key Vault Access Policy Manipulation | AzureDiagnostics.ResourceType =~ "VAULTS" | [AzureKeyVaultAccessManipulation.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Service%20Threat%20Protection%20Essentials/Hunting%20Queries/AzureKeyVaultAccessManipulation.yaml) |

### Common Event Format

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | CEFOverviewWorkbook | CommonSecurityLog.DeviceProduct has "PAN-OS" | [CEFOverviewWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format/Workbooks/CEFOverviewWorkbook.json) |

### ContinuousDiagnostics&Mitigation

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | ContinuousDiagnostics&Mitigation | AzureDiagnostics.Category in "NetworkSecurityGroupEvent,kube-audit"  \|  AzureDiagnostics.Category contains "SQL"  \|  AzureDiagnostics.ResourceType in "APPLICATIONGATEWAYS,AZUREFIREWALLS,CDNWEBAPPLICATIONFIREWALLPOLICIES,FRONTDOORS,PROFILES,PUBLICIPADDRESSES" | [ContinuousDiagnostics&Mitigation.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json) |

### Contrast Protect

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Contrast Blocks | CommonSecurityLog.DeviceVendor == "Contrast Security" | [ContrastBlocks.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastBlocks.yaml) |
| analytic_rule | Contrast Exploits | CommonSecurityLog.DeviceVendor == "Contrast Security" | [ContrastExploits.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastExploits.yaml) |
| analytic_rule | Contrast Probes | CommonSecurityLog.DeviceVendor == "Contrast Security" | [ContrastProbes.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastProbes.yaml) |
| analytic_rule | Contrast Suspicious | CommonSecurityLog.DeviceVendor == "Contrast Security" | [ContrastSuspicious.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Analytic%20Rules/ContrastSuspicious.yaml) |
| workbook | ContrastProtect | CommonSecurityLog.DeviceVendor == "Contrast Security" | [ContrastProtect.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Workbooks/ContrastProtect.json) |

### CyberArk Privilege Access Manager (PAM) Events

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | CyberArkEPV | CommonSecurityLog.DeviceProduct == "Vault"  \|  CommonSecurityLog.DeviceVendor == "Cyber-Ark" | [CyberArkEPV.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Workbooks/CyberArkEPV.json) |

### CybersecurityMaturityModelCertification(CMMC)2.0

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | CybersecurityMaturityModelCertification_CMMCV2 | AzureDiagnostics.Category == "AzureFirewallApplicationRule" | [CybersecurityMaturityModelCertification_CMMCV2.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json) |

### Cyborg Security HUNTER

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| hunting_query | Metasploit / Impacket PsExec Process Creation Acti | SecurityEvent.EventID == "4688" | [Metasploit Impacket PsExec Process Creation Activity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Metasploit%20Impacket%20PsExec%20Process%20Creation%20Activity.yaml) |

### DORA Compliance

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | DORACompliance | Event.EventID in "1001,1069,1205" | [DORACompliance.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance/Workbooks/DORACompliance.json) |

### Delinea Secret Server

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | DelineaWorkbook | CommonSecurityLog.DeviceProduct == "Secret Server"  \|  CommonSecurityLog.DeviceVendor in "Delinea Software,Thycotic Software" | [DelineaWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Delinea%20Secret%20Server/Workbooks/DelineaWorkbook.json) |

### EatonForeseer

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | EatonForeseer - Unauthorized Logins | SecurityEvent.EventID in "4624,4625,4634,4647,4648,4675" | [EatonUnautorizedLogins.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer/Analytic%20Rules/EatonUnautorizedLogins.yaml) |
| workbook | EatonForeseerHealthAndAccess | SecurityEvent.EventID in "4624,4625,4634,4647,4648,4675" | [EatonForeseerHealthAndAccess.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer/Workbooks/EatonForeseerHealthAndAccess.json) |

### Endpoint Threat Protection Essentials

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Detecting Macro Invoking ShellBrowserWindow COM Ob | Event.EventID == "1" | [MacroInvokingShellBrowserWindowCOMObjects.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/MacroInvokingShellBrowserWindowCOMObjects.yaml) |
| analytic_rule | Dumping LSASS Process Into a File | Event.EventID == "10" | [DumpingLSASSProcessIntoaFile.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/DumpingLSASSProcessIntoaFile.yaml) |
| analytic_rule | Lateral Movement via DCOM | Event.EventID == "1" | [LateralMovementViaDCOM.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/LateralMovementViaDCOM.yaml) |
| analytic_rule | Potential Remote Desktop Tunneling | SecurityEvent.EventID in "4624,4625" | [PotentialRemoteDesktopTunneling.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/PotentialRemoteDesktopTunneling.yaml) |
| analytic_rule | Registry Persistence via AppCert DLL Modification | Event.EventID == "13" | [RegistryPersistenceViaAppCertDLLModification.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/RegistryPersistenceViaAppCertDLLModification.yaml) |
| analytic_rule | Registry Persistence via AppInit DLLs Modification | Event.EventID == "13" | [RegistryPersistenceViaAppInt_DLLsModification.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/RegistryPersistenceViaAppInt_DLLsModification.yaml) |
| analytic_rule | Security Event log cleared | WindowsEvent.EventID == "1102"  \|  WindowsEvent.Provider =~ "Microsoft-Windows-Eventlog" | [SecurityEventLogCleared.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/SecurityEventLogCleared.yaml) |
| analytic_rule | WDigest downgrade attack | Event.EventID == "13" | [WDigestDowngradeAttack.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WDigestDowngradeAttack.yaml) |
| analytic_rule | Windows Binaries Executed from Non-Default Directo | SecurityEvent.EventID == "4688" | [WindowsBinariesExecutedfromNon-DefaultDirectory.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WindowsBinariesExecutedfromNon-DefaultDirectory.yaml) |
| analytic_rule | Windows Binaries Lolbins Renamed | Event.EventID == "1" | [WindowsBinariesLolbinsRenamed.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WindowsBinariesLolbinsRenamed.yaml) |
| hunting_query | Detect Certutil (LOLBins and LOLScripts) Usage | Event.EventID == "1"  \|  Event.Source =~ "Microsoft-Windows-Sysmon" | [Certutil-LOLBins.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/Certutil-LOLBins.yaml) |
| hunting_query | Execution of File with One Character in the Name | Event.EventID == "1" | [FileExecutionWithOneCharacterInTheName.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/FileExecutionWithOneCharacterInTheName.yaml) |
| hunting_query | Persisting via IFEO Registry Key | Event.Source =~ "Microsoft-Windows-Sysmon"  \|  WindowsEvent.EventID in "12,13,4657" | [PersistViaIFEORegistryKey.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/PersistViaIFEORegistryKey.yaml) |
| hunting_query | Potential Microsoft Security Services Tampering | Event.Source =~ "Microsoft-Windows-SENSE"  \|  WindowsEvent.EventID in "4688,87" | [PotentialMicrosoftSecurityServicesTampering.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/PotentialMicrosoftSecurityServicesTampering.yaml) |
| hunting_query | Rare Windows Firewall Rule updates using Netsh | Event.Source == "Microsoft-Windows-Sysmon"  \|  SecurityEvent.EventID == "1" | [WindowsFirewallUpdateUsingNetsh.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/WindowsFirewallUpdateUsingNetsh.yaml) |
| hunting_query | Remote Login Performed with WMI | SecurityEvent.EventID in "4624,4625" | [RemoteLoginPerformedwithWMI.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/RemoteLoginPerformedwithWMI.yaml) |
| hunting_query | Remote Scheduled Task Creation or Update using ATS | SecurityEvent.EventID == "5145" | [RemoteScheduledTaskCreationUpdateUsingATSVCNamedPipe.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/RemoteScheduledTaskCreationUpdateUsingATSVCNamedPipe.yaml) |
| hunting_query | Rundll32 (LOLBins and LOLScripts) | Event.EventID == "1"  \|  Event.Source =~ "Microsoft-Windows-Sysmon" | [SignedBinaryProxyExecutionRundll32.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/SignedBinaryProxyExecutionRundll32.yaml) |
| hunting_query | Scheduled Task Creation or Update from User Writab | SecurityEvent.EventID in "4698,4702" | [ScheduledTaskCreationUpdateFromUserWritableDrectory.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ScheduledTaskCreationUpdateFromUserWritableDrectory.yaml) |

### ExtraHop Reveal(x)

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | ExtraHopDetectionSummary | CommonSecurityLog.DeviceVendor == "ExtraHop" | [ExtraHopDetectionSummary.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop%20Reveal%28x%29/Workbooks/ExtraHopDetectionSummary.json) |

### FalconFriday

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Beacon Traffic Based on Common User Agents Visitin | CommonSecurityLog.DeviceProduct == "NSSWeblog"  \|  CommonSecurityLog.DeviceVendor == "Zscaler" | [RecognizingBeaconingTraffic.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/RecognizingBeaconingTraffic.yaml) |
| analytic_rule | Certified Pre-Owned - TGTs requested with certific | SecurityEvent.EventID == "4768" | [CertifiedPreOwned-TGTs-requested.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-TGTs-requested.yaml) |
| analytic_rule | Certified Pre-Owned - backup of CA private key - r | SecurityEvent.EventID == "5058" | [CertifiedPreOwned-backup-key-1.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-backup-key-1.yaml) |
| analytic_rule | Certified Pre-Owned - backup of CA private key - r | SecurityEvent.EventID == "5059" | [CertifiedPreOwned-backup-key-2.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-backup-key-2.yaml) |
| analytic_rule | Excessive share permissions | SecurityEvent.EventID == "5143" | [ExcessiveSharePermissions.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/ExcessiveSharePermissions.yaml) |

### Forcepoint CASB

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | ForcepointCASB | CommonSecurityLog.DeviceProduct in "CASB Admin audit log,Cloud Service Monitoring,SaaS Security Gateway"  \|  CommonSecurityLog.DeviceVendor == "Forcepoint CASB" | [ForcepointCASB.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CASB/Workbooks/ForcepointCASB.json) |

### Forcepoint CSG

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | ForcepointCloudSecuirtyGateway | CommonSecurityLog.DeviceProduct in "Email,Web"  \|  CommonSecurityLog.DeviceVendor == "Forcepoint CSG" | [ForcepointCloudSecuirtyGateway.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20CSG/Workbooks/ForcepointCloudSecuirtyGateway.json) |

### Forcepoint NGFW

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | ForcepointNGFW | CommonSecurityLog.DeviceProduct == "NGFW"  \|  CommonSecurityLog.DeviceVendor == "Forcepoint" | [ForcepointNGFW.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Workbooks/ForcepointNGFW.json) |
| workbook | ForcepointNGFWAdvanced | CommonSecurityLog.DeviceProduct in "Alert,Audit"  \|  CommonSecurityLog.DeviceVendor in~ "FORCEPOINT,Forcepoint" | [ForcepointNGFWAdvanced.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Forcepoint%20NGFW/Workbooks/ForcepointNGFWAdvanced.json) |

### Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | Fortigate | CommonSecurityLog.DeviceProduct contains "Fortigate"  \|  CommonSecurityLog.DeviceVendor =~ "Fortinet" | [Fortigate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiGate%20Next-Generation%20Firewall%20connector%20for%20Microsoft%20Sentinel/Workbooks/Fortigate.json) |

### GDPR Compliance & Data Security

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | GDPRComplianceAndDataSecurity | AzureDiagnostics.Category == "SQLSecurityAuditEvents"  \|  AzureDiagnostics.ResourceType == "SERVERS/DATABASES" | [GDPRComplianceAndDataSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json) |

### HIPAA Compliance

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | HIPAACompliance | AzureDiagnostics.Category == "AzureFirewallNetworkRule"  \|  AzureDiagnostics.Category =~ "SQLSecurityAuditEvents"  \|  SecurityEvent.EventID in "4624,4625" | [HIPAACompliance.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance/Workbooks/HIPAACompliance.json) |

### IllumioSaaS

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | IllumioOnPremHealth | Syslog.SyslogMessage has "disk=Policy"  \|  Syslog.SyslogMessage has "disk=Traffic"  \|  Syslog.SyslogMessage has "illumio_pce/system_health"  \|  Syslog.SyslogMessage has "src=collector"  \|  Syslog.SyslogMessage has "src=disk_latency"  \|  Syslog.SyslogMessage has "src=flow_analytics" | [IllumioOnPremHealth.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Workbooks/IllumioOnPremHealth.json) |

### Illusive Platform

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Illusive Incidents Analytic Rule | CommonSecurityLog.DeviceProduct == "illusive" | [Illusive_Detection_Query.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Platform/Analytic%20Rules/Illusive_Detection_Query.yaml) |

### Infoblox

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | Infoblox_Workbook | CommonSecurityLog.DeviceProduct == "Data Connector"  \|  CommonSecurityLog.DeviceVendor == "Infoblox" | [Infoblox_Workbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Workbooks/Infoblox_Workbook.json) |

### IronNet IronDefense

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Create Incidents from IronDefense | CommonSecurityLog.DeviceProduct == "IronDefense" | [IronDefense_Detection_Query.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Analytic%20Rules/IronDefense_Detection_Query.yaml) |
| workbook | IronDefenseAlertDetails | CommonSecurityLog.DeviceProduct == "IronDefense" | [IronDefenseAlertDetails.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Workbooks/IronDefenseAlertDetails.json) |

### Legacy IOC based Threat Protection

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| hunting_query | Connection from external IP to OMI related Ports | AzureDiagnostics.Category == "AzureFirewallNetworkRule" | [NetworkConnectiontoOMIPorts.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/NetworkConnectiontoOMIPorts.yaml) |
| hunting_query | Known Nylon Typhoon Registry modifications pattern | Event.Source == "Microsoft-Windows-Sysmon"  \|  WindowsEvent.EventID in "12,13,4657" | [NylonTyphoonRegIOCPatterns.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/NylonTyphoonRegIOCPatterns.yaml) |
| hunting_query | SolarWinds Inventory | Event.Source == "Microsoft-Windows-Sysmon"  \|  WindowsEvent.EventID in "1,4688" | [SolarWindsInventory.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/SolarWindsInventory.yaml) |

### MaturityModelForEventLogManagementM2131

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | MaturityModelForEventLogManagement_M2131 | AzureDiagnostics.Category in "AzureFirewallApplicationRule,AzureFirewallNetworkRule,EntitlementManagement,FrontdoorWebApplicationFirewallLog,GatewayDiagnosticLog,GroupManagement,IKEDiagnosticLog,NetworkSecurityGroupEvent,RouteDiagnosticLog,TunnelDiagnosticLog,UserManagement,WebApplicationFirewallLogs,kube-audit"  \|  AzureDiagnostics.Category contains "SQL"  \|  AzureDiagnostics.ResourceType in "APPLICATIONGATEWAYS,AZUREFIREWALLS,CDNWEBAPPLICATIONFIREWALLPOLICIES,FRONTDOORS,PROFILES,PUBLICIPADDRESSES,SERVERS/DATABASES"  \|  Syslog.SyslogMessage contains "runas"  \|  Syslog.SyslogMessage contains "sudo" | [MaturityModelForEventLogManagement_M2131.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json) |

### Microsoft Exchange Security - Exchange On-Premises

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | Microsoft Exchange Admin Activity | SecurityEvent.EventID in "4624,4720,4722,4724,4725,4726,7036" | [Microsoft Exchange Admin Activity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Workbooks/Microsoft%20Exchange%20Admin%20Activity.json) |

### MicrosoftPurviewInsiderRiskManagement

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | InsiderRiskManagement | SecurityEvent.EventID in "4723,4724"  \|  Syslog.Facility in "auth,authpriv" | [InsiderRiskManagement.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json) |

### NISTSP80053

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | NISTSP80053 | AzureDiagnostics.Category in "NetworkSecurityGroupEvent,kube-audit"  \|  AzureDiagnostics.Category contains "SQL"  \|  AzureDiagnostics.ResourceType in "APPLICATIONGATEWAYS,AZUREFIREWALLS,CDNWEBAPPLICATIONFIREWALLPOLICIES,FRONTDOORS,PROFILES,PUBLICIPADDRESSES" | [NISTSP80053.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json) |

### Nasuni

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Ransomware Attack Detected | Syslog.SyslogMessage has "The Filer has detected a new ransomware attack" | [RansomwareAttackDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni/Analytic%20Rules/RansomwareAttackDetected.yaml) |
| analytic_rule | Ransomware Client Blocked | Syslog.SyslogMessage has "The Filer has enforced the mitigation policy on volume" | [RansomwareClientBlocked.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni/Analytic%20Rules/RansomwareClientBlocked.yaml) |
| hunting_query | Nasuni File Delete Activity | Syslog.SyslogMessage matchesregex "(nasuni.)([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{1})" | [FileDeleteEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni/Hunting%20Queries/FileDeleteEvents.yaml) |

### Network Threat Protection Essentials

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Network endpoint to host executable correlation | CommonSecurityLog.DeviceVendor =~ "Trend Micro" | [NetworkEndpointCorrelation.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Threat%20Protection%20Essentials/Analytic%20Rules/NetworkEndpointCorrelation.yaml) |

### Onapsis Platform

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | OnapsisAlarmsOverview | CommonSecurityLog.DeviceVendor == "Onapsis" | [OnapsisAlarmsOverview.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform/Workbooks/OnapsisAlarmsOverview.json) |

### OneIdentity

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | OneIdentity | CommonSecurityLog.DeviceProduct == "SPS"  \|  CommonSecurityLog.DeviceVendor == "OneIdentity" | [OneIdentity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OneIdentity/Workbooks/OneIdentity.json) |

### Palo Alto - XDR (Cortex)

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | PaloAltoXDR | CommonSecurityLog.DeviceProduct == "Cortex XDR"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [PaloAltoXDR.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29/Workbooks/PaloAltoXDR.json) |

### PaloAlto-PAN-OS

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Palo Alto - potential beaconing detected | CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [PaloAlto-NetworkBeaconing.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/PaloAlto-NetworkBeaconing.yaml) |
| analytic_rule | Palo Alto Threat signatures from Unusual IP addres | CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [PaloAlto-UnusualThreatSignatures.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Analytic%20Rules/PaloAlto-UnusualThreatSignatures.yaml) |
| hunting_query | Palo Alto - high-risk ports | CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [PaloAlto-HighRiskPorts.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Hunting%20Queries/PaloAlto-HighRiskPorts.yaml) |
| hunting_query | Palo Alto - potential beaconing detected | CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Palo Alto - potential beaconing detected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Hunting%20Queries/Palo%20Alto%20-%20potential%20beaconing%20detected.yaml) |
| workbook | PaloAltoNetworkThreat | CommonSecurityLog.DeviceProduct has "PAN-OS"  \|  CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [PaloAltoNetworkThreat.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Workbooks/PaloAltoNetworkThreat.json) |
| workbook | PaloAltoOverview | CommonSecurityLog.DeviceProduct has "LF"  \|  CommonSecurityLog.DeviceProduct has "PAN-OS"  \|  CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [PaloAltoOverview.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAlto-PAN-OS/Workbooks/PaloAltoOverview.json) |

### PingFederate

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | PingFederate | CommonSecurityLog.DeviceProduct =~ "PingFederate" | [PingFederate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Workbooks/PingFederate.json) |

### Pure Storage

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | External Fabric Module XFM1 is unhealthy | Syslog.SyslogMessage has "purity.alert" | [FB-FabricModuleUnhealthy.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Analytic%20Rules/FB-FabricModuleUnhealthy.yaml) |
| analytic_rule | Pure Controller Failed | Syslog.SyslogMessage has "purity.alert" | [PureControllerFailed.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Analytic%20Rules/PureControllerFailed.yaml) |
| analytic_rule | Pure Failed Login | Syslog.SyslogMessage has "invalid username or password"  \|  Syslog.SyslogMessage has "purity.alert" | [PureFailedLogin.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Analytic%20Rules/PureFailedLogin.yaml) |

### Radiflow

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Radiflow - Exploit Detected | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowExploitDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowExploitDetected.yaml) |
| analytic_rule | Radiflow - Network Scanning Detected | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowNetworkScanningDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowNetworkScanningDetected.yaml) |
| analytic_rule | Radiflow - New Activity Detected | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowNewActivityDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowNewActivityDetected.yaml) |
| analytic_rule | Radiflow - Platform Alert | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowPlatformAlert.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowPlatformAlert.yaml) |
| analytic_rule | Radiflow - Policy Violation Detected | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowPolicyViolationDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowPolicyViolationDetected.yaml) |
| analytic_rule | Radiflow - Suspicious Malicious Activity Detected | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowSuspiciousMaliciousActivityDetected.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowSuspiciousMaliciousActivityDetected.yaml) |
| analytic_rule | Radiflow - Unauthorized Command in Operational Dev | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowUnauthorizedCommandinOperationalDevice.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowUnauthorizedCommandinOperationalDevice.yaml) |
| analytic_rule | Radiflow - Unauthorized Internet Access | CommonSecurityLog.DeviceProduct =~ "iSID" | [RadiflowUnauthorizedInternetAccess.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Radiflow/Analytic%20Rules/RadiflowUnauthorizedInternetAccess.yaml) |

### RidgeSecurity

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Critical Risks | CommonSecurityLog.DeviceVendor == "RidgeSecurity" | [RidgeSecurity_Risks.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RidgeSecurity/Analytic%20Rules/RidgeSecurity_Risks.yaml) |
| analytic_rule | Vulerabilities | CommonSecurityLog.DeviceVendor == "RidgeSecurity" | [RidgeSecurity_Vulnerabilities.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RidgeSecurity/Analytic%20Rules/RidgeSecurity_Vulnerabilities.yaml) |

### SOC Handbook

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | InvestigationInsights | SecurityEvent.EventID in "1102,4624,4625,4688,4719,4720,4723,4724,4768,4771,4776" | [InvestigationInsights.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json) |

### SOX IT Compliance

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | SOXITCompliance | CommonSecurityLog.DeviceVendor has_any "CrowdStrike,Microsoft,Qualys,Tripwire"  \|  SecurityEvent.EventID in "1100,1102,1104,1240,1241,1242,4656,4657,4660,4663,4670,4688,4719,4720,4726,4732,4739,4754,4907"  \|  Syslog.SyslogMessage has_any "ALTER TABLE,CREATE TABLE,DROP TABLE,database modified,schema change"  \|  Syslog.SyslogMessage has_any "auditd stopped,logging stopped,rsyslog stopped,syslog stopped"  \|  Syslog.SyslogMessage has_any "change,config,edit,modified,updated"  \|  Syslog.SyslogMessage has_any "change,config,modified,registry,updated"  \|  Syslog.SyslogMessage has_any "checksum mismatch,file deleted,file modified,file tamper" | [SOXITCompliance.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json) |

### Semperis Directory Services Protector

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Semperis DSP Failed Logons | SecurityEvent.EventID == "20002" | [Semperis_DSP_Failed_Logons.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_Failed_Logons.yaml) |
| analytic_rule | Semperis DSP Operations Critical Notifications | SecurityEvent.EventID == "30001" | [Semperis_DSP_Operations_Critical_Notifications_.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_Operations_Critical_Notifications_.yaml) |
| analytic_rule | Semperis DSP RBAC Changes | SecurityEvent.EventID == "20012" | [Semperis_DSP_RBAC_Changes.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_RBAC_Changes.yaml) |
| workbook | SemperisDSPNotifications | CommonSecurityLog.DeviceProduct == "Core Directory" | [SemperisDSPNotifications.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPNotifications.json) |
| workbook | SemperisDSPQuickviewDashboard | CommonSecurityLog.DeviceProduct == "Core Directory"  \|  SecurityEvent.EventID in "20000,20002,20012,9208,9211,9212" | [SemperisDSPQuickviewDashboard.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPQuickviewDashboard.json) |

### Silverfort

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Silverfort - Certifried Incident | CommonSecurityLog.DeviceProduct has "Admin Console"  \|  CommonSecurityLog.DeviceVendor has "Silverfort" | [Certifried.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/Certifried.yaml) |
| analytic_rule | Silverfort - Log4Shell Incident | CommonSecurityLog.DeviceProduct has "Admin Console"  \|  CommonSecurityLog.DeviceVendor has "Silverfort" | [Log4Shell.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/Log4Shell.yaml) |
| analytic_rule | Silverfort - NoPacBreach Incident | CommonSecurityLog.DeviceProduct has "Admin Console"  \|  CommonSecurityLog.DeviceVendor has "Silverfort" | [NoPac_Breach.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/NoPac_Breach.yaml) |
| analytic_rule | Silverfort - UserBruteForce Incident | CommonSecurityLog.DeviceProduct has "Admin Console"  \|  CommonSecurityLog.DeviceVendor has "Silverfort" | [User_Brute_Force.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Analytic%20Rules/User_Brute_Force.yaml) |
| workbook | SilverfortWorkbook | CommonSecurityLog.DeviceProduct has "Admin Console"  \|  CommonSecurityLog.DeviceVendor has "Silverfort" | [SilverfortWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Silverfort/Workbooks/SilverfortWorkbook.json) |

### SonicWall Firewall

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | SonicWallFirewall | CommonSecurityLog.DeviceVendor == "SonicWall" | [SonicWallFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonicWall%20Firewall/Workbooks/SonicWallFirewall.json) |

### Syslog

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Failed logon attempts in authpriv | Syslog.Facility =~ "authpriv"  \|  Syslog.SyslogMessage has "authentication failure"  \|  Syslog.SyslogMessage has "uid=0"  \|  Syslog.SyslogMessage has "user unknown" | [FailedLogonAttempts_UnknownUser.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/FailedLogonAttempts_UnknownUser.yaml) |
| analytic_rule | NRT Squid proxy events related to mining pools | Syslog.ProcessName contains "squid" | [NRT_squid_events_for_mining_pools.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/NRT_squid_events_for_mining_pools.yaml) |
| analytic_rule | SFTP File transfer above threshold | Syslog.ProcessName has "sftp"  \|  Syslog.SyslogMessage has "bytes read"  \|  Syslog.SyslogMessage has "close"  \|  Syslog.SyslogMessage has "session opened for" | [sftp_file_transfer_above_threshold.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/sftp_file_transfer_above_threshold.yaml) |
| analytic_rule | SFTP File transfer folder count above threshold | Syslog.ProcessName has "sftp"  \|  Syslog.SyslogMessage has "bytes read"  \|  Syslog.SyslogMessage has "close"  \|  Syslog.SyslogMessage has "session opened for" | [sftp_file_transfer_folders_above_threshold.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/sftp_file_transfer_folders_above_threshold.yaml) |
| analytic_rule | SSH - Potential Brute Force | Syslog.ProcessName =~ "sshd"  \|  Syslog.SyslogMessage contains "Failed password for invalid user" | [ssh_potentialBruteForce.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/ssh_potentialBruteForce.yaml) |
| analytic_rule | Squid proxy events for ToR proxies | Syslog.ProcessName contains "squid" | [squid_tor_proxies.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/squid_tor_proxies.yaml) |
| analytic_rule | Squid proxy events related to mining pools | Syslog.ProcessName contains "squid" | [squid_cryptomining_pools.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Analytic%20Rules/squid_cryptomining_pools.yaml) |
| hunting_query | Editing Linux scheduled tasks through Crontab | Syslog.Facility =~ "cron"  \|  Syslog.ProcessName =~ "crontab" | [SchedTaskEditViaCrontab.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/SchedTaskEditViaCrontab.yaml) |
| hunting_query | SCX Execute RunAs Providers | Syslog.SyslogMessage has "AUOMS_EXECVE" | [SCXExecuteRunAsProviders.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/SCXExecuteRunAsProviders.yaml) |
| hunting_query | Squid commonly abused TLDs | Syslog.ProcessName contains "squid" | [squid_abused_tlds.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/squid_abused_tlds.yaml) |
| hunting_query | Squid data volume timeseries anomalies | Syslog.ProcessName contains "squid" | [squid_volume_anomalies.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/squid_volume_anomalies.yaml) |
| hunting_query | Squid malformed requests | Syslog.ProcessName contains "squid" | [squid_malformed_requests.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/squid_malformed_requests.yaml) |
| hunting_query | Suspicious crytocurrency mining related threat act | Syslog.Facility == "user"  \|  Syslog.SyslogMessage has "AUOMS_EXECVE" | [CryptoThreatActivity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Syslog/Hunting%20Queries/CryptoThreatActivity.yaml) |

### Threat Intelligence

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | TI Map IP Entity to Azure SQL Security Audit Event | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [IPEntity_AzureSQL.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureSQL.yaml) |
| analytic_rule | TI Map URL Entity to PaloAlto Data | CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [URLEntity_PaloAlto.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_PaloAlto.yaml) |
| analytic_rule | TI map Domain entity to PaloAlto | CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [DomainEntity_PaloAlto.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_PaloAlto.yaml) |
| analytic_rule | TI map Email entity to PaloAlto CommonSecurityLog | CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [EmailEntity_PaloAlto.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_PaloAlto.yaml) |
| analytic_rule | TI map IP entity to Azure Key Vault logs | AzureDiagnostics.ResourceType =~ "VAULTS" | [IPEntity_AzureKeyVault.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AzureKeyVault.yaml) |
| analytic_rule | TI map IP entity to Workday(ASimAuditEventLogs) | ASimAuditEventLogs.EventVendor == "Workday" | [IPEntity_Workday.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_Workday.yaml) |
| hunting_query | TI Map File Entity to Security Event | SecurityEvent.EventID in "4648,4673,4688,8002" | [FileEntity_SecurityEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_SecurityEvent.yaml) |

### Threat Intelligence (NEW)

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | TI Map IP Entity to Azure SQL Security Audit Event | AzureDiagnostics.Category == "SQLSecurityAuditEvents" | [IPEntity_AzureSQL.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureSQL.yaml) |
| analytic_rule | TI Map URL Entity to PaloAlto Data | CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [URLEntity_PaloAlto.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_PaloAlto.yaml) |
| analytic_rule | TI map Domain entity to PaloAlto | CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks" | [DomainEntity_PaloAlto.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_PaloAlto.yaml) |
| analytic_rule | TI map Email entity to PaloAlto CommonSecurityLog | CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [EmailEntity_PaloAlto.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_PaloAlto.yaml) |
| analytic_rule | TI map IP entity to Azure Key Vault logs | AzureDiagnostics.ResourceType =~ "VAULTS" | [IPEntity_AzureKeyVault.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AzureKeyVault.yaml) |
| analytic_rule | TI map IP entity to Workday(ASimAuditEventLogs) | ASimAuditEventLogs.EventVendor == "Workday" | [IPEntity_Workday_Updated.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_Workday_Updated.yaml) |
| hunting_query | TI Map File Entity to Security Event | SecurityEvent.EventID in "4648,4673,4688,8002" | [FileEntity_SecurityEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_SecurityEvent.yaml) |

### ThreatAnalysis&Response

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | DynamicThreatModeling&Response | AzureDiagnostics.ResourceType == "PUBLICIPADDRESSES" | [DynamicThreatModeling&Response.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/DynamicThreatModeling%26Response.json) |

### VMware SASE

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | VMware SD-WAN Edge - IDS/IPS Alert triggered (Sysl | Syslog.SyslogMessage contains "VCF Alert" | [vmw-sdwan-idps-alert-syslog.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-idps-alert-syslog.yaml) |
| analytic_rule | VMware SD-WAN Edge - Network Anomaly Detection - P | Syslog.SyslogMessage contains "VCF Drop"  \|  Syslog.SyslogMessage contains "packet too big" | [vmw-sdwan-ipfrag-attempt.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-ipfrag-attempt.yaml) |
| analytic_rule | VMware SD-WAN Edge - Network Anomaly Detection - R | Syslog.SyslogMessage contains "Reverse path forwarding check fail"  \|  Syslog.SyslogMessage contains "VCF Drop" | [vmw-sdwan-rpfcheck.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-rpfcheck.yaml) |
| workbook | VMwareSASESOCDashboard | Syslog.SyslogMessage contains "ACTION=VCF"  \|  Syslog.SyslogMessage contains "VCF Alert" | [VMwareSASESOCDashboard.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Workbooks/VMwareSASESOCDashboard.json) |

### Vectra AI Detect

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Vectra AI Detect - Detections with High Severity | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-HighSeverityDetection-by-Tactics.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-HighSeverityDetection-by-Tactics.yaml) |
| analytic_rule | Vectra AI Detect - New Campaign Detected | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-NewCampaign.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-NewCampaign.yaml) |
| analytic_rule | Vectra AI Detect - Suspected Compromised Account | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-Account-by-Severity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Account-by-Severity.yaml) |
| analytic_rule | Vectra AI Detect - Suspected Compromised Host | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-Host-by-Severity.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Host-by-Severity.yaml) |
| analytic_rule | Vectra AI Detect - Suspicious Behaviors by Categor | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-Suspected-Behavior-by-Tactics.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Suspected-Behavior-by-Tactics.yaml) |
| analytic_rule | Vectra Account's Behaviors | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-Account-Detections.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Account-Detections.yaml) |
| analytic_rule | Vectra Host's Behaviors | CommonSecurityLog.DeviceProduct == "X Series"  \|  CommonSecurityLog.DeviceVendor == "Vectra Networks" | [VectraDetect-Host-Detections.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Analytic%20Rules/VectraDetect-Host-Detections.yaml) |
| workbook | AIVectraDetectWorkbook | CommonSecurityLog.DeviceVendor == "Vectra Networks" | [AIVectraDetectWorkbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Detect/Workbooks/AIVectraDetectWorkbook.json) |

### Veeam

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | VeeamSecurityActivities | Syslog.SyslogMessage has "instanceId"  \|  Syslog.SyslogMessage has "predefined_alarm_id" | [VeeamSecurityActivities.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Workbooks/VeeamSecurityActivities.json) |

### Web Shells Threat Protection

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Identify SysAid Server web shell creation | SecurityEvent.EventID in "4663,4688" | [PotentialMercury_Webshell.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/PotentialMercury_Webshell.yaml) |
| hunting_query | Possible Webshell usage attempt related to SpringS | AzureDiagnostics.Category in "ApplicationGatewayAccessLog,ApplicationGatewayFirewallLog,FrontdoorAccessLog,FrontdoorWebApplicationFirewallLog" | [SpringshellWebshellUsage.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/SpringshellWebshellUsage.yaml) |

### Windows Firewall

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | WindowsFirewall | SecurityEvent.EventID in "4624,4625" | [WindowsFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Workbooks/WindowsFirewall.json) |

### Windows Forwarded Events

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Caramel Tsunami Actor IOC - July 2021 | WindowsEvent.EventID == "4688" | [CaramelTsunami_IOC_WindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/CaramelTsunami_IOC_WindowsEvent.yaml) |
| analytic_rule | Chia_Crypto_Mining IOC - June 2021 | WindowsEvent.EventID == "4688" | [ChiaCryptoMining_WindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/ChiaCryptoMining_WindowsEvent.yaml) |
| analytic_rule | Progress MOVEIt File transfer above threshold | Event.EventID == "0"  \|  Event.Source == "MOVEit DMZ Audit" | [moveit_file_transfer_above_threshold.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/moveit_file_transfer_above_threshold.yaml) |
| analytic_rule | Progress MOVEIt File transfer folder count above t | Event.EventID == "0"  \|  Event.Source == "MOVEit DMZ Audit" | [moveit_file_transfer_folders_above_threshold.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Forwarded%20Events/Analytic%20Rules/moveit_file_transfer_folders_above_threshold.yaml) |

### Windows Security Events

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | AD FS Remote Auth Sync Connection | SecurityEvent.EventID in "412,501,5156" | [ADFSRemoteAuthSyncConnection.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSRemoteAuthSyncConnection.yaml) |
| analytic_rule | AD FS Remote HTTP Network Connection | Event.EventID in "18,3"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [ADFSRemoteHTTPNetworkConnection.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSRemoteHTTPNetworkConnection.yaml) |
| analytic_rule | ADFS Database Named Pipe Connection | Event.EventID == "18"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [ADFSDBNamedPipeConnection.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSDBNamedPipeConnection.yaml) |
| analytic_rule | Excessive Windows Logon Failures | SecurityEvent.EventID == "4625" | [ExcessiveLogonFailures.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ExcessiveLogonFailures.yaml) |
| analytic_rule | Exchange OAB Virtual Directory Attribute Containin | SecurityEvent.EventID == "5136" | [ExchangeOABVirtualDirectoryAttributeContainingPotentialWebshell.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ExchangeOABVirtualDirectoryAttributeContainingPotentialWebshell.yaml) |
| analytic_rule | Gain Code Execution on ADFS Server via SMB + Remot | SecurityEvent.EventID in "4624,4688,4697,4698,4699,4700,4701,4702,5145" | [GainCodeExecutionADFSViaSMB.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/GainCodeExecutionADFSViaSMB.yaml) |
| analytic_rule | Microsoft Entra ID Local Device Join Information a | SecurityEvent.EventID in "4656,4663" | [LocalDeviceJoinInfoAndTransportKeyRegKeysAccess.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/LocalDeviceJoinInfoAndTransportKeyRegKeysAccess.yaml) |
| analytic_rule | NRT Base64 Encoded Windows Process Command-lines | SecurityEvent.EventID == "4688" | [NRT_base64_encoded_pefile.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_base64_encoded_pefile.yaml) |
| analytic_rule | NRT Process executed from binary hidden in Base64  | SecurityEvent.EventID == "4688" | [NRT_execute_base64_decodedpayload.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_execute_base64_decodedpayload.yaml) |
| analytic_rule | NRT Security Event log cleared | SecurityEvent.EventID == "1102" | [NRT_SecurityEventLogCleared.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_SecurityEventLogCleared.yaml) |
| analytic_rule | New EXE deployed via Default Domain or Default Dom | SecurityEvent.EventID == "4688" | [NewEXEdeployedviaDefaultDomainorDefaultDomainControllerPolicies.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NewEXEdeployedviaDefaultDomainorDefaultDomainControllerPolicies.yaml) |
| analytic_rule | Non Domain Controller Active Directory Replication | SecurityEvent.EventID in "4624,4662" | [NonDCActiveDirectoryReplication.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NonDCActiveDirectoryReplication.yaml) |
| analytic_rule | Potential Fodhelper UAC Bypass | SecurityEvent.EventID in "4657,4688" | [PotentialFodhelperUACBypass.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/PotentialFodhelperUACBypass.yaml) |
| analytic_rule | Potential re-named sdelete usage | SecurityEvent.EventID == "4688" | [Potentialre-namedsdeleteusage.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/Potentialre-namedsdeleteusage.yaml) |
| analytic_rule | Process Execution Frequency Anomaly | SecurityEvent.EventID == "4688" | [TimeSeriesAnomaly-ProcessExecutions.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/TimeSeriesAnomaly-ProcessExecutions.yaml) |
| analytic_rule | Scheduled Task Hide | SecurityEvent.EventID == "4657" | [ScheduleTaskHide.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ScheduleTaskHide.yaml) |
| analytic_rule | Sdelete deployed via GPO and run recursively | SecurityEvent.EventID == "4688" | [SdeletedeployedviaGPOandrunrecursively.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/SdeletedeployedviaGPOandrunrecursively.yaml) |
| analytic_rule | SecurityEvent - Multiple authentication failures f | SecurityEvent.EventID in "4624,4625" | [MultipleFailedFollowedBySuccess.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/MultipleFailedFollowedBySuccess.yaml) |
| analytic_rule | Starting or Stopping HealthService to Avoid Detect | SecurityEvent.EventID in "4624,4656" | [StartStopHealthService.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/StartStopHealthService.yaml) |
| hunting_query | AD Account Lockout | SecurityEvent.EventID == "4740" | [ADAccountLockouts.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ADAccountLockouts.yaml) |
| hunting_query | Commands executed by WMI on new hosts - potential  | SecurityEvent.EventID == "4688" | [CommandsexecutedbyWMIonnewhosts-potentialImpacket.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/CommandsexecutedbyWMIonnewhosts-potentialImpacket.yaml) |
| hunting_query | Crash dump disabled on host | SecurityEvent.EventID == "4657" | [Crashdumpdisabledonhost.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Crashdumpdisabledonhost.yaml) |
| hunting_query | Decoy User Account Authentication Attempt | SecurityEvent.EventID in "4624,4625" | [DecoyUserAccountAuthenticationAttempt.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/DecoyUserAccountAuthenticationAttempt.yaml) |
| hunting_query | Discord download invoked from cmd line | SecurityEvent.EventID == "4688" | [Discorddownloadinvokedfromcmdline.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Discorddownloadinvokedfromcmdline.yaml) |
| hunting_query | Exchange PowerShell Snapin Added | SecurityEvent.EventID == "4688" | [ExchangePowerShellSnapin.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ExchangePowerShellSnapin.yaml) |
| hunting_query | Host Exporting Mailbox and Removing Export | SecurityEvent.EventID == "4688" | [HostExportingMailboxAndRemovingExport.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/HostExportingMailboxAndRemovingExport.yaml) |
| hunting_query | Hosts Running a Rare Process | SecurityEvent.EventID == "4688" | [RareProcess_forWinHost.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcess_forWinHost.yaml) |
| hunting_query | Hosts Running a Rare Process with Commandline | SecurityEvent.EventID == "4688" | [RareProcessWithCmdLine.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcessWithCmdLine.yaml) |
| hunting_query | Invoke-PowerShellTcpOneLine Usage. | SecurityEvent.EventID == "4688" | [Invoke-PowerShellTcpOneLine.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Invoke-PowerShellTcpOneLine.yaml) |
| hunting_query | KrbRelayUp Local Privilege Escalation Service Crea | Event.EventID == "7045"  \|  Event.Source == "Service Control Manager" | [KrbRelayUpServiceCreation.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/KrbRelayUpServiceCreation.yaml) |
| hunting_query | Least Common Parent And Child Process Pairs | SecurityEvent.EventID == "4688" | [Least_Common_Parent_Child_Process.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Parent_Child_Process.yaml) |
| hunting_query | Least Common Processes Including Folder Depth | SecurityEvent.EventID == "4688" | [Least_Common_Process_With_Depth.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Process_With_Depth.yaml) |
| hunting_query | Least Common Processes by Command Line | SecurityEvent.EventID == "4688" | [Least_Common_Process_Command_Lines.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Process_Command_Lines.yaml) |
| hunting_query | Long lookback User Account Created and Deleted wit | SecurityEvent.EventID in "4720,4726" | [UserAccountCreatedDeleted.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAccountCreatedDeleted.yaml) |
| hunting_query | Multiple Explicit Credential Usage - 4648 events | SecurityEvent.EventID == "4648" | [MultipleExplicitCredentialUsage4648Events.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/MultipleExplicitCredentialUsage4648Events.yaml) |
| hunting_query | New Child Process of W3WP.exe | SecurityEvent.EventID == "4688" | [NewChildProcessOfW3WP.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/NewChildProcessOfW3WP.yaml) |
| hunting_query | Nishang Reverse TCP Shell in Base64 | SecurityEvent.EventID == "4688" | [NishangReverseTCPShellBase64.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/NishangReverseTCPShellBase64.yaml) |
| hunting_query | Potential Exploitation of MS-RPRN printer bug | SecurityEvent.EventID == "5145" | [MSRPRN_Printer_Bug_Exploitation.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/MSRPRN_Printer_Bug_Exploitation.yaml) |
| hunting_query | Powercat Download | SecurityEvent.EventID == "4688" | [PowerCatDownload.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/PowerCatDownload.yaml) |
| hunting_query | Rare Process Path | SecurityEvent.EventID == "4688" | [RareProcessPath.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcessPath.yaml) |
| hunting_query | Remote Task Creation/Update using Schtasks Process | SecurityEvent.EventID == "4688" | [RemoteScheduledTaskCreationUpdateviaSchtasks.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RemoteScheduledTaskCreationUpdateviaSchtasks.yaml) |
| hunting_query | Service installation from user writable directory | Event.EventID == "7045"  \|  Event.Source == "Service Control Manager" | [ServiceInstallationFromUsersWritableDirectory.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ServiceInstallationFromUsersWritableDirectory.yaml) |
| hunting_query | Summary of failed user logons by reason of failure | SecurityEvent.EventID == "4625" | [FailedUserLogons.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/FailedUserLogons.yaml) |
| hunting_query | Summary of user logons by logon type | SecurityEvent.EventID in "4624,4625" | [User Logons By Logon Type.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/User%20Logons%20By%20Logon%20Type.yaml) |
| hunting_query | Summary of users created using uncommon/undocument | SecurityEvent.EventID == "4688" | [persistence_create_account.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/persistence_create_account.yaml) |
| hunting_query | Suspected LSASS Dump | SecurityEvent.EventID == "4688" | [SuspectedLSASSDump.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/SuspectedLSASSDump.yaml) |
| hunting_query | Suspicious Enumeration using Adfind Tool | SecurityEvent.EventID == "4688" | [Suspicious_enumeration_using_adfind.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Suspicious_enumeration_using_adfind.yaml) |
| hunting_query | Suspicious Windows Login Outside Normal Hours | SecurityEvent.EventID in "4624,4625" | [Suspicious_Windows_Login_outside_normal_hours.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Suspicious_Windows_Login_outside_normal_hours.yaml) |
| hunting_query | Suspicious command line tokens in LolBins or LolSc | SecurityEvent.EventID == "4688" | [SuspiciousCommandlineTokenLolbas.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/SuspiciousCommandlineTokenLolbas.yaml) |
| hunting_query | User Account added to Built in Sensitive or Privil | SecurityEvent.EventID in "4728,4732,4756" | [UserAccountAddedToPrivlegeGroup.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAccountAddedToPrivlegeGroup.yaml) |
| hunting_query | User account added or removed from a security grou | SecurityEvent.EventID in "4728,4729,4732,4733,4746,4747,4751,4752,4756,4757,4761,4762" | [UserAdd_RemToGroupByUnauthorizedUser.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAdd_RemToGroupByUnauthorizedUser.yaml) |
| hunting_query | User created by unauthorized user | SecurityEvent.EventID == "4720" | [UserCreatedByUnauthorizedUser.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserCreatedByUnauthorizedUser.yaml) |
| hunting_query | VIP account more than 6 failed logons in 10 | SecurityEvent.EventID == "4625" | [CustomUserList_FailedLogons.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/CustomUserList_FailedLogons.yaml) |
| hunting_query | VIP account more than 6 failed logons in 10 | SecurityEvent.EventID == "4625" | [VIPAccountFailedLogons.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/VIPAccountFailedLogons.yaml) |
| hunting_query | Windows System Shutdown/Reboot(Sysmon) | Event.EventID == "1"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [WindowsSystemShutdownReboot.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/WindowsSystemShutdownReboot.yaml) |
| hunting_query | Windows System Time changed on hosts | SecurityEvent.EventID == "4616" | [WindowsSystemTimeChange.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/WindowsSystemTimeChange.yaml) |
| workbook | EventAnalyzer | SecurityEvent.EventID in "4656,4657,4658,4660,4661,4663,4664,4670,4671,4673,4674,4690,4691,4698,4699,4700,4701,4702,4715,4719,4817,4902,4904,4905,4906,4907,4908,4912,4985,5031,5039,5051,5140,5142,5143,5144,5148,5149,5150,5151,5154,5155,5156,5157,5158,5159,5168,5888,5889,5890" | [EventAnalyzer.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Workbooks/EventAnalyzer.json) |

### ZeroTrust(TIC3.0)

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| workbook | ZeroTrustTIC3 | AzureDiagnostics.Category in "ApplicationGatewayFirewallLog,AzureFirewallApplicationRule,AzureFirewallDnsProxy,AzureFirewallNetworkRule,DDoSMitigationReports,FrontdoorWebApplicationFirewallLog,NetworkSecurityGroupEvent,WebApplicationFirewallLogs,kube-audit"  \|  AzureDiagnostics.Category contains "SQL"  \|  AzureDiagnostics.ResourceType in "APPLICATIONGATEWAYS,AZUREFIREWALLS,CDNWEBAPPLICATIONFIREWALLPOLICIES,FRONTDOORS,PROFILES,PUBLICIPADDRESSES" | [ZeroTrustTIC3.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json) |

### Zscaler Internet Access

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | Discord CDN Risky File Download | CommonSecurityLog.DeviceVendor =~ "ZScaler" | [DiscordCDNRiskyDownload.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Analytic%20Rules/DiscordCDNRiskyDownload.yaml) |
| analytic_rule | Request for single resource on domain | CommonSecurityLog.DeviceVendor =~ "Zscaler" | [Zscaler-LowVolumeDomainRequests.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Analytic%20Rules/Zscaler-LowVolumeDomainRequests.yaml) |
| workbook | ZscalerFirewall | CommonSecurityLog.DeviceProduct == "NSSFWlog" | [ZscalerFirewall.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerFirewall.json) |
| workbook | ZscalerOffice365Apps | CommonSecurityLog.DeviceVendor == "Zscaler" | [ZscalerOffice365Apps.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerOffice365Apps.json) |
| workbook | ZscalerThreats | CommonSecurityLog.DeviceProduct == "NSSWeblog"  \|  CommonSecurityLog.DeviceVendor == "Zscaler" | [ZscalerThreats.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerThreats.json) |
| workbook | ZscalerWebOverview | CommonSecurityLog.DeviceProduct == "NSSWeblog"  \|  CommonSecurityLog.DeviceVendor == "Zscaler" | [ZscalerWebOverview.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zscaler%20Internet%20Access/Workbooks/ZscalerWebOverview.json) |

### vArmour Application Controller

| Type | Name | Filter Fields | File |
|------|------|---------------|------|
| analytic_rule | vArmour AppController - SMB Realm Traversal | CommonSecurityLog.DeviceProduct == "AC"  \|  CommonSecurityLog.DeviceVendor == "vArmour" | [vArmourApplicationControllerSMBRealmTraversal.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Analytic%20Rules/vArmourApplicationControllerSMBRealmTraversal.yaml) |
| workbook | vArmour_AppContoller_Workbook | CommonSecurityLog.DeviceProduct == "AC"  \|  CommonSecurityLog.DeviceVendor == "vArmour" | [vArmour_AppContoller_Workbook.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/vArmour%20Application%20Controller/Workbooks/vArmour_AppContoller_Workbook.json) |


## ASIM Parsers with Filter Fields

Total: 74 parsers

### AuditEvent Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimAuditEventBarracudaCEF | Barracuda WAF | CommonSecurityLog.DeviceProduct in "WAAS,WAF"  \|  CommonSecurityLog.DeviceVendor startswith "Barracuda" | [Parsers\ASimAuditEvent\Parsers\ASimAuditEventBarracudaCEF.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/Parsers/ASimAuditEventBarracudaCEF.yaml) |
| ASimAuditEventCiscoISE | Cisco ISE | Syslog.ProcessName has_any "CISE,CSCO" | [Parsers\ASimAuditEvent\Parsers\ASimAuditEventCiscoISE.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/Parsers/ASimAuditEventCiscoISE.yaml) |
| ASimAuditEventCrowdStrikeFalconHost | CrowdStrike Falcon Endpoint Pr | CommonSecurityLog.DeviceProduct == "FalconHost"  \|  CommonSecurityLog.DeviceVendor == "CrowdStrike" | [Parsers\ASimAuditEvent\Parsers\ASimAuditEventCrowdStrikeFalconHost.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/Parsers/ASimAuditEventCrowdStrikeFalconHost.yaml) |
| ASimAuditEventInfobloxBloxOne | Infoblox BloxOne | CommonSecurityLog.DeviceVendor == "Infoblox" | [Parsers\ASimAuditEvent\Parsers\ASimAuditEventInfobloxBloxOne.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/Parsers/ASimAuditEventInfobloxBloxOne.yaml) |
| ASimAuditEventMicrosoftWindowsEvents | Microsoft Windows | WindowsEvent.Provider == "Microsoft-Windows-Eventlog" | [Parsers\ASimAuditEvent\Parsers\ASimAuditEventMicrosoftWindowsEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuditEvent/Parsers/ASimAuditEventMicrosoftWindowsEvents.yaml) |

### Authentication Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimAuthenticationBarracudaWAF | Barracuda WAF | CommonSecurityLog.DeviceProduct in "WAAS,WAF"  \|  CommonSecurityLog.DeviceVendor startswith "Barracuda" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationBarracudaWAF.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationBarracudaWAF.yaml) |
| ASimAuthenticationCiscoASA | Cisco Adaptive Security Applia | CommonSecurityLog.DeviceProduct == "ASA"  \|  CommonSecurityLog.DeviceVendor =~ "Cisco" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationCiscoASA.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationCiscoASA.yaml) |
| ASimAuthenticationCiscoISE | Cisco ISE | Syslog.ProcessName has_any "CISE,CSCO" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationCiscoISE.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationCiscoISE.yaml) |
| ASimAuthenticationCrowdStrikeFalconHost | CrowdStrike Falcon Endpoint Pr | CommonSecurityLog.DeviceProduct == "FalconHost"  \|  CommonSecurityLog.DeviceVendor == "CrowdStrike" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationCrowdStrikeFalconHost.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationCrowdStrikeFalconHost.yaml) |
| ASimAuthenticationMicrosoftWindowsEvent | Windows Security Events | WindowsEvent.EventID in "4624,4625,4634"  \|  WindowsEvent.Provider == "Microsoft-Windows-Security-Auditing" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationMicrosoftWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationMicrosoftWindowsEvent.yaml) |
| ASimAuthenticationPaloAltoCortexDataLake | Palo Alto Cortex Data Lake | CommonSecurityLog.DeviceProduct == "LF"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationPaloAltoCortexDataLake.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationPaloAltoCortexDataLake.yaml) |
| ASimAuthenticationSshd | OpenSSH | Syslog.ProcessName == "sshd"  \|  Syslog.SyslogMessage has "Failed"  \|  Syslog.SyslogMessage has "but this does not map back to the address"  \|  Syslog.SyslogMessage has "publickey"  \|  Syslog.SyslogMessage startswith "Accepted"  \|  Syslog.SyslogMessage startswith "Failed"  \|  Syslog.SyslogMessage startswith "Invalid user"  \|  Syslog.SyslogMessage startswith "Nasty PTR record"  \|  Syslog.SyslogMessage startswith "Timeout"  \|  Syslog.SyslogMessage startswith "message repeated"  \|  Syslog.SyslogMessage startswith "reverse mapping checking getaddrinfo for" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationSshd.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationSshd.yaml) |
| ASimAuthenticationSu | su | Syslog.ProcessName == "su"  \|  Syslog.SyslogMessage has_all "pam_unix(su"  \|  Syslog.SyslogMessage startswith "Successful su for" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationSu.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationSu.yaml) |
| ASimAuthenticationSudo | sudo | Syslog.ProcessName == "sudo"  \|  Syslog.SyslogMessage has "COMMAND="  \|  Syslog.SyslogMessage has "TTY="  \|  Syslog.SyslogMessage has "USER="  \|  Syslog.SyslogMessage has "incorrect password attempts"  \|  Syslog.SyslogMessage has "session closed for user"  \|  Syslog.SyslogMessage has "user NOT in sudoers" | [Parsers\ASimAuthentication\Parsers\ASimAuthenticationSudo.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/Parsers/ASimAuthenticationSudo.yaml) |

### DhcpEvent Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimDhcpEventInfobloxBloxOne | Infoblox BloxOne | CommonSecurityLog.DeviceVendor == "Infoblox" | [Parsers\ASimDhcpEvent\Parsers\ASimDhcpEventInfobloxBloxOne.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDhcpEvent/Parsers/ASimDhcpEventInfobloxBloxOne.yaml) |

### Dns Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimDnsAzureFirewall | Azure Firewall | AzureDiagnostics.Category == "AzureFirewallDnsProxy"  \|  AzureDiagnostics.ResourceType == "AZUREFIREWALLS" | [Parsers\ASimDns\Parsers\ASimDnsAzureFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsAzureFirewall.yaml) |
| ASimDnsFortinetFortiGate | Fortinet FortiGate | CommonSecurityLog.DeviceProduct startswith "Fortigate"  \|  CommonSecurityLog.DeviceVendor == "Fortinet" | [Parsers\ASimDns\Parsers\ASimDnsFortinetFortigate.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsFortinetFortigate.yaml) |
| ASimDnsInfobloxBloxOne | Infoblox BloxOne | CommonSecurityLog.DeviceVendor == "Infoblox" | [Parsers\ASimDns\Parsers\ASimDnsInfobloxBloxOne.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsInfobloxBloxOne.yaml) |
| ASimDnsInfobloxNIOS | Infoblox NIOS | Syslog.ProcessName == "named"  \|  Syslog.SyslogMessage !has "response:"  \|  Syslog.SyslogMessage has_all "client" | [Parsers\ASimDns\Parsers\ASimDnsInfobloxNIOS.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsInfobloxNIOS.yaml) |
| ASimDnsMicrosoftSysmon | Microsoft Windows Events Sysmo | Event.EventID == "22"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [Parsers\ASimDns\Parsers\ASimDnsMicrosoftSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsMicrosoftSysmon.yaml) |
| ASimDnsMicrosoftSysmonWindowsEvent | Microsoft Windows Events Sysmo | WindowsEvent.EventID == "22"  \|  WindowsEvent.Provider == "Microsoft-Windows-Sysmon" | [Parsers\ASimDns\Parsers\ASimDnsMicrosoftSysmonWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsMicrosoftSysmonWindowsEvent.yaml) |
| ASimDnsZscalerZIA | Zscaler ZIA DNS | CommonSecurityLog.DeviceProduct == "NSSDNSlog" | [Parsers\ASimDns\Parsers\ASimDnsZscalerZIA.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimDns/Parsers/ASimDnsZscalerZIA.yaml) |

### FileEvent Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimFileEventLinuxSysmonFileCreated | Microsoft Sysmon for Linux | Syslog.SyslogMessage has_all "<Provider Name=" | [Parsers\ASimFileEvent\Parsers\ASimFileEventLinuxSysmonFileCreated.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/Parsers/ASimFileEventLinuxSysmonFileCreated.yaml) |
| ASimFileEventLinuxSysmonFileDeleted | Microsoft Sysmon for Linux | Syslog.SyslogMessage has "<Provider Name="  \|  Syslog.SyslogMessage has_any "<EventID>23</EventID>,<EventID>26</EventID>" | [Parsers\ASimFileEvent\Parsers\ASimFileEventLinuxSysmonFileDeleted.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/Parsers/ASimFileEventLinuxSysmonFileDeleted.yaml) |
| ASimFileEventMicrosoftSecurityEvents | Microsoft Windows Events | SecurityEvent.EventID == "4663" | [Parsers\ASimFileEvent\Parsers\ASimFileEventMicrosoftSecurityEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/Parsers/ASimFileEventMicrosoftSecurityEvents.yaml) |
| ASimFileEventMicrosoftSysmon | Windows Sysmon | Event.EventID in "11,23,26"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [Parsers\ASimFileEvent\Parsers\ASimFileEventMicrosoftSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/Parsers/ASimFileEventMicrosoftSysmon.yaml) |
| ASimFileEventMicrosoftSysmonWindowsEvent | Windows Sysmon | WindowsEvent.EventID in "11,23,26"  \|  WindowsEvent.Provider == "Microsoft-Windows-Sysmon" | [Parsers\ASimFileEvent\Parsers\ASimFileEventMicrosoftSysmonWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/Parsers/ASimFileEventMicrosoftSysmonWindowsEvent.yaml) |
| ASimFileEventMicrosoftWindowsEvents | Microsoft Windows Events | WindowsEvent.EventID == "4663" | [Parsers\ASimFileEvent\Parsers\ASimFileEventMicrosoftWindowsEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimFileEvent/Parsers/ASimFileEventMicrosoftWindowsEvents.yaml) |

### NetworkSession Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimNetworkSessionAppGateSDP | AppGate SDP | Syslog.ProcessName in "cz-sessiond,cz-vpnd"  \|  Syslog.SyslogMessage has_all "[AUDIT]"  \|  Syslog.SyslogMessage has_any ":" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionAppGateSDP.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionAppGateSDP.yaml) |
| ASimNetworkSessionAzureFirewall | Azure Firewall | AzureDiagnostics.Category == "AzureFirewallNetworkRule" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionAzureFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionAzureFirewall.yaml) |
| ASimNetworkSessionBarracudaCEF | Barracuda WAF | CommonSecurityLog.DeviceProduct in "WAAS,WAF"  \|  CommonSecurityLog.DeviceVendor startswith "Barracuda" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionBarracudaCEF.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionBarracudaCEF.yaml) |
| ASimNetworkSessionCheckPointFirewall | CheckPointFirewall | CommonSecurityLog.DeviceProduct == "VPN-1 & FireWall-1"  \|  CommonSecurityLog.DeviceVendor == "CheckPoint" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionCheckPointFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionCheckPointFirewall.yaml) |
| ASimNetworkSessionCiscoASA | CiscoASA | CommonSecurityLog.DeviceProduct == "ASA"  \|  CommonSecurityLog.DeviceVendor == "Cisco" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionCiscoASA.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionCiscoASA.yaml) |
| ASimNetworkSessionCiscoFirepower | Cisco Firepower | CommonSecurityLog.DeviceProduct == "Firepower"  \|  CommonSecurityLog.DeviceVendor == "Cisco" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionCiscoFirepower.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionCiscoFirepower.yaml) |
| ASimNetworkSessionCiscoISE | Cisco ISE | Syslog.ProcessName has_any "CISE,CSCO" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionCiscoISE.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionCiscoISE.yaml) |
| ASimNetworkSessionCrowdStrikeFalconHost | CrowdStrike Falcon Endpoint Pr | CommonSecurityLog.DeviceProduct == "FalconHost"  \|  CommonSecurityLog.DeviceVendor == "CrowdStrike" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionCrowdStrikeFalconHost.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionCrowdStrikeFalconHost.yaml) |
| ASimNetworkSessionForcePointFirewall | ForcePointFirewall | CommonSecurityLog.DeviceProduct == "Firewall"  \|  CommonSecurityLog.DeviceVendor == "FORCEPOINT" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionForcePointFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionForcePointFirewall.yaml) |
| ASimNetworkSessionFortinetFortiGate | Fortinet FortiGate | CommonSecurityLog.DeviceProduct startswith "FortiGate"  \|  CommonSecurityLog.DeviceVendor == "Fortinet" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionFortinetFortiGate.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionFortinetFortiGate.yaml) |
| ASimNetworkSessionLinuxSysmon | Sysmon for Linux | Syslog.SyslogMessage has_all "<Provider Name=" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionMicrosoftLinuxSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionMicrosoftLinuxSysmon.yaml) |
| ASimNetworkSessionMicrosoftSecurityEventFirewall | Windows Firewall | SecurityEvent.EventID in "5152,5154,5155,5156,5157,5158,5159" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionMicrosoftSecurityEventFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionMicrosoftSecurityEventFirewall.yaml) |
| ASimNetworkSessionMicrosoftSysmon | Windows Sysmon | Event.EventID == "3"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionMicrosoftSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionMicrosoftSysmon.yaml) |
| ASimNetworkSessionMicrosoftSysmonWindowsEvent | Windows Sysmon | WindowsEvent.EventID == "3"  \|  WindowsEvent.Provider == "Microsoft-Windows-Sysmon" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionMicrosoftSysmonWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionMicrosoftSysmonWindowsEvent.yaml) |
| ASimNetworkSessionMicrosoftWindowsEventFirewall | Windows Firewall | WindowsEvent.EventID in "5154,5155,5156,5158,5159" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionMicrosoftWindowsEventFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionMicrosoftWindowsEventFirewall.yaml) |
| ASimNetworkSessionPaloAltoCEF | Palo Alto PanOS | CommonSecurityLog.DeviceProduct == "PAN-OS"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionPaloAltoCEF.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionPaloAltoCEF.yaml) |
| ASimNetworkSessionPaloAltoCortexDataLake | Palo Alto Cortex Data Lake | CommonSecurityLog.DeviceProduct == "LF"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionPaloAltoCortexDataLake.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionPaloAltoCortexDataLake.yaml) |
| ASimNetworkSessionSonicWallFirewall | SonicWall | CommonSecurityLog.DeviceVendor == "SonicWall" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionSonicWallFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionSonicWallFirewall.yaml) |
| ASimNetworkSessionWatchGuardFirewareOS | WatchGuard Fireware OS | Syslog.SyslogMessage !has "3000-0151"  \|  Syslog.SyslogMessage !has "icmp"  \|  Syslog.SyslogMessage !has "igmp"  \|  Syslog.SyslogMessage !has "msg="  \|  Syslog.SyslogMessage has "3000-0151"  \|  Syslog.SyslogMessage has "icmp"  \|  Syslog.SyslogMessage has "igmp"  \|  Syslog.SyslogMessage has_any "msg_id=" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionWatchGuardFirewareOS.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionWatchGuardFirewareOS.yaml) |
| ASimNetworkSessionZscalerZIA | Zscaler ZIA Firewall | CommonSecurityLog.DeviceProduct == "NSSFWlog"  \|  CommonSecurityLog.DeviceVendor == "Zscaler" | [Parsers\ASimNetworkSession\Parsers\ASimNetworkSessionzScalerZIA.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimNetworkSession/Parsers/ASimNetworkSessionzScalerZIA.yaml) |

### ProcessEvent Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimProcessCreateLinuxSysmon | Sysmon for Linux | Syslog.SyslogMessage has_all "<Provider Name=" | [Parsers\ASimProcessEvent\Parsers\ASimProcessCreateLinuxSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessCreateLinuxSysmon.yaml) |
| ASimProcessCreateMicrosoftSecurityEvents | Security Events | SecurityEvent.EventID == "4688" | [Parsers\ASimProcessEvent\Parsers\ASimProcessCreateMicrosoftSecurityEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessCreateMicrosoftSecurityEvents.yaml) |
| ASimProcessCreateMicrosoftWindowsEvents | Security Events | WindowsEvent.EventID == "4688" | [Parsers\ASimProcessEvent\Parsers\ASimProcessCreateMicrosoftWindowsEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessCreateMicrosoftWindowsEvents.yaml) |
| ASimProcessEventCreateMicrosoftSysmon | Sysmon | Event.EventID == "1"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [Parsers\ASimProcessEvent\Parsers\ASimProcessCreateMicrosoftSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessCreateMicrosoftSysmon.yaml) |
| ASimProcessEventCreateMicrosoftSysmonWindowsEvent | Sysmon | WindowsEvent.EventID == "1"  \|  WindowsEvent.Provider == "Microsoft-Windows-Sysmon" | [Parsers\ASimProcessEvent\Parsers\ASimProcessCreateMicrosoftSysmonWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessCreateMicrosoftSysmonWindowsEvent.yaml) |
| ASimProcessEventTerminateMicrosoftSysmon | Microsoft Windows Events Sysmo | Event.EventID == "5"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [Parsers\ASimProcessEvent\Parsers\ASimProcessTerminateMicrosoftSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessTerminateMicrosoftSysmon.yaml) |
| ASimProcessEventTerminateMicrosoftSysmonWindowsEvent | Microsoft Windows Events Sysmo | WindowsEvent.EventID == "5"  \|  WindowsEvent.Provider == "Microsoft-Windows-Sysmon" | [Parsers\ASimProcessEvent\Parsers\ASimProcessTerminateMicrosoftSysmonWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessTerminateMicrosoftSysmonWindowsEvent.yaml) |
| ASimProcessTerminateLinuxSysmon | Sysmon for Linux | Syslog.SyslogMessage has_all "<Provider Name=" | [Parsers\ASimProcessEvent\Parsers\ASimProcessTerminateLinuxSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessTerminateLinuxSysmon.yaml) |
| ASimProcessTerminateMicrosoftSecurityEvents | Security Events | SecurityEvent.EventID == "4689" | [Parsers\ASimProcessEvent\Parsers\ASimProcessTerminateMicrosoftSecurityEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessTerminateMicrosoftSecurityEvents.yaml) |
| ASimProcessTerminateMicrosoftWindowsEvents | Security Events | WindowsEvent.EventID == "4689" | [Parsers\ASimProcessEvent\Parsers\ASimProcessTerminateMicrosoftWindowsEvents.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimProcessEvent/Parsers/ASimProcessTerminateMicrosoftWindowsEvents.yaml) |

### RegistryEvent Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimRegistryEventMicrosoftSecurityEvent | Security Events | SecurityEvent.EventID in "4657,4663" | [Parsers\ASimRegistryEvent\Parsers\ASimRegistryEventMicrosoftSecurityEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimRegistryEvent/Parsers/ASimRegistryEventMicrosoftSecurityEvent.yaml) |
| ASimRegistryEventMicrosoftSysmon | Microsoft Sysmon | Event.EventID in "12,13,14"  \|  Event.Source == "Microsoft-Windows-Sysmon" | [Parsers\ASimRegistryEvent\Parsers\ASimRegistryEventMicrosoftSysmon.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimRegistryEvent/Parsers/ASimRegistryEventMicrosoftSysmon.yaml) |
| ASimRegistryEventMicrosoftSysmonWindowsEvent | Microsoft Sysmon | WindowsEvent.EventID in "12,13,14"  \|  WindowsEvent.Provider == "Microsoft-Windows-Sysmon" | [Parsers\ASimRegistryEvent\Parsers\ASimRegistryEventMicrosoftSysmonWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimRegistryEvent/Parsers/ASimRegistryEventMicrosoftSysmonWindowsEvent.yaml) |
| ASimRegistryEventMicrosoftWindowsEvent | Security Events | WindowsEvent.EventID in "4657,4663" | [Parsers\ASimRegistryEvent\Parsers\ASimRegistryEventMicrosoftWindowsEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimRegistryEvent/Parsers/ASimRegistryEventMicrosoftWindowsEvent.yaml) |

### UserManagement Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimUserManagementCiscoISE | Cisco ISE | Syslog.ProcessName has_any "CISE,CSCO" | [Parsers\ASimUserManagement\Parsers\ASimUserManagementCiscoISE.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimUserManagement/Parsers/ASimUserManagementCiscoISE.yaml) |
| ASimUserManagementLinuxAuthpriv | Microsoft | Syslog.Facility == "authpriv"  \|  Syslog.ProcessName in "gpasswd,groupadd,groupdel,groupmod,useradd,userdel,usermod" | [Parsers\ASimUserManagement\Parsers\ASimUserManagementLinuxAuthpriv.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimUserManagement/Parsers/ASimUserManagementLinuxAuthpriv.yaml) |
| ASimUserManagementMicrosoftSecurityEvent | Microsoft Security Event | SecurityEvent.EventID in "4744,4748,4749,4753,4759,4763" | [Parsers\ASimUserManagement\Parsers\ASimUserManagementMicrosoftSecurityEvent.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimUserManagement/Parsers/ASimUserManagementMicrosoftSecurityEvent.yaml) |

### WebSession Schema

| Parser Name | Product | Filter Fields | File |
|-------------|---------|---------------|------|
| ASimWebSessionBarracudaCEF | Barracuda WAF | CommonSecurityLog.DeviceProduct in "WAAS,WAF"  \|  CommonSecurityLog.DeviceVendor startswith "Barracuda" | [Parsers\ASimWebSession\Parsers\ASimWebSessionBarracudaCEF.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionBarracudaCEF.yaml) |
| ASimWebSessionCiscoFirepower | Cisco Firepower | CommonSecurityLog.DeviceProduct == "Firepower"  \|  CommonSecurityLog.DeviceVendor == "Cisco" | [Parsers\ASimWebSession\Parsers\ASimWebSessionCiscoFirepower.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionCiscoFirepower.yaml) |
| ASimWebSessionCitrixNetScaler | Citrix NetScaler | CommonSecurityLog.DeviceProduct == "NetScaler"  \|  CommonSecurityLog.DeviceVendor == "Citrix" | [Parsers\ASimWebSession\Parsers\ASimWebSessionCitrixNetScaler.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionCitrixNetScaler.yaml) |
| ASimWebSessionF5ASM | F5 BIG-IP Application Security | CommonSecurityLog.DeviceProduct == "ASM"  \|  CommonSecurityLog.DeviceVendor == "F5" | [Parsers\ASimWebSession\Parsers\ASimWebSessionF5ASM.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionF5ASM.yaml) |
| ASimWebSessionFortinetFortiGate | Fortinet FortiGate | CommonSecurityLog.DeviceProduct startswith "Fortigate"  \|  CommonSecurityLog.DeviceVendor == "Fortinet" | [Parsers\ASimWebSession\Parsers\ASimWebSessionFortinetFortiGate.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionFortinetFortiGate.yaml) |
| ASimWebSessionPaloAltoCEF | Palo Alto Networks | CommonSecurityLog.DeviceProduct == "PAN-OS"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Parsers\ASimWebSession\Parsers\ASimWebSessionPaloAltoCEF.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionPaloAltoCEF.yaml) |
| ASimWebSessionPaloAltoCortexDataLake | Palo Alto Cortex Data Lake | CommonSecurityLog.DeviceProduct == "LF"  \|  CommonSecurityLog.DeviceVendor == "Palo Alto Networks" | [Parsers\ASimWebSession\Parsers\ASimWebSessionPaloAltoCortexDataLake.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionPaloAltoCortexDataLake.yaml) |
| ASimWebSessionSonicWallFirewall | SonicWall | CommonSecurityLog.DeviceVendor == "SonicWall" | [Parsers\ASimWebSession\Parsers\ASimWebSessionSonicWallFirewall.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionSonicWallFirewall.yaml) |
| ASimWebSessionZscalerZIA | Zscaler ZIA | CommonSecurityLog.DeviceProduct == "NSSWeblog"  \|  CommonSecurityLog.DeviceVendor == "Zscaler" | [Parsers\ASimWebSession\Parsers\ASimWebSessionzScalerZIA.yaml](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimWebSession/Parsers/ASimWebSessionzScalerZIA.yaml) |

