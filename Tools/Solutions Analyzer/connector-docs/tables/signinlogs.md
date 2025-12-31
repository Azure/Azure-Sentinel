# SigninLogs

Reference for SigninLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Azure Resources, Security |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs) |

## Solutions (29)

This table is used by the following solutions:

- [1Password](../solutions/1password.md)
- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md)
- [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md)
- [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md)
- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [FalconFriday](../solutions/falconfriday.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [GitLab](../solutions/gitlab.md)
- [HIPAA Compliance](../solutions/hipaa-compliance.md)
- [LastPass](../solutions/lastpass.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft 365](../solutions/microsoft-365.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [SOC Handbook](../solutions/soc-handbook.md)
- [SOX IT Compliance](../solutions/sox-it-compliance.md)
- [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md)
- [Teams](../solutions/teams.md)
- [UEBA Essentials](../solutions/ueba-essentials.md)
- [Windows Firewall](../solutions/windows-firewall.md)
- [Windows Server DNS](../solutions/windows-server-dns.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Entra ID](../connectors/azureactivedirectory.md)

---

## Content Items Using This Table (57)

### Analytic Rules (17)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [FalconFriday](../solutions/falconfriday.md):**
- [Expired access credentials being used in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/ExpiredAccessCredentials.yaml)

**In solution [GitLab](../solutions/gitlab.md):**
- [GitLab - SSO - Sign-Ins Burst](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GitLab/Analytic%20Rules/GitLab_SignInBurst.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress in SigninLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_SigninLogs.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Suspicious use of Web API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Suspicious%20use%20of%20Web%20API.yaml)
- [F&O - Unusual sign-in activity using single factor authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/F%26O%20-%20Unusual%20sign-in%20activity%20using%20single%20factor%20authentication.yaml)
- [Power Apps - App activity from unauthorized geo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Apps%20-%20App%20activity%20from%20unauthorized%20geo.yaml)
- [Power Platform - Possibly compromised user accesses Power Platform services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Platform%20-%20Possibly%20compromised%20user%20accesses%20Power%20Platform%20services.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Unusual Volume of file deletion by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Impact/AnomalousVoulmeOfFileDeletion.yaml)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [Brute force attack against a Cloud PC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/BruteForceCloudPC.yaml)
- [MFA Rejected by User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MFARejectedbyUser.yaml)
- [MFA Spamming followed by Successful login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MFASpammingfollowedbySuccessfullogin.yaml)
- [Possible SignIn from Azure Backdoor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PossibleSignInfromAzureBackdoor.yaml)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [Insider Risk_Risky User Access By Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskyAccessByApplication.yaml)

**In solution [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md):**
- [Cross-Cloud Password Spray detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/BrutforceAttemptOnAzurePortalAndAWSConsolAtSameTime.yaml)
- [Cross-Cloud Unauthorized Credential Access Detection From AWS RDS Login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/CrossCloudUnauthorizedCredentialsAccessDetection.yaml)
- [High-Risk Cross-Cloud User Impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/UserImpersonateByRiskyUser.yaml)

### Hunting Queries (23)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Login attempts using Legacy Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/LegacyAuthAttempt.yaml)
- [Microsoft Entra ID signins from new locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/new_locations_azuread_signin.yaml)
- [Risky Sign-in with new MFA method](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/riskSignInWithNewMFAMethod.yaml)
- [Successful Signin From Non-Compliant Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/SuccessfulSigninFromNon-CompliantDevice.yaml)
- [User Accounts - Unusual authentications occurring when countries do not conduct normal business operations.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserAccounts-UnusualLogonTimes.yaml)
- [User Login IP Address Teleportation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserLoginIPAddressTeleportation.yaml)

**In solution [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md):**
- [Detect Disabled Account Sign-in Attempts by Account Name](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/DisabledAccountSigninAttempts.yaml)
- [Detect Disabled Account Sign-in Attempts by IP Address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/DisabledAccountSigninAttemptsByIP.yaml)
- [Sign-ins From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-From-VPS-Providers.yaml)
- [Sign-ins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-from-NordVPN-Providers.yaml)

**In solution [LastPass](../solutions/lastpass.md):**
- [Login into LastPass from a previously unknown IP.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Hunting%20Queries/LoginIntoLastPassFromUnknownIP.yaml)

**In solution [Microsoft 365](../solutions/microsoft-365.md):**
- [SharePointFileOperation via devices with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_sharepoint_downloads_by_UserAgent.yaml)
- [SharePointFileOperation via previously unseen IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_sharepoint_downloads_by_IP.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Activity after failed logons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Activity%20after%20failed%20logons.yaml)
- [Dataverse - Generic client app used to access production environments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Generic%20client%20app%20used%20to%20access%20production%20environments.yaml)
- [Dataverse - Identity management changes without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Identity%20management%20changes%20without%20MFA.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Unusual Volume of file deletion by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Impact/AnomalousVoulmeOfFileDeletion.yaml)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [Insider Risk_Sign In Risk Followed By Sensitive Data Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderSignInRiskFollowedBySensitiveDataAccessyaml.yaml)

**In solution [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md):**
- [Threat Essentials - Signins From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Hunting%20Queries/Signins-From-VPS-Providers.yaml)
- [Threat Essentials - Signins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Hunting%20Queries/Signins-from-NordVPN-Providers.yaml)

**In solution [UEBA Essentials](../solutions/ueba-essentials.md):**
- [Anomalous Failed Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Failed%20Logon.yaml)
- [Anomalous Sign-in by New or Dormant Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Sign-in%20Activity.yaml)

**In solution [Windows Server DNS](../solutions/windows-server-dns.md):**
- [Solorigate Encoded Domain in URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Hunting%20Queries/Solorigate-Encoded-Domain-URL.yaml)

### Workbooks (17)

**In solution [1Password](../solutions/1password.md):**
- [1Password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Workbooks/1Password.json)

**In solution [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md):**
- [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [HIPAA Compliance](../solutions/hipaa-compliance.md):**
- [HIPAACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance/Workbooks/HIPAACompliance.json)

**In solution [LastPass](../solutions/lastpass.md):**
- [LastPassWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Workbooks/LastPassWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [AzureActiveDirectorySignins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/AzureActiveDirectorySignins.json)
- [ConditionalAccessSISM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/ConditionalAccessSISM.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [SOC Handbook](../solutions/soc-handbook.md):**
- [InvestigationInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json)

**In solution [SOX IT Compliance](../solutions/sox-it-compliance.md):**
- [SOXITCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json)

**In solution [Teams](../solutions/teams.md):**
- [MicrosoftTeams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Teams/Workbooks/MicrosoftTeams.json)

**In solution [Windows Firewall](../solutions/windows-firewall.md):**
- [WindowsFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Workbooks/WindowsFirewall.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.graph/tenants`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
