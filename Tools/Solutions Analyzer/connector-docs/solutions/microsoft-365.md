# Microsoft 365

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft 365 (formerly, Office 365)](../connectors/office365.md)

## Tables Reference

This solution uses **9 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`OfficeActivity`](../tables/officeactivity.md) | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) | Analytics, Hunting, Workbooks |
| [`OperationsData`](../tables/operationsdata.md) | - | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | - | Hunting |
| [`TeamsAddDel`](../tables/teamsadddel.md) | - | Analytics |
| [`exchange`](../tables/exchange.md) | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) | - |
| [`recentActivity`](../tables/recentactivity.md) | - | Hunting |
| [`recentUA`](../tables/recentua.md) | - | Hunting |
| [`sharePoint`](../tables/sharepoint.md) | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) | - |
| [`teams`](../tables/teams.md) | [Microsoft 365 (formerly, Office 365)](../connectors/office365.md) | - |

## Content Items

This solution includes **40 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 21 |
| Analytic Rules | 16 |
| Workbooks | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Accessed files shared by temporary external user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/External%20User%20added%20to%20Team%20and%20immediately%20uploads%20file.yaml) | Low | InitialAccess | [`OfficeActivity`](../tables/officeactivity.md) |
| [Exchange AuditLog Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/exchange_auditlogdisabled.yaml) | Medium | DefenseEvasion | [`OfficeActivity`](../tables/officeactivity.md) |
| [Exchange workflow MailItemsAccessed operation anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/MailItemsAccessedTimeSeries.yaml) | Medium | Collection | [`OfficeActivity`](../tables/officeactivity.md) |
| [External user added and removed in short timeframe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/ExternalUserAddedRemovedInTeams.yaml) | Low | Persistence | [`OfficeActivity`](../tables/officeactivity.md)<br>[`TeamsAddDel`](../tables/teamsadddel.md) |
| [Mail redirect via ExO transport rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Mail_redirect_via_ExO_transport_rule.yaml) | Medium | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Malicious Inbox Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Malicious_Inbox_Rule.yaml) | Medium | Persistence, DefenseEvasion | [`OfficeActivity`](../tables/officeactivity.md) |
| [Multiple Teams deleted by a single user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/MultipleTeamsDeletes.yaml) | Low | Impact | [`OfficeActivity`](../tables/officeactivity.md) |
| [Multiple users email forwarded to same destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Office_MailForwarding.yaml) | Medium | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [New executable via Office FileUploaded Operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/Office_Uploaded_Executables.yaml) | Low | CommandAndControl, LateralMovement | [`OfficeActivity`](../tables/officeactivity.md) |
| [Office Policy Tampering](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/office_policytampering.yaml) | Medium | Persistence, DefenseEvasion | [`OfficeActivity`](../tables/officeactivity.md) |
| [Office365 Sharepoint File transfer Folders above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/sharepoint_file_transfer_folders_above_threshold.yaml) | Medium | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Office365 Sharepoint File transfer above threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/sharepoint_file_transfer_above_threshold.yaml) | Medium | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Rare and potentially high-risk Office operations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/RareOfficeOperations.yaml) | Low | Persistence, Collection | [`OfficeActivity`](../tables/officeactivity.md) |
| [SharePointFileOperation via devices with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/SharePoint_Downloads_byNewUserAgent.yaml) | Medium | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [SharePointFileOperation via previously unseen IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/SharePoint_Downloads_byNewIP.yaml) | Medium | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |

#### Retired/Deprecated Rules

