# AuditLogs

Reference for AuditLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Azure Resources, Security |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs) |

## Solutions (15)

This table is used by the following solutions:

- [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md)
- [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md)
- [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md)
- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [SOX IT Compliance](../solutions/sox-it-compliance.md)
- [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md)
- [UEBA Essentials](../solutions/ueba-essentials.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Entra ID](../connectors/azureactivedirectory.md)

---

## Content Items Using This Table (78)

### Analytic Rules (60)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Account Elevated to New Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/AccountElevatedtoNewRole.yaml)
- [User Added to Admin Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/UserAddedtoAdminRole.yaml)

**In solution [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md):**
- [New External User Granted Admin Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Analytic%20Rules/NewExtUserGrantedAdmin.yaml)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Guest user exfiltration following Power Platform defense impairment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Guest%20user%20exfiltration%20following%20Power%20Platform%20defense%20impairment.yaml)
- [Dataverse - New non-interactive identity granted access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20non-interactive%20identity%20granted%20access.yaml)
- [Power Apps - Bulk sharing of Power Apps to newly created guest users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Apps%20-%20Bulk%20sharing%20of%20Power%20Apps%20to%20newly%20created%20guest%20users.yaml)
- [Power Platform - Account added to privileged Microsoft Entra roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Platform%20-%20Account%20added%20to%20privileged%20Microsoft%20Entra%20roles.yaml)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [Account Created and Deleted in Short Timeframe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AccountCreatedandDeletedinShortTimeframe.yaml)
- [Account created or deleted by non-approved user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AccountCreatedDeletedByNonApprovedUser.yaml)
- [Admin promotion after Role Management Application Permission Grant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AdminPromoAfterRoleMgmtAppPermissionGrant.yaml)
- [Azure RBAC (Elevate Access)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AzureRBAC.yaml)
- [Bulk Changes to Privileged Account Permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/BulkChangestoPrivilegedAccountPermissions.yaml)
- [Conditional Access - A Conditional Access Device platforms condition has changed (the Device platforms condition can be spoofed)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20Device%20platforms%20condition%20has%20changed%20%28the%20Device%20platforms%20condition%20can%20be%20spoofed%29.yaml)
- [Conditional Access - A Conditional Access app exclusion has changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20app%20exclusion%20has%20changed.yaml)
- [Conditional Access - A Conditional Access policy was deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20deleted.yaml)
- [Conditional Access - A Conditional Access policy was disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20disabled.yaml)
- [Conditional Access - A Conditional Access policy was put into report-only mode](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20put%20into%20report-only%20mode.yaml)
- [Conditional Access - A Conditional Access policy was updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20updated.yaml)
- [Conditional Access - A Conditional Access user/group/role exclusion has changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20usergrouprole%20exclusion%20has%20changed.yaml)
- [Conditional Access - A new Conditional Access policy was created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20new%20Conditional%20Access%20policy%20was%20created.yaml)
- [Conditional Access - Dynamic Group Exclusion Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20Dynamic%20Group%20Exclusion%20Changes.yaml)
- [Credential added after admin consented to Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/CredentialAddedAfterAdminConsent.yaml)
- [Cross-tenant Access Settings Organization Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationAdded.yaml)
- [Cross-tenant Access Settings Organization Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationDeleted.yaml)
- [Cross-tenant Access Settings Organization Inbound Collaboration Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationInboundCollaborationSettingsChanged.yaml)
- [Cross-tenant Access Settings Organization Inbound Direct Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationInboundDirectSettingsChanged.yaml)
- [Cross-tenant Access Settings Organization Outbound Collaboration Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationOutboundCollaborationSettingsChanged.yaml)
- [Cross-tenant Access Settings Organization Outbound Direct Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationOutboundDirectSettingsChanged.yaml)
- [External guest invitation followed by Microsoft Entra ID PowerShell signin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UnusualGuestActivity.yaml)
- [First access credential added to Application or Service Principal where no credential was present](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/FirstAppOrServicePrincipalCredential.yaml)
- [Guest accounts added in Entra ID Groups other than the ones specified](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/GuestAccountsAddedinAADGroupsOtherThanTheOnesSpecified.yaml)
- [Mail.Read Permissions Granted to Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MailPermissionsAddedToApplication.yaml)
- [Microsoft Entra ID Role Management Permission Grant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AzureADRoleManagementPermissionGrant.yaml)
- [Modified domain federation trust settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ADFSDomainTrustMods.yaml)
- [Multiple admin membership removals from newly created admin.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MultipleAdmin_membership_removals_from_NewAdmin.yaml)
- [NRT Authentication Methods Changed for VIP Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_AuthenticationMethodsChangedforVIPUsers.yaml)
- [NRT First access credential added to Application or Service Principal where no credential was present](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/nrt_FirstAppOrServicePrincipalCredential.yaml)
- [NRT Modified domain federation trust settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_ADFSDomainTrustMods.yaml)
- [NRT New access credential added to Application or Service Principal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_NewAppOrServicePrincipalCredential.yaml)
- [NRT PIM Elevation Request Rejected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_PIMElevationRequestRejected.yaml)
- [NRT Privileged Role Assigned Outside PIM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_PrivlegedRoleAssignedOutsidePIM.yaml)
- [NRT User added to Microsoft Entra ID Privileged Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_UseraddedtoPrivilgedGroups.yaml)
- [New User Assigned to Privileged Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAssignedPrivilegedRole.yaml)
- [New access credential added to Application or Service Principal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NewAppOrServicePrincipalCredential.yaml)
- [New onmicrosoft domain added to tenant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NewOnmicrosoftDomainAdded.yaml)
- [PIM Elevation Request Rejected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PIMElevationRequestRejected.yaml)
- [Possible SignIn from Azure Backdoor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PossibleSignInfromAzureBackdoor.yaml)
- [Privileged Role Assigned Outside PIM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PrivlegedRoleAssignedOutsidePIM.yaml)
- [Rare application consent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/RareApplicationConsent.yaml)
- [Suspicious Entra ID Joined Device Update](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousAADJoinedDeviceUpdate.yaml)
- [Suspicious Service Principal creation activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousServicePrincipalcreationactivity.yaml)
- [Suspicious application consent for offline access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousOAuthApp_OfflineAccess.yaml)
- [Suspicious application consent similar to O365 Attack Toolkit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MaliciousOAuthApp_O365AttackToolkit.yaml)
- [Suspicious application consent similar to PwnAuth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MaliciousOAuthApp_PwnAuth.yaml)
- [User Assigned New Privileged Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAssignedNewPrivilegedRole.yaml)
- [User added to Microsoft Entra ID Privileged Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UseraddedtoPrivilgedGroups.yaml)
- [full_access_as_app Granted To Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ExchangeFullAccessGrantedToApp.yaml)

