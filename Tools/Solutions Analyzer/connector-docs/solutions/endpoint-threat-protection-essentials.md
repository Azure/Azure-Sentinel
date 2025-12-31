# Endpoint Threat Protection Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-11-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **13 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`ASimProcessEventLogs`](../tables/asimprocesseventlogs.md) | Hunting |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | Hunting |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | Hunting |
| [`DeviceEvents`](../tables/deviceevents.md) | Analytics, Hunting |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | Hunting |
| [`DeviceProcessEvents`](../tables/deviceprocessevents.md) | Hunting |
| [`Event`](../tables/event.md) | Analytics, Hunting |
| [`SecurityEvent`](../tables/securityevent.md) | Analytics, Hunting |
| [`SecurityIoTRawEvent`](../tables/securityiotrawevent.md) | Hunting |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | Hunting |
| [`Syslog`](../tables/syslog.md) | Hunting |
| [`TrendMicro_XDR_OAT_CL`](../tables/trendmicro-xdr-oat-cl.md) | Hunting |
| [`WindowsEvent`](../tables/windowsevent.md) | Hunting |

## Content Items

This solution includes **29 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 15 |
| Analytic Rules | 14 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Base64 encoded Windows process command-lines](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/base64_encoded_pefile.yaml) | Medium | Execution, DefenseEvasion | - |
| [Detecting Macro Invoking ShellBrowserWindow COM Objects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/MacroInvokingShellBrowserWindowCOMObjects.yaml) | Medium | LateralMovement | [`Event`](../tables/event.md) |
| [Dumping LSASS Process Into a File](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/DumpingLSASSProcessIntoaFile.yaml) | High | CredentialAccess | [`Event`](../tables/event.md) |
| [Lateral Movement via DCOM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/LateralMovementViaDCOM.yaml) | Medium | LateralMovement | [`Event`](../tables/event.md) |
| [Malware in the recycle bin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/malware_in_recyclebin.yaml) | Medium | DefenseEvasion | - |
| [Potential Remote Desktop Tunneling](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/PotentialRemoteDesktopTunneling.yaml) | Medium | CommandAndControl | [`SecurityEvent`](../tables/securityevent.md) |
| [Process executed from binary hidden in Base64 encoded file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/execute_base64_decodedpayload.yaml) | Medium | Execution, DefenseEvasion | - |
| [Registry Persistence via AppCert DLL Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/RegistryPersistenceViaAppCertDLLModification.yaml) | Medium | Persistence | [`Event`](../tables/event.md) |
| [Registry Persistence via AppInit DLLs Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/RegistryPersistenceViaAppInt_DLLsModification.yaml) | Medium | Persistence | [`Event`](../tables/event.md) |
| [Security Event log cleared](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/SecurityEventLogCleared.yaml) | Medium | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Suspicious Powershell Commandlet Executed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/SuspiciousPowerShellCommandExecuted.yaml) | Medium | Execution | [`DeviceEvents`](../tables/deviceevents.md) |
| [WDigest downgrade attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WDigestDowngradeAttack.yaml) | Medium | CredentialAccess | [`Event`](../tables/event.md) |
| [Windows Binaries Executed from Non-Default Directory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WindowsBinariesExecutedfromNon-DefaultDirectory.yaml) | Medium | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Windows Binaries Lolbins Renamed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WindowsBinariesLolbinsRenamed.yaml) | Medium | Execution | [`Event`](../tables/event.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Backup Deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/BackupDeletion.yaml) | Impact | - |
| [Certutil (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_CertutilLoLBins.yaml) | CommandAndControl | [`ASimProcessEventLogs`](../tables/asimprocesseventlogs.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`DeviceProcessEvents`](../tables/deviceprocessevents.md)<br>[`Event`](../tables/event.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`TrendMicro_XDR_OAT_CL`](../tables/trendmicro-xdr-oat-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md) |
| [Detect Certutil (LOLBins and LOLScripts) Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/Certutil-LOLBins.yaml) | CommandAndControl | [`Event`](../tables/event.md) |
| [Download of New File Using Curl](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/DownloadOfNewFileUsingCurl.yaml) | CommandAndControl | [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) |
| [Execution of File with One Character in the Name](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/FileExecutionWithOneCharacterInTheName.yaml) | Execution | [`Event`](../tables/event.md) |
| [Persisting via IFEO Registry Key](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/PersistViaIFEORegistryKey.yaml) | Persistence | [`SecurityEvent`](../tables/securityevent.md) |
| [Potential Microsoft Security Services Tampering](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/PotentialMicrosoftSecurityServicesTampering.yaml) | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Rare Windows Firewall Rule updates using Netsh](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/WindowsFirewallUpdateUsingNetsh.yaml) | Execution | [`DeviceProcessEvents`](../tables/deviceprocessevents.md)<br>[`Event`](../tables/event.md)<br>[`SecurityEvent`](../tables/securityevent.md) |
| [Remote Login Performed with WMI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/RemoteLoginPerformedwithWMI.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Remote Scheduled Task Creation or Update using ATSVC Named Pipe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/RemoteScheduledTaskCreationUpdateUsingATSVCNamedPipe.yaml) | Persistence | [`SecurityEvent`](../tables/securityevent.md) |
| [Rundll32 (LOLBins and LOLScripts)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/SignedBinaryProxyExecutionRundll32.yaml) | DefenseEvasion | [`Event`](../tables/event.md) |
| [Scheduled Task Creation or Update from User Writable Directory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ScheduledTaskCreationUpdateFromUserWritableDrectory.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Suspicious Powershell Commandlet Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/SuspiciousPowerShellCommandExecution.yaml) | Execution | [`DeviceEvents`](../tables/deviceevents.md) |
| [Unicode Obfuscation in Command Line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/UnicodeObfuscationInCommandLine.yaml) | DefenseEvasion | - |
| [Windows System Shutdown/Reboot (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_WindowsSystemShutdownReboot.yaml) | Impact | [`ASimProcessEventLogs`](../tables/asimprocesseventlogs.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`DeviceProcessEvents`](../tables/deviceprocessevents.md)<br>[`Event`](../tables/event.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`Syslog`](../tables/syslog.md)<br>[`TrendMicro_XDR_OAT_CL`](../tables/trendmicro-xdr-oat-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.5       |     18-11-2024                 | Removed the broken URL in **Analytic Rule**                                      |
| 3.0.4       |     10-06-2024                 | Added entityMappings and added missing AMA DC reference in **Analytical Rules** and **Hunting Queries**  |
| 3.0.3       |     11-03-2024                 | Added few **Hunting Queries** to detect Endpoint Threats                     |
| 3.0.2       |     21-02-2024                 | Tagged for dependent solutions for deployment                                |
|             |                                | Added New rules to detect Suspicious PowerShell Commandlet Exceutions        | 
| 3.0.1       |     29-01-2024                 | Added subTechniques in Template                                              |
| 3.0.0       |     25-10-2023                 | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
