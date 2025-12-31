# Microsoft Business Applications

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-04-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Dynamics 365 Finance and Operations](../connectors/dynamics365finance.md)

## Tables Reference

This solution uses **16 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AuditLogs`](../tables/auditlogs.md) | - | Analytics |
| [`DataverseActivity`](../tables/dataverseactivity.md) | - | Analytics, Hunting, Workbooks |
| [`DataverseSharepointSites_data`](../tables/dataversesharepointsites-data.md) | - | Analytics |
| [`EmailEvents`](../tables/emailevents.md) | - | Analytics |
| [`FinanceOperationsActivity_CL`](../tables/financeoperationsactivity-cl.md) | [Dynamics 365 Finance and Operations](../connectors/dynamics365finance.md) | Analytics |
| [`MSBizAppsVIPUsers_data`](../tables/msbizappsvipusers-data.md) | - | Analytics |
| [`MsBizAppsNetworkAddresses_data`](../tables/msbizappsnetworkaddresses-data.md) | - | Analytics |
| [`OfficeActivity`](../tables/officeactivity.md) | - | Analytics |
| [`PowerAutomateActivity`](../tables/powerautomateactivity.md) | - | Analytics |
| [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) | - | Analytics, Hunting |
| [`Sensitive`](../tables/sensitive.md) | - | Analytics |
| [`SigninLogs`](../tables/signinlogs.md) | - | Analytics, Hunting |
| [`TerminatedEmployees_data`](../tables/terminatedemployees-data.md) | - | Analytics |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Analytics |
| [`dataverse_signin_activity`](../tables/dataverse-signin-activity.md) | - | Analytics |
| [`url_click_events`](../tables/url-click-events.md) | - | Analytics |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`IdentityInfo`](../tables/identityinfo.md) | - | Hunting |
| [`SecurityAlert`](../tables/securityalert.md) | - | Analytics, Hunting |

## Content Items

This solution includes **72 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 49 |
| Hunting Queries | 8 |
| Playbooks | 8 |
| Parsers | 5 |
| Workbooks | 1 |
| Watchlists | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Dataverse - Anomalous application user activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Anomalous%20application%20user%20activity.yaml) | Medium | CredentialAccess, Execution, Persistence | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Audit log data deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Audit%20log%20data%20deletion.yaml) | Low | DefenseEvasion | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Audit logging disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Audit%20logging%20disabled.yaml) | Low | DefenseEvasion | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Bulk record ownership re-assignment or sharing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Bulk%20record%20ownership%20re-assignment%20or%20sharing.yaml) | Medium | PrivilegeEscalation | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Executable uploaded to SharePoint document management site](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Executable%20uploaded%20to%20SharePoint%20document%20management%20site.yaml) | Low | Execution, Persistence | [`DataverseSharepointSites_data`](../tables/dataversesharepointsites-data.md)<br>[`OfficeActivity`](../tables/officeactivity.md) |
| [Dataverse - Export activity from terminated or notified employee](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Export%20activity%20from%20terminated%20or%20notified%20employee.yaml) | Medium | Exfiltration | [`TerminatedEmployees_data`](../tables/terminatedemployees-data.md) |
| [Dataverse - Guest user exfiltration following Power Platform defense impairment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Guest%20user%20exfiltration%20following%20Power%20Platform%20defense%20impairment.yaml) | High | DefenseEvasion, Exfiltration | [`AuditLogs`](../tables/auditlogs.md)<br>[`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) |
| [Dataverse - Hierarchy security manipulation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Hierarchy%20security%20manipulation.yaml) | Medium | PrivilegeEscalation | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Honeypot instance activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Honeypot%20instance%20activity.yaml) | Medium | Discovery, Exfiltration | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Login by a sensitive privileged user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Login%20by%20a%20sensitive%20privileged%20user.yaml) | High | InitialAccess, CredentialAccess, PrivilegeEscalation | [`MSBizAppsVIPUsers_data`](../tables/msbizappsvipusers-data.md)<br>[`Sensitive`](../tables/sensitive.md) |
| [Dataverse - Login from IP in the block list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Login%20from%20IP%20in%20the%20block%20list.yaml) | High | InitialAccess | [`MsBizAppsNetworkAddresses_data`](../tables/msbizappsnetworkaddresses-data.md) |
| [Dataverse - Login from IP not in the allow list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Login%20from%20IP%20not%20in%20the%20allow%20list.yaml) | High | InitialAccess | [`MsBizAppsNetworkAddresses_data`](../tables/msbizappsnetworkaddresses-data.md)<br>[`dataverse_signin_activity`](../tables/dataverse-signin-activity.md) |
| [Dataverse - Malware found in SharePoint document management site](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Malware%20found%20in%20SharePoint%20document%20management%20site.yaml) | Medium | Execution | [`OfficeActivity`](../tables/officeactivity.md) |
| [Dataverse - Mass deletion of records](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Mass%20deletion%20of%20records.yaml) | Medium | Impact | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Mass download from SharePoint document management](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Mass%20download%20from%20SharePoint%20document%20management.yaml) | Low | Exfiltration | [`DataverseSharepointSites_data`](../tables/dataversesharepointsites-data.md)<br>[`OfficeActivity`](../tables/officeactivity.md) |
| [Dataverse - Mass export of records to Excel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Mass%20export%20of%20records%20to%20Excel.yaml) | Low | Exfiltration | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Mass record updates](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Mass%20record%20updates.yaml) | Medium | Impact | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - New Dataverse application user activity type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20Dataverse%20application%20user%20activity%20type.yaml) | Medium | CredentialAccess, Execution, PrivilegeEscalation | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - New non-interactive identity granted access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20non-interactive%20identity%20granted%20access.yaml) | Informational | Persistence, LateralMovement, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md)<br>[`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - New sign-in from an unauthorized domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20sign-in%20from%20an%20unauthorized%20domain.yaml) | Medium | InitialAccess | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - New user agent type that was not used before](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20user%20agent%20type%20that%20was%20not%20used%20before.yaml) | Low | InitialAccess, DefenseEvasion | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - New user agent type that was not used with Office 365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20New%20user%20agent%20type%20that%20was%20not%20used%20with%20Office%20365.yaml) | Low | InitialAccess | [`DataverseActivity`](../tables/dataverseactivity.md)<br>[`OfficeActivity`](../tables/officeactivity.md) |
| [Dataverse - Organization settings modified](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Organization%20settings%20modified.yaml) | Informational | Persistence | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Removal of blocked file extensions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Removal%20of%20blocked%20file%20extensions.yaml) | Medium | DefenseEvasion | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - SharePoint document management site added or updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20SharePoint%20document%20management%20site%20added%20or%20updated.yaml) | Informational | Exfiltration | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Suspicious security role modifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Suspicious%20security%20role%20modifications.yaml) | Medium | PrivilegeEscalation | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Suspicious use of TDS endpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Suspicious%20use%20of%20TDS%20endpoint.yaml) | Low | Exfiltration, InitialAccess | [`DataverseActivity`](../tables/dataverseactivity.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Dataverse - Suspicious use of Web API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Suspicious%20use%20of%20Web%20API.yaml) | Medium | Execution, Exfiltration, Reconnaissance, Discovery | [`DataverseActivity`](../tables/dataverseactivity.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [Dataverse - TI map IP to DataverseActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20TI%20map%20IP%20to%20DataverseActivity.yaml) | Medium | InitialAccess, LateralMovement, Discovery | [`DataverseActivity`](../tables/dataverseactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Dataverse - TI map URL to DataverseActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20TI%20map%20URL%20to%20DataverseActivity.yaml) | Medium | InitialAccess, Execution, Persistence | [`DataverseActivity`](../tables/dataverseactivity.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Dataverse - Terminated employee exfiltration over email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Terminated%20employee%20exfiltration%20over%20email.yaml) | High | Exfiltration | [`EmailEvents`](../tables/emailevents.md)<br>[`TerminatedEmployees_data`](../tables/terminatedemployees-data.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Dataverse - Terminated employee exfiltration to USB drive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Terminated%20employee%20exfiltration%20to%20USB%20drive.yaml) | High | Exfiltration | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Unusual sign-in following disabled IP address-based cookie binding protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Unusual%20sign-in%20following%20disabled%20IP%20address-based%20cookie%20binding%20protection.yaml) | Medium | DefenseEvasion | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - User bulk retrieval outside normal activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20User%20bulk%20retrieval%20outside%20normal%20activity.yaml) | Low | Exfiltration | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [F&O - Bank account change following network alias reassignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/F%26O%20-%20Bank%20account%20change%20following%20network%20alias%20reassignment.yaml) | Low | CredentialAccess, LateralMovement, PrivilegeEscalation | [`FinanceOperationsActivity_CL`](../tables/financeoperationsactivity-cl.md) |
| [F&O - Mass update or deletion of user records](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/F%26O%20-%20Mass%20update%20or%20deletion%20of%20user%20records.yaml) | Medium | Impact | [`FinanceOperationsActivity_CL`](../tables/financeoperationsactivity-cl.md) |
| [F&O - Non-interactive account mapped to self or sensitive privileged user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/F%26O%20-%20Non-interactive%20account%20mapped%20to%20self%20or%20sensitive%20privileged%20user.yaml) | Medium | CredentialAccess, Persistence, PrivilegeEscalation | [`FinanceOperationsActivity_CL`](../tables/financeoperationsactivity-cl.md) |
| [F&O - Reverted bank account number modifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/F%26O%20-%20Reverted%20bank%20account%20number%20modifications.yaml) | Low | Impact | [`FinanceOperationsActivity_CL`](../tables/financeoperationsactivity-cl.md) |
| [F&O - Unusual sign-in activity using single factor authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/F%26O%20-%20Unusual%20sign-in%20activity%20using%20single%20factor%20authentication.yaml) | Low | CredentialAccess, InitialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Power Apps - App activity from unauthorized geo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Apps%20-%20App%20activity%20from%20unauthorized%20geo.yaml) | Low | InitialAccess | [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [Power Apps - Bulk sharing of Power Apps to newly created guest users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Apps%20-%20Bulk%20sharing%20of%20Power%20Apps%20to%20newly%20created%20guest%20users.yaml) | Medium | ResourceDevelopment, InitialAccess, LateralMovement | [`AuditLogs`](../tables/auditlogs.md)<br>[`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) |
| [Power Apps - Multiple apps deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Apps%20-%20Multiple%20apps%20deleted.yaml) | Medium | Impact | [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) |
| [Power Apps - Multiple users access a malicious link after launching new app](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Apps%20-%20Multiple%20users%20access%20a%20malicious%20link%20after%20launching%20new%20app.yaml) | High | InitialAccess | [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md)<br>[`url_click_events`](../tables/url-click-events.md) |
| [Power Automate - Departing employee flow activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Automate%20-%20Departing%20employee%20flow%20activity.yaml) | High | Exfiltration, Impact | [`PowerAutomateActivity`](../tables/powerautomateactivity.md) |
| [Power Automate - Unusual bulk deletion of flow resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Automate%20-%20Unusual%20bulk%20deletion%20of%20flow%20resources.yaml) | Medium | Impact, DefenseEvasion | [`PowerAutomateActivity`](../tables/powerautomateactivity.md) |
| [Power Platform - Account added to privileged Microsoft Entra roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Platform%20-%20Account%20added%20to%20privileged%20Microsoft%20Entra%20roles.yaml) | Low | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Power Platform - Connector added to a sensitive environment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Platform%20-%20Connector%20added%20to%20a%20sensitive%20environment.yaml) | Low | Execution, Exfiltration | [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) |
| [Power Platform - DLP policy updated or removed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Platform%20-%20DLP%20policy%20updated%20or%20removed.yaml) | Low | DefenseEvasion | [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) |
| [Power Platform - Possibly compromised user accesses Power Platform services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Power%20Platform%20-%20Possibly%20compromised%20user%20accesses%20Power%20Platform%20services.yaml) | High | InitialAccess, LateralMovement | [`SigninLogs`](../tables/signinlogs.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Dataverse - Activity after Microsoft Entra alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Activity%20after%20Microsoft%20Entra%20alerts.yaml) | InitialAccess | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Dataverse - Activity after failed logons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Activity%20after%20failed%20logons.yaml) | InitialAccess | [`DataverseActivity`](../tables/dataverseactivity.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [Dataverse - Cross-environment data export activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Cross-environment%20data%20export%20activity.yaml) | Exfiltration, Collection | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Dataverse export copied to USB devices](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Dataverse%20export%20copied%20to%20USB%20devices.yaml) | Exfiltration | [`DataverseActivity`](../tables/dataverseactivity.md) |
| [Dataverse - Generic client app used to access production environments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Generic%20client%20app%20used%20to%20access%20production%20environments.yaml) | Execution | [`SigninLogs`](../tables/signinlogs.md) |
| [Dataverse - Identity management activity outside of privileged directory role membership](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Identity%20management%20activity%20outside%20of%20privileged%20directory%20role%20membership.yaml) | PrivilegeEscalation | *Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Dataverse - Identity management changes without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Dataverse%20-%20Identity%20management%20changes%20without%20MFA.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Power Apps - Anomalous bulk sharing of Power App to newly created guest users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Hunting%20Queries/Power%20Apps%20-%20Anomalous%20bulk%20sharing%20of%20Power%20App%20to%20newly%20created%20guest%20users.yaml) | InitialAccess, LateralMovement, ResourceDevelopment | [`PowerPlatformAdminActivity`](../tables/powerplatformadminactivity.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Dynamics365Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Workbooks/Dynamics365Activity.json) | [`DataverseActivity`](../tables/dataverseactivity.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Dataverse: Add SharePoint sites to watchlist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Add-SharePoint-Site/azuredeploy.json) | This playbook is used to add new or updated SharePoint document management sites into the configurat... | - |
| [Dataverse: Add user to blocklist (alert trigger)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Blocklist-Add-User-AlertTrigger/azuredeploy.json) | This playbook can be triggered on-demand when a Microsoft Sentinel alert is raised, allowing the ana... | - |
| [Dataverse: Add user to blocklist (incident trigger)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Blocklist-Add-User/azuredeploy.json) | This playbook can be triggered when a Microsoft Sentinel incident is raised and will automatically a... | - |
| [Dataverse: Add user to blocklist using Outlook approval workflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Blocklist-Add-User-Via-Outlook/azuredeploy.json) | This playbook can be triggered when a Microsoft Sentinel incident is raised and will automatically a... | - |
| [Dataverse: Add user to blocklist using Teams approval workflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Blocklist-Add-User-Via-Teams/azuredeploy.json) | This playbook can be triggered when a Microsoft Sentinel incident is raised and will automatically a... | - |
| [Dataverse: Remove user from blocklist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Blocklist-Remove-User-AlertTrigger/azuredeploy.json) | This playbook can be triggered on-demand when a Microsoft Sentinel alert is raised, allowing the ana... | - |
| [Dataverse: Send notification to manager](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/Dataverse-Send-Manager-Notification/azuredeploy.json) | This playbook can be triggered when a Microsoft Sentinel incident is raised and will automatically s... | - |
| [Security workflow: alert verification with workload owners](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Playbooks/MSBizApps-Incident-From-Alert-Teams/azuredeploy.json) | This playbook can reduce burden on the SOC by offloading alert verification to IT admins for specifi... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DataverseSharePointSites](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Parsers/DataverseSharePointSites.yaml) | - | - |
| [MSBizAppsNetworkAddresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Parsers/MSBizAppsNetworkAddresses.yaml) | - | - |
| [MSBizAppsOrgSettings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Parsers/MSBizAppsOrgSettings.yaml) | - | - |
| [MSBizAppsTerminatedEmployees](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Parsers/MSBizAppsTerminatedEmployees.yaml) | - | - |
| [MSBizAppsVIPUsers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Parsers/MSBizAppsVIPUsers.yaml) | - | - |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [MSBizApps-Configuration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Watchlists/MSBizApps-Configuration.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                  |
|-------------|--------------------------------|---------------------------------------------------------------------|
| 3.2.2       | 22-04-2025                     |<ul><li>Updated solution description.</li></ul> |
| 3.2.1       | 11-04-2025                     |<ul><li>Move solution and content to GA.</li><li>Minor analytic rule update.</li></ul> |
| 3.2.0       | 15-11-2024                     | <ul><li>Renamed solution from Power Platform to Microsoft Business Applications.</li><li>Merge Dynamics 365 CE Apps and Dynamics 365 Finance & Operations into a unified solution.</li><li>New analytics rules, playbooks and hunting queries.</li><li>Replace Dynamics 365 Finance and Operations function app using Codeless Connector.</li><li>Retire PPInventory function app.</li></ul>|
| 3.1.3       | 12-07-2024                     |<ul><li>Removal of Power Apps, Power Platform Connectors, Power Platform DLP data connectors. Associated logs are now ingested via Power Platform Admin Activity data connector.</li><li>Update of analytics rules to utilize PowerPlatfromAdminActivity table.</li><li>Update data connectors DCR properties.</li></ul> |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
