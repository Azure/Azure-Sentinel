# IdentityInfo

Account information from various sources, including Microsoft Entra ID

| Attribute | Value |
|:----------|:------|
| **Category** | Internal |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-identityinfo-table) |

## Solutions (13)

This table is used by the following solutions:

- [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md)
- [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)
- [Microsoft Entra ID Protection](../solutions/microsoft-entra-id-protection.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [UEBA Essentials](../solutions/ueba-essentials.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

---

## Content Items Using This Table (28)

### Analytic Rules (9)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Local Admin Group Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/LocalAdminGroupChanges.yaml)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [Authentication Methods Changed for Privileged Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AuthenticationMethodsChangedforPrivilegedAccount.yaml)
- [MFA Rejected by User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MFARejectedbyUser.yaml)
- [Privileged Accounts - Sign in Failure Spikes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PrivilegedAccountsSigninFailureSpikes.yaml)
- [Successful logon from IP and failure from a different IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuccessThenFail_DiffIP_SameUserandApp.yaml)
- [User Accounts - Sign in Failure due to CA Spikes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAccounts-CABlockedSigninSpikes.yaml)

**In solution [Microsoft Entra ID Protection](../solutions/microsoft-entra-id-protection.md):**
- [Correlate Unfamiliar sign-in properties & atypical travel alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Analytic%20Rules/CorrelateIPC_Unfamiliar-Atypical.yaml)

**In solution [Multi Cloud Attack Coverage Essentials - Resource Abuse](../solutions/multi-cloud-attack-coverage-essentials---resource-abuse.md):**
- [Successful AWS Console Login from IP Address Observed Conducting Password Spray](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuccessfulAWSConsoleLoginfromIPAddressObservedConductingPasswordSpray.yaml)
- [Suspicious AWS console logins by credential access alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuspiciousAWSConsolLoginByCredentialAceessAlerts.yaml)

### Hunting Queries (14)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Login attempts using Legacy Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/LegacyAuthAttempt.yaml)
- [Microsoft Entra ID signins from new locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/new_locations_azuread_signin.yaml)
- [Risky Sign-in with new MFA method](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/riskSignInWithNewMFAMethod.yaml)
- [Successful Signin From Non-Compliant Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/SuccessfulSigninFromNon-CompliantDevice.yaml)
- [User Accounts - Unusual authentications occurring when countries do not conduct normal business operations.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserAccounts-UnusualLogonTimes.yaml)
- [User Login IP Address Teleportation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserLoginIPAddressTeleportation.yaml)

**In solution [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md):**
- [Detect Disabled Account Sign-in Attempts by Account Name](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/DisabledAccountSigninAttempts.yaml)
- [Sign-ins From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-From-VPS-Providers.yaml)
- [Sign-ins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/Signins-from-NordVPN-Providers.yaml)
- [Suspicious Sign-ins to Privileged Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/SuspiciousSignintoPrivilegedAccount.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Identity management activity outside of privileged directory role membership](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Identity%20management%20activity%20outside%20of%20privileged%20directory%20role%20membership.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Local Admin Group Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/LocalAdminGroupChanges.yaml)
- [User not covered under display name impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/User%20not%20covered%20under%20display%20name%20impersonation.yaml)

**In solution [UEBA Essentials](../solutions/ueba-essentials.md):**
- [Anomalous connection from highly privileged user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20connection%20from%20highly%20privileged%20user.yaml)

### Workbooks (5)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
