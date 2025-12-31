# SecurityAlert

Reference for SecurityAlert table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Internal |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityalert) |

## Solutions (39)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [Azure Key Vault](../solutions/azure-key-vault.md)
- [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md)
- [Azure kubernetes Service](../solutions/azure-kubernetes-service.md)
- [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md)
- [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md)
- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [DORA Compliance](../solutions/dora-compliance.md)
- [Dragos](../solutions/dragos.md)
- [Dynatrace](../solutions/dynatrace.md)
- [ExtraHop](../solutions/extrahop.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [Infoblox](../solutions/infoblox.md)
- [Infoblox SOC Insights](../solutions/infoblox-soc-insights.md)
- [IoTOTThreatMonitoringwithDefenderforIoT](../solutions/iototthreatmonitoringwithdefenderforiot.md)
- [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Defender For Identity](../solutions/microsoft-defender-for-identity.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Defender for Cloud](../solutions/microsoft-defender-for-cloud.md)
- [Microsoft Defender for Cloud Apps](../solutions/microsoft-defender-for-cloud-apps.md)
- [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md)
- [Microsoft Entra ID Protection](../solutions/microsoft-entra-id-protection.md)
- [MicrosoftDefenderForEndpoint](../solutions/microsoftdefenderforendpoint.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [ReversingLabs](../solutions/reversinglabs.md)
- [SOC Handbook](../solutions/soc-handbook.md)
- [SentinelSOARessentials](../solutions/sentinelsoaressentials.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatAnalysis&Response](../solutions/threatanalysis&response.md)
- [Vectra XDR](../solutions/vectra-xdr.md)
- [Web Session Essentials](../solutions/web-session-essentials.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (10)

This table is ingested by the following connectors:

- [Microsoft Entra ID Protection](../connectors/azureactivedirectoryidentityprotection.md)
- [Microsoft Defender for Identity](../connectors/azureadvancedthreatprotection.md)
- [Subscription-based Microsoft Defender for Cloud (Legacy)](../connectors/azuresecuritycenter.md)
- [Microsoft Defender for IoT](../connectors/iot.md)
- [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md)
- [Microsoft Defender for Endpoint](../connectors/microsoftdefenderadvancedthreatprotection.md)
- [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md)
- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)
- [Microsoft Defender for Office 365 (Preview)](../connectors/officeatp.md)
- [Microsoft 365 Insider Risk Management](../connectors/officeirm.md)

---

## Content Items Using This Table (81)

### Analytic Rules (34)

**In solution [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md):**
- [Azure DevOps Pipeline modified by a new user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOPipelineModifiedbyNewUser.yaml)

**In solution [Dragos](../solutions/dragos.md):**
- [Dragos Notifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Analytic%20Rules/DragosNotifiction.yaml)

**In solution [IoTOTThreatMonitoringwithDefenderforIoT](../solutions/iototthreatmonitoringwithdefenderforiot.md):**
- [Denial of Service (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTDenialofService.yaml)
- [Excessive Login Attempts (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTExcessiveLoginAttempts.yaml)
- [Firmware Updates (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTFirmwareUpdates.yaml)
- [High bandwidth in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTHighBandwidth.yaml)
- [Illegal Function Codes for ICS traffic (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTIllegalFunctionCodes.yaml)
- [Internet Access (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTInternetAccess.yaml)
- [Multiple scans in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTNetworkScanning.yaml)
- [No traffic on Sensor Detected (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTINoSensorTrafficDetected.yaml)
- [PLC Stop Command (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTPLCStopCommand.yaml)
- [PLC unsecure key state (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTInsecurePLC.yaml)
- [Suspicious malware found in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTMalware.yaml)
- [Unauthorized DHCP configuration in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedNetworkConfiguration.yaml)
- [Unauthorized PLC changes (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedPLCModifications.yaml)
- [Unauthorized device in the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedDevice.yaml)
- [Unauthorized remote access to the network (Microsoft Defender for IoT)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IoTOTThreatMonitoringwithDefenderforIoT/Analytic%20Rules/IoTUnauthorizedRemoteAccess.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Suspicious use of TDS endpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Suspicious%20use%20of%20TDS%20endpoint.yaml)
- [Dataverse - Terminated employee exfiltration over email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Terminated%20employee%20exfiltration%20over%20email.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [AV detections related to Ukraine threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/AVdetectionsrelatedtoUkrainebasedthreats.yaml)

**In solution [Microsoft Defender for Cloud](../solutions/microsoft-defender-for-cloud.md):**
- [Detect CoreBackUp Deletion Activity from related Security Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Analytic%20Rules/CoreBackupDeletionwithSecurityAlert.yaml)

**In solution [Microsoft Defender for Cloud Apps](../solutions/microsoft-defender-for-cloud-apps.md):**
- [Linked Malicious Storage Artifacts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps/Analytic%20Rules/AdditionalFilesUploadedByActor.yaml)

**In solution [Microsoft Entra ID Protection](../solutions/microsoft-entra-id-protection.md):**
- [Correlate Unfamiliar sign-in properties & atypical travel alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Analytic%20Rules/CorrelateIPC_Unfamiliar-Atypical.yaml)

**In solution [MicrosoftDefenderForEndpoint](../solutions/microsoftdefenderforendpoint.md):**
- [Aqua Blizzard AV hits - Feb 2022](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Analytic%20Rules/AquaBlizzardAVHits.yaml)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [Insider Risk_High User Security Alert Correlations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskHighUserAlertsCorrelation.yaml)
- [Insider Risk_Microsoft Purview Insider Risk Management Alert Observed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskM365IRMAlertObserved.yaml)

**In solution [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md):**
- [Cross-Cloud Suspicious user activity observed in GCP Envourment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/CrossCloudSuspiciousUserActivityObservedInGCPEnvourment.yaml)
- [Successful AWS Console Login from IP Address Observed Conducting Password Spray](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuccessfulAWSConsoleLoginfromIPAddressObservedConductingPasswordSpray.yaml)
- [Suspicious AWS console logins by credential access alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuspiciousAWSConsolLoginByCredentialAceessAlerts.yaml)
- [User impersonation by Identity Protection alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/UserImpersonateByAAID.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Domain entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_SecurityAlert.yaml)
- [TI map Email entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_SecurityAlert.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_SecurityAlert.yaml)
- [TI map Email entity to SecurityAlert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_SecurityAlert.yaml)

### Hunting Queries (6)

**In solution [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md):**
- [Azure DevOps - New Package Feed Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewPackageFeedCreated.yaml)
- [Azure DevOps - New Release Pipeline Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOReleasePipelineCreated.yaml)

**In solution [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md):**
- [Nylon Typhoon Command Line Activity November 2021](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/NylonTyphoonCommandLineActivity-Nov2021.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Activity after Microsoft Entra alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Activity%20after%20Microsoft%20Entra%20alerts.yaml)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [Insider Risk_Entity Anomaly Followed by IRM Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderEntityAnomalyFollowedByIRMAlert.yaml)
- [Insider Risk_ISP Anomaly to Exfil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderISPAnomalyCorrelatedToExfiltrationAlert.yaml)

### Workbooks (33)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4jImpactAssessment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Workbooks/Log4jImpactAssessment.json)

**In solution [Azure Key Vault](../solutions/azure-key-vault.md):**
- [AzureKeyVaultWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Key%20Vault/Workbooks/AzureKeyVaultWorkbook.json)

**In solution [Azure SQL Database solution for sentinel](../solutions/azure-sql-database-solution-for-sentinel.md):**
- [Workbook-AzureSQLSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Workbooks/Workbook-AzureSQLSecurity.json)

**In solution [Azure kubernetes Service](../solutions/azure-kubernetes-service.md):**
- [AksSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Workbooks/AksSecurity.json)

**In solution [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md):**
- [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [DORA Compliance](../solutions/dora-compliance.md):**
- [DORACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance/Workbooks/DORACompliance.json)

**In solution [ExtraHop](../solutions/extrahop.md):**
- [ExtraHopDetectionsOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Workbooks/ExtraHopDetectionsOverview.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [Infoblox](../solutions/infoblox.md):**
- [Infoblox_Lookup_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Workbooks/Infoblox_Lookup_Workbook.json)
- [Infoblox_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Workbooks/Infoblox_Workbook.json)

**In solution [Infoblox SOC Insights](../solutions/infoblox-soc-insights.md):**
- [InfobloxSOCInsightsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Workbooks/InfobloxSOCInsightsWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForIdentity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForIdentity.json)
- [MicrosoftDefenderForOffice365detectionsandinsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json)

**In solution [Microsoft Defender for Cloud Apps](../solutions/microsoft-defender-for-cloud-apps.md):**
- [MicrosoftCloudAppSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps/Workbooks/MicrosoftCloudAppSecurity.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

**In solution [ReversingLabs](../solutions/reversinglabs.md):**
- [ReversingLabs-CapabilitiesOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReversingLabs/Workbooks/ReversingLabs-CapabilitiesOverview.json)

**In solution [SOC Handbook](../solutions/soc-handbook.md):**
- [AnalyticsEfficiency](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AnalyticsEfficiency.json)
- [AzureSentinelSecurityAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AzureSentinelSecurityAlerts.json)
- [IncidentOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/IncidentOverview.json)
- [InvestigationInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json)
- [MITREAttack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/MITREAttack.json)
- [SentinelCentral](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/SentinelCentral.json)

**In solution [SentinelSOARessentials](../solutions/sentinelsoaressentials.md):**
- [IncidentOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Workbooks/IncidentOverview.json)

**In solution [ThreatAnalysis&Response](../solutions/threatanalysis&response.md):**
- [DynamicThreatModeling&Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/DynamicThreatModeling%26Response.json)
- [ThreatAnalysis&Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatAnalysis%26Response/Workbooks/ThreatAnalysis%26Response.json)

**In solution [Web Session Essentials](../solutions/web-session-essentials.md):**
- [WebSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Session%20Essentials/Workbooks/WebSessionEssentials.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/securityinsights`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
