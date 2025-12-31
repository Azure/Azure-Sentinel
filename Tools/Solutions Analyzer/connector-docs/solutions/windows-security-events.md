# Windows Security Events

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Security Events via Legacy Agent](../connectors/securityevents.md)
- [Windows Security Events via AMA](../connectors/windowssecurityevents.md)

## Tables Reference

This solution uses **9 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Combined`](../tables/combined.md) | - | Hunting |
| [`Event`](../tables/event.md) | - | Analytics, Hunting |
| [`LogonEvents`](../tables/logonevents.md) | - | Hunting |
| [`ProcessCreationEvents`](../tables/processcreationevents.md) | - | Hunting |
| [`SecEvents`](../tables/secevents.md) | - | Hunting |
| [`SecurityEvent`](../tables/securityevent.md) | [Security Events via Legacy Agent](../connectors/securityevents.md), [Windows Security Events via AMA](../connectors/windowssecurityevents.md) | Analytics, Hunting, Workbooks |
| [`encodedPSScripts`](../tables/encodedpsscripts.md) | - | Hunting |
| [`normalizedProcessPath`](../tables/normalizedprocesspath.md) | - | Hunting |
| [`userEnable`](../tables/userenable.md) | - | Analytics |

## Content Items

This solution includes **72 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 50 |
| Analytic Rules | 20 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [AD FS Remote Auth Sync Connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSRemoteAuthSyncConnection.yaml) | Medium | Collection | [`SecurityEvent`](../tables/securityevent.md) |
| [AD FS Remote HTTP Network Connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSRemoteHTTPNetworkConnection.yaml) | Medium | Collection | [`Event`](../tables/event.md) |
| [AD user enabled and password not set within 48 hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/password_not_set.yaml) | Low | Persistence | [`userEnable`](../tables/userenable.md) |
| [ADFS Database Named Pipe Connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSDBNamedPipeConnection.yaml) | Medium | Collection | [`Event`](../tables/event.md) |
| [Excessive Windows Logon Failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ExcessiveLogonFailures.yaml) | Low | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Exchange OAB Virtual Directory Attribute Containing Potential Webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ExchangeOABVirtualDirectoryAttributeContainingPotentialWebshell.yaml) | High | InitialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Gain Code Execution on ADFS Server via SMB + Remote Service or Scheduled Task](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/GainCodeExecutionADFSViaSMB.yaml) | Medium | LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Microsoft Entra ID Local Device Join Information and Transport Key Registry Keys Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/LocalDeviceJoinInfoAndTransportKeyRegKeysAccess.yaml) | Medium | Discovery | [`SecurityEvent`](../tables/securityevent.md) |
| [NRT Base64 Encoded Windows Process Command-lines](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_base64_encoded_pefile.yaml) | Medium | Execution, DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [NRT Process executed from binary hidden in Base64 encoded file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_execute_base64_decodedpayload.yaml) | Medium | Execution, DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [NRT Security Event log cleared](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_SecurityEventLogCleared.yaml) | Medium | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [New EXE deployed via Default Domain or Default Domain Controller Policies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NewEXEdeployedviaDefaultDomainorDefaultDomainControllerPolicies.yaml) | High | Execution, LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Non Domain Controller Active Directory Replication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NonDCActiveDirectoryReplication.yaml) | High | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Potential Fodhelper UAC Bypass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/PotentialFodhelperUACBypass.yaml) | Medium | PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [Potential re-named sdelete usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/Potentialre-namedsdeleteusage.yaml) | Low | DefenseEvasion, Impact | [`SecurityEvent`](../tables/securityevent.md) |
| [Process Execution Frequency Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/TimeSeriesAnomaly-ProcessExecutions.yaml) | Medium | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Scheduled Task Hide](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ScheduleTaskHide.yaml) | High | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Sdelete deployed via GPO and run recursively](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/SdeletedeployedviaGPOandrunrecursively.yaml) | Medium | Impact | [`SecurityEvent`](../tables/securityevent.md) |
| [SecurityEvent - Multiple authentication failures followed by a success](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/MultipleFailedFollowedBySuccess.yaml) | Low | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Starting or Stopping HealthService to Avoid Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/StartStopHealthService.yaml) | Medium | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [AD Account Lockout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ADAccountLockouts.yaml) | Impact | [`SecurityEvent`](../tables/securityevent.md) |
| [Commands executed by WMI on new hosts - potential Impacket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/CommandsexecutedbyWMIonnewhosts-potentialImpacket.yaml) | Execution, LateralMovement | - |
| [Crash dump disabled on host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Crashdumpdisabledonhost.yaml) | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Cscript script daily summary breakdown](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/cscript_summary.yaml) | Execution | [`ProcessCreationEvents`](../tables/processcreationevents.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [Decoy User Account Authentication Attempt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/DecoyUserAccountAuthenticationAttempt.yaml) | LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Discord download invoked from cmd line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Discorddownloadinvokedfromcmdline.yaml) | Execution, CommandAndControl, Exfiltration | [`SecurityEvent`](../tables/securityevent.md) |
| [Domain controller installation media creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/CreateDCInstallationMedia.yaml) | CredentialAccess | - |
| [Entropy for Processes for a given Host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ProcessEntropy.yaml) | Execution | [`Combined`](../tables/combined.md)<br>[`SecEvents`](../tables/secevents.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [Enumeration of users and groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/enumeration_user_and_group.yaml) | Discovery | [`SecurityEvent`](../tables/securityevent.md) |
| [Establishing internal proxies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/InternalProxies.yaml) | CommandandControl | - |
| [Exchange PowerShell Snapin Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ExchangePowerShellSnapin.yaml) | Collection | [`SecurityEvent`](../tables/securityevent.md) |
| [Group added to Built in Domain Local or Global Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/GroupAddedToPrivlegeGroup.yaml) | Persistence, PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [Host Exporting Mailbox and Removing Export](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/HostExportingMailboxAndRemovingExport.yaml) | Collection | [`SecurityEvent`](../tables/securityevent.md) |
| [Hosts Running a Rare Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcess_forWinHost.yaml) | Execution, Persistence, Discovery, LateralMovement, Collection | [`SecurityEvent`](../tables/securityevent.md) |
| [Hosts Running a Rare Process with Commandline](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcessWithCmdLine.yaml) | Execution, Persistence, Discovery, LateralMovement, Collection | [`SecurityEvent`](../tables/securityevent.md) |
| [Hosts with new logons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/HostsWithNewLogons.yaml) | CredentialAccess, LateralMovement | [`LogonEvents`](../tables/logonevents.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [Invoke-PowerShellTcpOneLine Usage.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Invoke-PowerShellTcpOneLine.yaml) | Exfiltration | [`SecurityEvent`](../tables/securityevent.md) |
| [KrbRelayUp Local Privilege Escalation Service Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/KrbRelayUpServiceCreation.yaml) | PrivilegeEscalation | [`Event`](../tables/event.md) |
| [Least Common Parent And Child Process Pairs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Parent_Child_Process.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Least Common Processes Including Folder Depth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Process_With_Depth.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Least Common Processes by Command Line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Process_Command_Lines.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Long lookback User Account Created and Deleted within 10mins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAccountCreatedDeleted.yaml) | Persistence, PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [Masquerading files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/masquerading_files.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Multiple Explicit Credential Usage - 4648 events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/MultipleExplicitCredentialUsage4648Events.yaml) | Discovery, LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [New Child Process of W3WP.exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/NewChildProcessOfW3WP.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [New PowerShell scripts encoded on the commandline](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/powershell_newencodedscipts.yaml) | Execution, CommandAndControl | [`SecurityEvent`](../tables/securityevent.md)<br>[`encodedPSScripts`](../tables/encodedpsscripts.md) |
| [New processes observed in last 24 hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/new_processes.yaml) | Execution | [`ProcessCreationEvents`](../tables/processcreationevents.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [Nishang Reverse TCP Shell in Base64](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/NishangReverseTCPShellBase64.yaml) | Exfiltration | [`SecurityEvent`](../tables/securityevent.md) |
| [Potential Exploitation of MS-RPRN printer bug](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/MSRPRN_Printer_Bug_Exploitation.yaml) | PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [PowerShell downloads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/powershell_downloads.yaml) | Execution, CommandAndControl | [`SecurityEvent`](../tables/securityevent.md) |
| [Powercat Download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/PowerCatDownload.yaml) | Exfiltration | [`SecurityEvent`](../tables/securityevent.md) |
| [Rare Process Path](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcessPath.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md)<br>[`normalizedProcessPath`](../tables/normalizedprocesspath.md) |
| [Rare Processes Run by Service Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcbyServiceAccount.yaml) | Execution | [`ProcessCreationEvents`](../tables/processcreationevents.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [Remote Task Creation/Update using Schtasks Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RemoteScheduledTaskCreationUpdateviaSchtasks.yaml) | Persistence | [`SecurityEvent`](../tables/securityevent.md) |
| [Service installation from user writable directory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ServiceInstallationFromUsersWritableDirectory.yaml) | Execution | [`Event`](../tables/event.md) |
| [Summary of failed user logons by reason of failure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/FailedUserLogons.yaml) | CredentialAccess, LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Summary of user logons by logon type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/User%20Logons%20By%20Logon%20Type.yaml) | CredentialAccess, LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Summary of users created using uncommon/undocumented commandline switches](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/persistence_create_account.yaml) | CredentialAccess, LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Suspected LSASS Dump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/SuspectedLSASSDump.yaml) | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Suspicious Enumeration using Adfind Tool](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Suspicious_enumeration_using_adfind.yaml) | Execution, Discovery, Collection | [`SecurityEvent`](../tables/securityevent.md) |
| [Suspicious Windows Login Outside Normal Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Suspicious_Windows_Login_outside_normal_hours.yaml) | InitialAccess, LateralMovement | [`SecurityEvent`](../tables/securityevent.md) |
| [Suspicious command line tokens in LolBins or LolScripts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/SuspiciousCommandlineTokenLolbas.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Uncommon processes - bottom 5%](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/uncommon_processes.yaml) | Execution | [`ProcessCreationEvents`](../tables/processcreationevents.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [User Account added to Built in Sensitive or Privileged Domain Local or Global Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAccountAddedToPrivlegeGroup.yaml) | Persistence, PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [User account added or removed from a security group by an unauthorized user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAdd_RemToGroupByUnauthorizedUser.yaml) | Persistence, PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [User created by unauthorized user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserCreatedByUnauthorizedUser.yaml) | Persistence, PrivilegeEscalation | [`SecurityEvent`](../tables/securityevent.md) |
| [VIP account more than 6 failed logons in 10](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/CustomUserList_FailedLogons.yaml) | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [VIP account more than 6 failed logons in 10](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/VIPAccountFailedLogons.yaml) | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Windows System Shutdown/Reboot(Sysmon)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/WindowsSystemShutdownReboot.yaml) | Impact | [`Event`](../tables/event.md) |
| [Windows System Time changed on hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/WindowsSystemTimeChange.yaml) | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [EventAnalyzer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Workbooks/EventAnalyzer.json) | [`SecurityEvent`](../tables/securityevent.md) |
| [IdentityAndAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Workbooks/IdentityAndAccess.json) | [`SecurityEvent`](../tables/securityevent.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                         |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------|
| 3.0.9       | 01-10-2024                     | Removed kind from  **Hunting Query** [Service installation from user writable directory]   |
| 3.0.8       | 23-07-2024                     | Updated the Workspace type from resource type picker to resource picker in **Workbook**    |
| 3.0.7       | 12-06-2024                     | Fixed the bugs from **Analytic Rules** NRT_execute_base64_decodedpayload.yaml and ADFSRemoteAuthSyncConnection.yaml |												
| 3.0.6       | 16-05-2024                     | Fixed wrong fieldMappings of **Analytic Rules** password_not_set.yaml						|												
| 3.0.5       | 21-03-2024                     | Updated Entity Mappings of **Analytic Rules** 												|					|
| 3.0.4       | 06-03-2024                     | Added New **Hunting Queries**																	|
| 3.0.3       | 19-02-2024                     | Updated Entity Mapping in 	**Analytical Rule** [Non Domain Controller Active Directory Replication]														|
| 3.0.2       | 23-01-2024                     | Added Sub-Technique in Template															|
| 3.0.1       | 13-12-2023                     | Updated query in **Analytical Rule** (AD user enabled and password not set within 48 hours)|
| 3.0.0       | 26-12-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