| Name | Status | Description |
|:-----|:-------|:------------|
| [Possible Forest Blizzard attempted credential harvesting - Sept 2020](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Analytic%20Rules/ForestBlizzardCredHarvesting.yaml) | Retired | This analytic rule is retired because IoCs are outdated. It is recommended to use Microsoft Entra ID Solution's Analytic rules instead to detect crede... |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Anomalous access to other users' mailboxes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/AnomolousUserAccessingOtherUsersMailbox.yaml) | Collection | [`OfficeActivity`](../tables/officeactivity.md) |
| [Bots added to multiple teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultiTeamBot.yaml) | Persistence, Collection | [`OfficeActivity`](../tables/officeactivity.md) |
| [Exes with double file extension and access summary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/double_file_ext_exes.yaml) | DefenseEvasion | [`OfficeActivity`](../tables/officeactivity.md) |
| [External user added and removed in a short timeframe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/ExternalUserAddedRemovedInTeams_HuntVersion.yaml) | Persistence | [`OfficeActivity`](../tables/officeactivity.md) |
| [External user from a new organisation added to Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/ExternalUserFromNewOrgAddedToTeams.yaml) | Persistence | [`OfficeActivity`](../tables/officeactivity.md) |
| [Files uploaded to teams and access summary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/TeamsFilesUploaded.yaml) | InitialAccess, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Mail redirect via ExO transport rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/Mail_redirect_via_ExO_transport_rule_hunting.yaml) | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Multiple Teams deleted by a single user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultipleTeamsDeletes.yaml) | Impact | [`OfficeActivity`](../tables/officeactivity.md) |
| [Multiple users email forwarded to same destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultipleUsersEmailForwardedToSameDestination.yaml) | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [New Admin account activity seen which was not seen historically](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_adminaccountactivity.yaml) | PrivilegeEscalation, Collection | [`OfficeActivity`](../tables/officeactivity.md)<br>[`recentActivity`](../tables/recentactivity.md) |
| [New Windows Reserved Filenames staged on Office file services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/New_WindowsReservedFileNamesOnOfficeFileServices.yaml) | CommandAndControl | [`OfficeActivity`](../tables/officeactivity.md) |
| [Non-owner mailbox login activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/nonowner_MailboxLogin.yaml) | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Office Mail Forwarding - Hunting Version](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/OfficeMailForwarding_hunting.yaml) | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [PowerShell or non-browser mailbox login activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/powershell_or_nonbrowser_MailboxLogin.yaml) | Execution, Persistence, Collection | [`OfficeActivity`](../tables/officeactivity.md) |
| [Previously unseen bot or application added to Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/NewBotAddedToTeams.yaml) | Persistence, Collection | [`OfficeActivity`](../tables/officeactivity.md) |
| [SharePointFileOperation via clientIP with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/sharepoint_downloads.yaml) | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md)<br>[`recentUA`](../tables/recentua.md) |
| [SharePointFileOperation via devices with previously unseen user agents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_sharepoint_downloads_by_UserAgent.yaml) | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [SharePointFileOperation via previously unseen IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/new_sharepoint_downloads_by_IP.yaml) | Exfiltration | [`OfficeActivity`](../tables/officeactivity.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [User added to Teams and immediately uploads file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/UserAddToTeamsAndUploadsFile.yaml) | InitialAccess | [`OfficeActivity`](../tables/officeactivity.md) |
| [User made Owner of multiple teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/MultiTeamOwner.yaml) | PrivilegeEscalation | - |
| [Windows Reserved Filenames staged on Office file services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Hunting%20Queries/WindowsReservedFileNamesOnOfficeFileServices.yaml) | CommandAndControl | [`OfficeActivity`](../tables/officeactivity.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ExchangeOnline](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Workbooks/ExchangeOnline.json) | [`OfficeActivity`](../tables/officeactivity.md)<br>[`OperationsData`](../tables/operationsdata.md) |
| [Office365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Workbooks/Office365.json) | [`OfficeActivity`](../tables/officeactivity.md) |
| [SharePointAndOneDrive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20365/Workbooks/SharePointAndOneDrive.json) | [`OfficeActivity`](../tables/officeactivity.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 04-02-2025                     | Updated **Analytic Rule** MailItemsAccessedTimeSeries.yaml    |
| 3.0.4       | 27-08-2024                     | Updated **Analytic Rule**  for Same names     |
| 3.0.3       | 12-06-2024                     | Updated **Analytic Rule**  for Bug Fixes ExternalUserAddedRemovedInTeams.yaml      |
| 3.0.2       | 09-05-2024					   | Updated **Analytic Rule** to get expected result and Entity Mapping exchange_auditlogdisabled.yaml	and fixed typo description in **Analytic Rules** ExternalUserAddedRemovedInTeams.yaml	   |
| 3.0.1       | 04-01-2024                     | Updated **Analytic Rules**, **Hunting Queries** and **Workbook** for Bug Fixes |
| 3.0.0       | 08-08-2023                     | Renamed **Data Connector** in the solution to Microsoft 365 (formerly, Office 365) so that the naming aligns in Content Hub and Data Connector gallery.<br/> Updated **Hunting Queries** to have descriptions that meet the 255 characters limit.      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
