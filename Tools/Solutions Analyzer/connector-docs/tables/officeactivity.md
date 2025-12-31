# OfficeActivity

Reference for OfficeActivity table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Office 365 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/officeactivity) |

## Solutions (24)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [Global Secure Access](../solutions/global-secure-access.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft 365](../solutions/microsoft-365.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Exchange Security - Exchange Online](../solutions/microsoft-exchange-security---exchange-online.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [Recorded Future](../solutions/recorded-future.md)
- [SOX IT Compliance](../solutions/sox-it-compliance.md)
- [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md)
- [Teams](../solutions/teams.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatConnect](../solutions/threatconnect.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft 365 (formerly, Office 365)](../connectors/office365.md)

---

## Content Items Using This Table (76)

### Analytic Rules (30)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Malicious BEC Inbox Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/BEC_MailboxRule.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntHash.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI map IP entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_OfficeActivity.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress in OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_OfficeActivity.yaml)

**In solution [Microsoft 365](../solutions/microsoft-365.md):**
- [Accessed files shared by temporary external user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/External%20User%20added%20to%20Team%20and%20immediately%20uploads%20file.yaml)
- [Exchange AuditLog Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/exchange_auditlogdisabled.yaml)
- [Exchange workflow MailItemsAccessed operation anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/MailItemsAccessedTimeSeries.yaml)
- [External user added and removed in short timeframe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/ExternalUserAddedRemovedInTeams.yaml)
- [Mail redirect via ExO transport rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Mail_redirect_via_ExO_transport_rule.yaml)
- [Malicious Inbox Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Malicious_Inbox_Rule.yaml)
- [Multiple Teams deleted by a single user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/MultipleTeamsDeletes.yaml)
- [Multiple users email forwarded to same destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Office_MailForwarding.yaml)
- [New executable via Office FileUploaded Operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Office_Uploaded_Executables.yaml)
- [Office Policy Tampering](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/office_policytampering.yaml)
- [Office365 Sharepoint File transfer Folders above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/sharepoint_file_transfer_folders_above_threshold.yaml)
- [Office365 Sharepoint File transfer above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/sharepoint_file_transfer_above_threshold.yaml)
- [Rare and potentially high-risk Office operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/RareOfficeOperations.yaml)
- [SharePointFileOperation via devices with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/SharePoint_Downloads_byNewUserAgent.yaml)
- [SharePointFileOperation via previously unseen IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/SharePoint_Downloads_byNewIP.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Executable uploaded to SharePoint document management site](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Executable%20uploaded%20to%20SharePoint%20document%20management%20site.yaml)
- [Dataverse - Malware found in SharePoint document management site](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Malware%20found%20in%20SharePoint%20document%20management%20site.yaml)
- [Dataverse - Mass download from SharePoint document management](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Mass%20download%20from%20SharePoint%20document%20management.yaml)
- [Dataverse - New user agent type that was not used with Office 365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20user%20agent%20type%20that%20was%20not%20used%20with%20Office%20365.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingHashAllActors.yaml)

**In solution [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md):**
- [Threat Essentials - Mail redirect via ExO transport rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_Mail_redirect_via_ExO_transport_rule.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/EmailEntity_OfficeActivity.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/EmailEntity_OfficeActivity.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI Map URL Entity to OfficeActivity Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_URLEntity_OfficeActivity.yaml)
- [ThreatConnect TI map Email entity to OfficeActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_EmailEntity_OfficeActivity.yaml)

### Hunting Queries (31)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Office Mail Rule Creation with suspicious archive mail move activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/OfficeMailRuleCreationWithMailMoveActivity.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntHash.yaml)

**In solution [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md):**
- [Dev-0322 File Drop Activity November 2021 (ASIM Version)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/Dev-0322FileDropActivityNovember2021%28ASIMVersion%29.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect File Creation in Startup Folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/FileCretaedInStartupFolder.yaml)
- [Detect Files with Ramsomware Extensions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/FilesWithRansomwareExtensions.yaml)
- [Detect Modification to System Files or Directories by User Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/SystemFilesModifiedByUser.yaml)
- [Detect New Scheduled Task Entry Creations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/NewScheduledTaskCreation.yaml)
- [Executable Files Created in Uncommon Locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/ExecutableInUncommonLocation.yaml)

**In solution [Microsoft 365](../solutions/microsoft-365.md):**
- [Anomalous access to other users' mailboxes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/AnomolousUserAccessingOtherUsersMailbox.yaml)
- [Bots added to multiple teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultiTeamBot.yaml)
- [Exes with double file extension and access summary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/double_file_ext_exes.yaml)
- [External user added and removed in a short timeframe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/ExternalUserAddedRemovedInTeams_HuntVersion.yaml)
- [External user from a new organisation added to Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/ExternalUserFromNewOrgAddedToTeams.yaml)
- [Files uploaded to teams and access summary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/TeamsFilesUploaded.yaml)
- [Mail redirect via ExO transport rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/Mail_redirect_via_ExO_transport_rule_hunting.yaml)
- [Multiple Teams deleted by a single user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultipleTeamsDeletes.yaml)
- [Multiple users email forwarded to same destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultipleUsersEmailForwardedToSameDestination.yaml)
- [New Admin account activity seen which was not seen historically](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_adminaccountactivity.yaml)
- [New Windows Reserved Filenames staged on Office file services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/New_WindowsReservedFileNamesOnOfficeFileServices.yaml)
- [Non-owner mailbox login activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/nonowner_MailboxLogin.yaml)
- [Office Mail Forwarding - Hunting Version](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/OfficeMailForwarding_hunting.yaml)
- [PowerShell or non-browser mailbox login activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/powershell_or_nonbrowser_MailboxLogin.yaml)
- [Previously unseen bot or application added to Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/NewBotAddedToTeams.yaml)
- [SharePointFileOperation via clientIP with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/sharepoint_downloads.yaml)
- [SharePointFileOperation via devices with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_sharepoint_downloads_by_UserAgent.yaml)
- [SharePointFileOperation via previously unseen IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_sharepoint_downloads_by_IP.yaml)
- [User added to Teams and immediately uploads file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/UserAddToTeamsAndUploadsFile.yaml)
- [Windows Reserved Filenames staged on Office file services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/WindowsReservedFileNamesOnOfficeFileServices.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureHashThreatActorHunt.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map File Entity to OfficeActivity Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_OfficeActivity.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map File Entity to OfficeActivity Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_OfficeActivity.yaml)

### Workbooks (15)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [Global Secure Access](../solutions/global-secure-access.md):**
- [GSAM365EnrichedEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Global%20Secure%20Access/Workbooks/GSAM365EnrichedEvents.json)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft 365](../solutions/microsoft-365.md):**
- [ExchangeOnline](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Workbooks/ExchangeOnline.json)
- [Office365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Workbooks/Office365.json)
- [SharePointAndOneDrive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Workbooks/SharePointAndOneDrive.json)

**In solution [Microsoft Exchange Security - Exchange Online](../solutions/microsoft-exchange-security---exchange-online.md):**
- [Microsoft Exchange Admin Activity - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Admin%20Activity%20-%20Online.json)
- [Microsoft Exchange Search AdminAuditLog - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Search%20AdminAuditLog%20-%20Online.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [SOX IT Compliance](../solutions/sox-it-compliance.md):**
- [SOXITCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json)

**In solution [Teams](../solutions/teams.md):**
- [MicrosoftTeams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Teams/Workbooks/MicrosoftTeams.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
