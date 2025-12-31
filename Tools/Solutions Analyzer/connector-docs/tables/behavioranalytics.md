# BehaviorAnalytics

Reference for BehaviorAnalytics table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Internal |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/behavioranalytics) |

## Solutions (11)

This table is used by the following solutions:

- [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md)
- [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md)
- [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [SOC Handbook](../solutions/soc-handbook.md)
- [UEBA Essentials](../solutions/ueba-essentials.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

---

## Content Items Using This Table (43)

### Analytic Rules (5)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [MFA Rejected by User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MFARejectedbyUser.yaml)
- [Sign-ins from IPs that attempt sign-ins to disabled accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SigninAttemptsByIPviaDisabledAccounts.yaml)
- [Successful logon from IP and failure from a different IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuccessThenFail_DiffIP_SameUserandApp.yaml)
- [Suspicious Sign In Followed by MFA Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousSignInFollowedByMFAModification.yaml)
- [User Accounts - Sign in Failure due to CA Spikes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAccounts-CABlockedSigninSpikes.yaml)

### Hunting Queries (31)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Login attempts using Legacy Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/LegacyAuthAttempt.yaml)
- [Risky Sign-in with new MFA method](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/riskSignInWithNewMFAMethod.yaml)
- [Successful Signin From Non-Compliant Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/SuccessfulSigninFromNon-CompliantDevice.yaml)
- [User Accounts - New Single Factor Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserAccounts-NewSingleFactorAuth.yaml)
- [User Login IP Address Teleportation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserLoginIPAddressTeleportation.yaml)

**In solution [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md):**
- [Sign-ins From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-From-VPS-Providers.yaml)
- [Sign-ins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-from-NordVPN-Providers.yaml)
- [Suspicious Sign-ins to Privileged Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/SuspiciousSignintoPrivilegedAccount.yaml)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [Insider Risk_ISP Anomaly to Exfil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderISPAnomalyCorrelatedToExfiltrationAlert.yaml)
- [Insider Risk_Multiple Entity-Based Anomalies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderMultipleEntityAnomalies.yaml)

**In solution [UEBA Essentials](../solutions/ueba-essentials.md):**
- [Anomalies on users tagged as VIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/anomaliesOnVIPUsers.yaml)
- [Anomalous AWS Console Login Without MFA from Uncommon Country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20AWS%20Console%20Login%20Without%20MFA%20from%20Uncommon%20Country.yaml)
- [Anomalous Activity Role Assignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Activity%20Role%20Assignment.yaml)
- [Anomalous Code Execution on a Virtual Machine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Code%20Execution.yaml)
- [Anomalous Database Export Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Database%20Export%20Activity.yaml)
- [Anomalous Database Vulnerability Baseline Removal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Database%20Vulnerability%20Baseline%20Removal.yaml)
- [Anomalous Failed Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Failed%20Logon.yaml)
- [Anomalous First-Time Device Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20First-Time%20Device%20Logon.yaml)
- [Anomalous GCP IAM Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20GCP%20IAM%20Activity.yaml)
- [Anomalous Geo Location Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Geo%20Location%20Logon.yaml)
- [Anomalous Key Vault Modification by High-Privilege User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/updateKeyVaultActivity.yaml)
- [Anomalous Microsoft Entra ID Account Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Account%20Creation.yaml)
- [Anomalous Okta First-Time or Uncommon Actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Okta%20First-Time%20or%20Uncommon%20Actions.yaml)
- [Anomalous Password Reset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Password%20Reset.yaml)
- [Anomalous RDP Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20RDP%20Activity.yaml)
- [Anomalous Resource Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Resource%20Access.yaml)
- [Anomalous Sign-in by New or Dormant Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Sign-in%20Activity.yaml)
- [Anomalous action performed in tenant by privileged user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/anomalousActionInTenant.yaml)
- [Anomalous login activity originated from Botnet, Tor proxy or C2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/loginActivityFromBotnet.yaml)
- [Dormant Local Admin Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Dormant%20Local%20Admin%20Logon.yaml)
- [Dormant account activity from uncommon country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/dormantAccountActivityFromUncommonCountry.yaml)

### Workbooks (7)

**In solution [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md):**
- [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [SOC Handbook](../solutions/soc-handbook.md):**
- [InvestigationInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