**In solution [SecurityThreatEssentialSolution](../solutions/securitythreatessentialsolution.md):**
- [Threat Essentials - Multiple admin membership removals from newly created admin.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_MultipleAdmin_membership_removals_from_NewAdmin.yaml)
- [Threat Essentials - NRT User added to Microsoft Entra ID Privileged Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_NRT_UseraddedtoPrivilgedGroups.yaml)
- [Threat Essentials - User Assigned Privileged Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_UserAssignedPrivilegedRole.yaml)

### Hunting Queries (7)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Risky Sign-in with new MFA method](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/riskSignInWithNewMFAMethod.yaml)
- [User detection added to privilege groups based in Watchlist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserDetectPrivilegeGroup.yaml)

**In solution [Cloud Identity Threat Protection Essentials](../solutions/cloud-identity-threat-protection-essentials.md):**
- [Application Granted EWS Permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/ApplicationGrantedEWSPermissions.yaml)
- [Interactive STS refresh token modifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/StsRefreshTokenModification.yaml)
- [User Granted Access and Grants Access to Other Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloud%20Identity%20Threat%20Protection%20Essentials/Hunting%20Queries/UserGrantedAccess_GrantsOthersAccess.yaml)

**In solution [UEBA Essentials](../solutions/ueba-essentials.md):**
- [Anomalous Entra High-Privilege Role Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Entra%20High-Privilege%20Role%20Modification.yaml)
- [Anomalous High-Privileged Role Assignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20High-Privileged%20Role%20Assignment.yaml)

### Workbooks (11)

**In solution [AzureSecurityBenchmark](../solutions/azuresecuritybenchmark.md):**
- [AzureSecurityBenchmark](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureSecurityBenchmark/Workbooks/AzureSecurityBenchmark.json)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [GDPR Compliance & Data Security](../solutions/gdpr-compliance-&-data-security.md):**
- [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [AzureActiveDirectoryAuditLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/AzureActiveDirectoryAuditLogs.json)
- [ConditionalAccessSISM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/ConditionalAccessSISM.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [SOX IT Compliance](../solutions/sox-it-compliance.md):**
- [SOXITCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.azureadgraph/tenants`
- `microsoft.graph/tenants`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
