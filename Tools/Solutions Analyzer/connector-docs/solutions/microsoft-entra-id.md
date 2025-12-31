# Microsoft Entra ID

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Entra ID](../connectors/azureactivedirectory.md)

## Tables Reference

This solution uses **28 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AADManagedIdentitySignInLogs`](../tables/aadmanagedidentitysigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`AADNonInteractiveUserSignInLogs`](../tables/aadnoninteractiveusersigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | Analytics, Workbooks |
| [`AADProvisioningLogs`](../tables/aadprovisioninglogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`AADRiskyServicePrincipals`](../tables/aadriskyserviceprincipals.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | Workbooks |
| [`AADRiskyUsers`](../tables/aadriskyusers.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`AADServicePrincipalRiskEvents`](../tables/aadserviceprincipalriskevents.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`AADServicePrincipalSignInLogs`](../tables/aadserviceprincipalsigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | Workbooks |
| [`AADUserRiskEvents`](../tables/aaduserriskevents.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`ADFSSignInLogs`](../tables/adfssigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | Analytics |
| [`AuditLogs`](../tables/auditlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | Analytics, Workbooks |
| [`DeviceInfo`](../tables/deviceinfo.md) | - | Analytics |
| [`EventInfo_Unseen`](../tables/eventinfo-unseen.md) | - | Analytics |
| [`ManagedIdentitySignInLogs`](../tables/managedidentitysigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`NetworkAccessTraffic`](../tables/networkaccesstraffic.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`NetworkAccessTrafficLogs`](../tables/networkaccesstrafficlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`NonInteractiveUserSignInLogs`](../tables/noninteractiveusersigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`ProvisioningLogs`](../tables/provisioninglogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`RareConsentBy`](../tables/rareconsentby.md) | - | Analytics |
| [`RiskyServicePrincipals`](../tables/riskyserviceprincipals.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`RiskyUsers`](../tables/riskyusers.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`ServicePrincipalRiskEvents`](../tables/serviceprincipalriskevents.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`ServicePrincipalSignInLogs`](../tables/serviceprincipalsigninlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`SignInLogs`](../tables/signinlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`SigninLogs`](../tables/signinlogs.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | Analytics, Workbooks |
| [`UserRiskEvents`](../tables/userriskevents.md) | [Microsoft Entra ID](../connectors/azureactivedirectory.md) | - |
| [`aadFunc`](../tables/aadfunc.md) | - | Analytics |
| [`awsFunc`](../tables/awsfunc.md) | - | Analytics |
| [`table`](../tables/table.md) | - | Analytics |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | - | Analytics |
| [`IdentityInfo`](../tables/identityinfo.md) | - | Analytics |

## Content Items

This solution includes **87 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 73 |
| Playbooks | 11 |
| Workbooks | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Account Created and Deleted in Short Timeframe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AccountCreatedandDeletedinShortTimeframe.yaml) | High | InitialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Account created or deleted by non-approved user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AccountCreatedDeletedByNonApprovedUser.yaml) | Medium | InitialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Admin promotion after Role Management Application Permission Grant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AdminPromoAfterRoleMgmtAppPermissionGrant.yaml) | High | PrivilegeEscalation, Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [Anomalous sign-in location by user account and authenticating application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AnomalousUserAppSigninLocationIncrease-detection.yaml) | Medium | InitialAccess | - |
| [Attempt to bypass conditional access rule in Microsoft Entra ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/BypassCondAccessRule.yaml) | Low | InitialAccess, Persistence | [`aadFunc`](../tables/aadfunc.md) |
| [Attempts to sign in to disabled accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/DisabledAccountSigninsAcrossManyApplications.yaml) | Medium | InitialAccess | [`aadFunc`](../tables/aadfunc.md) |
| [Authentication Methods Changed for Privileged Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AuthenticationMethodsChangedforPrivilegedAccount.yaml) | High | Persistence | *Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Azure Portal sign in from another Azure Tenant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AzurePortalSigninfromanotherAzureTenant.yaml) | Medium | InitialAccess | - |
| [Azure RBAC (Elevate Access)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AzureRBAC.yaml) | High | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Brute Force Attack against GitHub Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Brute%20Force%20Attack%20against%20GitHub%20Account.yaml) | Medium | CredentialAccess | [`aadFunc`](../tables/aadfunc.md) |
| [Brute force attack against Azure Portal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SigninBruteForce-AzurePortal.yaml) | Medium | CredentialAccess | [`aadFunc`](../tables/aadfunc.md) |
| [Brute force attack against a Cloud PC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/BruteForceCloudPC.yaml) | Medium | CredentialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Bulk Changes to Privileged Account Permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/BulkChangestoPrivilegedAccountPermissions.yaml) | High | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access Device platforms condition has changed (the Device platforms condition can be spoofed)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20Device%20platforms%20condition%20has%20changed%20%28the%20Device%20platforms%20condition%20can%20be%20spoofed%29.yaml) | Low | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access app exclusion has changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20app%20exclusion%20has%20changed.yaml) | Low | CommandAndControl | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access policy was deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20deleted.yaml) | Low | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access policy was disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20disabled.yaml) | Low | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access policy was put into report-only mode](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20put%20into%20report-only%20mode.yaml) | Low | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access policy was updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20policy%20was%20updated.yaml) | Informational | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A Conditional Access user/group/role exclusion has changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20Conditional%20Access%20usergrouprole%20exclusion%20has%20changed.yaml) | High | Persistence, DefenseEvasion, CredentialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - A new Conditional Access policy was created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20A%20new%20Conditional%20Access%20policy%20was%20created.yaml) | Informational | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Conditional Access - Dynamic Group Exclusion Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Conditional%20Access%20-%20Dynamic%20Group%20Exclusion%20Changes.yaml) | High | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Credential added after admin consented to Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/CredentialAddedAfterAdminConsent.yaml) | Medium | CredentialAccess, Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Cross-tenant Access Settings Organization Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationAdded.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Cross-tenant Access Settings Organization Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationDeleted.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Cross-tenant Access Settings Organization Inbound Collaboration Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationInboundCollaborationSettingsChanged.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Cross-tenant Access Settings Organization Inbound Direct Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationInboundDirectSettingsChanged.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Cross-tenant Access Settings Organization Outbound Collaboration Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationOutboundCollaborationSettingsChanged.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Cross-tenant Access Settings Organization Outbound Direct Settings Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Cross-tenantAccessSettingsOrganizationOutboundDirectSettingsChanged.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Distributed Password cracking attempts in Microsoft Entra ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/DistribPassCrackAttempt.yaml) | Medium | CredentialAccess | - |
| [External guest invitation followed by Microsoft Entra ID PowerShell signin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UnusualGuestActivity.yaml) | Medium | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [Failed login attempts to Azure Portal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/FailedLogonToAzurePortal.yaml) | Low | CredentialAccess | [`aadFunc`](../tables/aadfunc.md) |
| [First access credential added to Application or Service Principal where no credential was present](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/FirstAppOrServicePrincipalCredential.yaml) | High | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [GitHub Signin Burst from Multiple Locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/Sign-in%20Burst%20from%20Multiple%20Locations.yaml) | Medium | CredentialAccess | [`aadFunc`](../tables/aadfunc.md) |
| [Guest accounts added in Entra ID Groups other than the ones specified](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/GuestAccountsAddedinAADGroupsOtherThanTheOnesSpecified.yaml) | High | InitialAccess, Persistence, Discovery | [`AuditLogs`](../tables/auditlogs.md) |
| [MFA Rejected by User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MFARejectedbyUser.yaml) | Medium | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [MFA Spamming followed by Successful login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MFASpammingfollowedbySuccessfullogin.yaml) | High | CredentialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Mail.Read Permissions Granted to Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MailPermissionsAddedToApplication.yaml) | Medium | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [Microsoft Entra ID PowerShell accessing non-Entra ID resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AzureAADPowerShellAnomaly.yaml) | Low | InitialAccess | [`aadFunc`](../tables/aadfunc.md) |
| [Microsoft Entra ID Role Management Permission Grant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/AzureADRoleManagementPermissionGrant.yaml) | High | Persistence, Impact | [`AuditLogs`](../tables/auditlogs.md) |
| [Modified domain federation trust settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ADFSDomainTrustMods.yaml) | High | CredentialAccess, Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Multiple admin membership removals from newly created admin.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MultipleAdmin_membership_removals_from_NewAdmin.yaml) | Medium | Impact | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT Authentication Methods Changed for VIP Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_AuthenticationMethodsChangedforVIPUsers.yaml) | Medium | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT First access credential added to Application or Service Principal where no credential was present](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/nrt_FirstAppOrServicePrincipalCredential.yaml) | Medium | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT Modified domain federation trust settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_ADFSDomainTrustMods.yaml) | High | CredentialAccess, Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT New access credential added to Application or Service Principal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_NewAppOrServicePrincipalCredential.yaml) | Medium | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT PIM Elevation Request Rejected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_PIMElevationRequestRejected.yaml) | High | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT Privileged Role Assigned Outside PIM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_PrivlegedRoleAssignedOutsidePIM.yaml) | Low | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [NRT User added to Microsoft Entra ID Privileged Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NRT_UseraddedtoPrivilgedGroups.yaml) | Medium | Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [New User Assigned to Privileged Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAssignedPrivilegedRole.yaml) | High | Persistence | [`AuditLogs`](../tables/auditlogs.md)<br>[`EventInfo_Unseen`](../tables/eventinfo-unseen.md)<br>[`awsFunc`](../tables/awsfunc.md) |
| [New access credential added to Application or Service Principal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NewAppOrServicePrincipalCredential.yaml) | Medium | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [New onmicrosoft domain added to tenant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/NewOnmicrosoftDomainAdded.yaml) | Medium | ResourceDevelopment | [`AuditLogs`](../tables/auditlogs.md) |
| [PIM Elevation Request Rejected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PIMElevationRequestRejected.yaml) | High | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [Password spray attack against ADFSSignInLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ADFSSignInLogsPasswordSpray.yaml) | Medium | CredentialAccess | [`ADFSSignInLogs`](../tables/adfssigninlogs.md) |
| [Password spray attack against Microsoft Entra ID Seamless SSO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SeamlessSSOPasswordSpray.yaml) | Medium | CredentialAccess | [`AADNonInteractiveUserSignInLogs`](../tables/aadnoninteractiveusersigninlogs.md) |
| [Password spray attack against Microsoft Entra ID application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SigninPasswordSpray.yaml) | Medium | CredentialAccess | [`aadFunc`](../tables/aadfunc.md)<br>[`table`](../tables/table.md) |
| [Possible SignIn from Azure Backdoor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PossibleSignInfromAzureBackdoor.yaml) | Medium | Persistence | [`AuditLogs`](../tables/auditlogs.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [Privileged Accounts - Sign in Failure Spikes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PrivilegedAccountsSigninFailureSpikes.yaml) | High | InitialAccess | [`aadFunc`](../tables/aadfunc.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Privileged Role Assigned Outside PIM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/PrivlegedRoleAssignedOutsidePIM.yaml) | Low | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Rare application consent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/RareApplicationConsent.yaml) | Medium | Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md)<br>[`RareConsentBy`](../tables/rareconsentby.md) |
| [Sign-ins from IPs that attempt sign-ins to disabled accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SigninAttemptsByIPviaDisabledAccounts.yaml) | Medium | InitialAccess, Persistence | [`table`](../tables/table.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Successful logon from IP and failure from a different IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuccessThenFail_DiffIP_SameUserandApp.yaml) | Medium | CredentialAccess, InitialAccess | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Suspicious Entra ID Joined Device Update](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousAADJoinedDeviceUpdate.yaml) | Medium | CredentialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Suspicious Service Principal creation activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousServicePrincipalcreationactivity.yaml) | Low | CredentialAccess, PrivilegeEscalation, InitialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Suspicious Sign In Followed by MFA Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousSignInFollowedByMFAModification.yaml) | Medium | InitialAccess, DefenseEvasion | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Suspicious application consent for offline access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SuspiciousOAuthApp_OfflineAccess.yaml) | Low | CredentialAccess | [`AuditLogs`](../tables/auditlogs.md) |
| [Suspicious application consent similar to O365 Attack Toolkit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MaliciousOAuthApp_O365AttackToolkit.yaml) | High | CredentialAccess, DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [Suspicious application consent similar to PwnAuth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/MaliciousOAuthApp_PwnAuth.yaml) | Medium | CredentialAccess, DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |
| [User Accounts - Sign in Failure due to CA Spikes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAccounts-CABlockedSigninSpikes.yaml) | Medium | InitialAccess | [`aadFunc`](../tables/aadfunc.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [User Assigned New Privileged Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UserAssignedNewPrivilegedRole.yaml) | High | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [User added to Microsoft Entra ID Privileged Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/UseraddedtoPrivilgedGroups.yaml) | Medium | Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [[Deprecated] Explicit MFA Deny](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ExplicitMFADeny.yaml) | Medium | CredentialAccess | [`DeviceInfo`](../tables/deviceinfo.md)<br>[`aadFunc`](../tables/aadfunc.md) |
| [full_access_as_app Granted To Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ExchangeFullAccessGrantedToApp.yaml) | Medium | DefenseEvasion | [`AuditLogs`](../tables/auditlogs.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AzureActiveDirectoryAuditLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/AzureActiveDirectoryAuditLogs.json) | [`AuditLogs`](../tables/auditlogs.md) |
| [AzureActiveDirectorySignins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/AzureActiveDirectorySignins.json) | [`AADNonInteractiveUserSignInLogs`](../tables/aadnoninteractiveusersigninlogs.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [ConditionalAccessSISM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/ConditionalAccessSISM.json) | [`AADRiskyServicePrincipals`](../tables/aadriskyserviceprincipals.md)<br>[`AADServicePrincipalSignInLogs`](../tables/aadserviceprincipalsigninlogs.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`SigninLogs`](../tables/signinlogs.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block Entra ID user - Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Block-AADUser/incident-trigger/azuredeploy.json) | For each account entity included in the incident, this playbook will disable the user in Microsoft E... | - |
| [Block Microsoft Entra ID user - Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Block-AADUser/alert-trigger/azuredeploy.json) | For each account entity included in the alert, this playbook will disable the user in Microsoft Entr... | - |
| [Block Microsoft Entra ID user - Entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Block-AADUser/entity-trigger/azuredeploy.json) | This playbook disables the selected user (account entity) in Microsoft Entra ID. If this playbook tr... | - |
| [Prompt User - Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Prompt-User/alert-trigger/azuredeploy.json) | This playbook will ask the user if they completed the action from the alert in Microsoft Sentinel. I... | - |
| [Prompt User - Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Prompt-User/incident-trigger/azuredeploy.json) | This playbook will ask the user if they completed the action from the Incident in Microsoft Sentinel... | - |
| [Reset Microsoft Entra ID User Password - Alert Trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Reset-AADUserPassword/alert-trigger/azuredeploy.json) | This playbook will reset the user password using Graph API. It will send the password (which is a ra... | - |
| [Reset Microsoft Entra ID User Password - Entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Reset-AADUserPassword/entity-trigger/azuredeploy.json) | This playbook will reset the user password using Graph API. It will send the password (which is a ra... | - |
| [Reset Microsoft Entra ID User Password - Incident Trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Reset-AADUserPassword/incident-trigger/azuredeploy.json) | This playbook will reset the user password using Graph API. It will send the password (which is a ra... | - |
| [Revoke Entra ID  Sign-in session using entity trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Revoke-AADSignInSessions/entity-trigger/azuredeploy.json) | This playbook will revoke user's sign-in sessions and user will have to perform authentication again... | - |
| [Revoke Entra ID SignIn Sessions - incident trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Revoke-AADSignInSessions/incident-trigger/azuredeploy.json) | This playbook will revoke all signin sessions for the user using Graph API. It will send an email to... | - |
| [Revoke-Entra ID SignInSessions alert trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Playbooks/Revoke-AADSignInSessions/alert-trigger/azuredeploy.json) | This playbook will revoke all signin sessions for the user using Graph API. It will send an email to... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                                                                                                         |
| ----------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 3.3.7       | 04-12-2025                     | Updated Revoke-AADSignInSessions **Playbooks** Instructions |
| 3.3.6       | 23-09-2025                     | Updated  **Analytical Rule** to fix the rule saving issue. <br/> Removed Preview Designation from **Microsoft Entra ID Connector** Data Types.  | 
| 3.3.5       | 25-07-2025                     | Updated Entra id Conditional Access (prefix) **Analytical Rule** |
| 3.3.4       | 10-07-2025                     | Updated **Analytical Rule** NRT_UseraddedtoPrivilgedGroups.yaml and UseraddedtoPrivilgedGroups.yaml
| 3.3.3       | 03-06-2025                     | Updates to multiple **Playbooks** to improve documentation, streamline deployment instructions, and add links to detailed setup steps.							                    	   |
| 3.3.2       | 08-05-2025                     | Removed the IP entity type and its associated field mappings (Address and IPAddress) in *DistribPassCrackAttempt.yaml* **Analytic Rule**.								                   |
| 3.3.1       | 08-04-2025                     | Updated **Analytical Rule** [Anomalous sign-in location by user account and authenticating application]							                                                	   |
| 3.3.0       | 28-01-2025                     | Added new **Analytic Rule** AzureRBAC to the Solution.								                                                                                                    	|	    			
| 3.2.10      | 19-12-2024                     | Updated **Analytical Rule** MFARejectedbyUser.yaml.								                                                                                                        |	    			
| 3.2.9       | 27-08-2024                     | Updated **Analytical Rule** for missing TTP.	    																																		|
| 3.2.8       | 19-08-2024                     | Exclude Result Reason "RoleAssignmentExists" from **Analytic Rule** [NRT PIM Elevation Request Rejected].                						                                            |
| 3.2.7       | 12-06-2024                     | Fixed the bugs from **Analytic Rules**.        																																    		|
| 3.2.6       | 06-06-2024                     | Successful logon from IP and failure from a different IP fixes.       																												        |
| 3.2.5       | 28-05-2024                     | Updated Entity mappings and changed description in **Analytic Rule**.         																												|
| 3.2.4       | 21-03-2024                     | Used the make-series operator instead of Make_list.          																																|
| 3.2.3       | 13-03-2024                     | Removed uses of BlastRadius from query section of **Hunting Queries** where it was used incorrectly.																						|
| 3.2.2       | 13-03-2024                     | Updated **Analytic Rule** ExplicitMFADeny.                                                                                                                                  				|
| 3.2.1       | 16-02-2024                     | Fixed entity mapping of **Analytic Rule** NRT_NewAppOrServicePrincipalCredential.yaml.                                                                                                      |
| 3.2.0       | 05-02-2024                     | 1 **Analytic Rule** added PossibleSignInfromAzureBackdoor NRT_NewAppOrServicePrincipalCredential.                                                                                           |
| 3.0.11      | 17-01-2024                     | 1 **Analytic Rule** Fixed wrong capitalization for identifier ResourceId.                                                                                                                   |
| 3.0.10      | 26-12-2023                     | 1 **Analytic Rule** Modified by adding "GroupMembership" instead of "Admin" condition for better extraction of admin accounts from the identity infotable.                                 |
| 3.0.9       | 28-11-2023                     | 2 **Analytic Rules** Modified by Adding Entity Mapping to (GuestAccountsAddedinAADGroupsOtherThanTheOnesSpecified.yaml) and Changed timerange of (SigninPasswordSpray.yaml) from 3d to 1d. |
| 3.0.8       | 21-11-2023                     | 1 **Analytic Rules** Fixed issue that was causing multiple triggers for the same event.                                                                                                    |
| 3.0.7       | 06-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.                                                                                                    |
| 3.0.6       | 30-10-2023                     | 1 **Data Connector** added back in the solution.                                                                                                                                           |
| 3.0.5       | 19-10-2023                     | 1 **Analytic Rules** updated in the solution (PIMElevationRequestRejected).                                                                                                                |
| 3.0.4       | 16-10-2023                     | 1 **Analytic Rules** got added in the solution (SuspiciousSignInFollowedByMFAModification), modified workbook query to fix duplicate locations for the query.                              |
| 3.0.3       | 22-09-2023                     | 2 **Analytic Rules** updated in the solution (PIM Elevation Request Rejected),(NRT Authentication Methods Changed for VIP Users).                                                          |
| 3.0.2       | 08-08-2023                     | 1 **Analytic Rules** updated in the solution (Credential added after admin consented to Application).                                                                                      |
| 3.0.1       | 01-08-2023                     | Added new **Analytic Rule** (New onmicrosoft domain added to tenant).                                                                                                                      |
| 3.0.0       | 19-07-2023                     | 2 **Analytic Rules** updated in the solution (User Assigned Privileged Role,Successful logon from IP and failure from a different IP).                                                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
