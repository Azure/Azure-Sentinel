# Cyborg Security HUNTER

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cyborg Security |
| **Support Tier** | Partner |
| **Support Link** | [https://hunter.cyborgsecurity.io/customer-support](https://hunter.cyborgsecurity.io/customer-support) |
| **Categories** | domains |
| **First Published** | 2023-07-03 |
| **Last Updated** | 2023-09-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cyborg Security HUNTER Hunt Packages](../connectors/cyborgsecurity-hunter.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityEvent`](../tables/securityevent.md) | [Cyborg Security HUNTER Hunt Packages](../connectors/cyborgsecurity-hunter.md) | Hunting |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 10 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Attempted VBScript Stored in Non-Run CurrentVersion Registry Key Value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Attempted%20VBScript%20Stored%20in%20Non-Run%20CurrentVersion%20Registry%20Key%20Value.yaml) | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Excessive Windows Discovery and Execution Processes - Potential Malware Installation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Excessive%20Windows%20Discovery%20and%20Execution%20Processes%20-%20Potential%20Malware%20Installation.yaml) | Discovery | [`SecurityEvent`](../tables/securityevent.md) |
| [LSASS Memory Dumping using WerFault.exe - Command Identification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/LSASS%20Memory%20Dumping%20using%20WerFault.exe%20-%20Command%20Identification.yaml) | CredentialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [Metasploit / Impacket PsExec Process Creation Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Metasploit%20Impacket%20PsExec%20Process%20Creation%20Activity.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Potential Maldoc Execution Chain Observed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Potential%20Maldoc%20Execution%20Chain%20Observed.yaml) | DefenseEvasion, Execution, InitialAccess | [`SecurityEvent`](../tables/securityevent.md) |
| [PowerShell Pastebin Download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/PowerShell%20Pastebin%20Download.yaml) | CommandandControl | [`SecurityEvent`](../tables/securityevent.md) |
| [Powershell Encoded Command Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Powershell%20Encoded%20Command%20Execution.yaml) | DefenseEvasion, Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Prohibited Applications Spawning cmd.exe or powershell.exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Prohibited%20Applications%20Spawning%20cmd.exe%20or%20powershell.exe.yaml) | CommandandControl | [`SecurityEvent`](../tables/securityevent.md) |
| [Proxy VBScript Execution via CurrentVersion Registry Key](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Proxy%20VBScript%20Execution%20via%20CurrentVersion%20Registry%20Key.yaml) | DefenseEvasion, Execution | [`SecurityEvent`](../tables/securityevent.md) |
| [Rundll32 or cmd Executing Application from Explorer - Potential Malware Execution Chain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Rundll32%20or%20cmd%20Executing%20Application%20from%20Explorer%20-%20Potential%20Malware%20Execution%20Chain.yaml) | Execution | [`SecurityEvent`](../tables/securityevent.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 22-11-2023                     | Initial Submission                          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
