# FalconFriday

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | FalconForce |
| **Support Tier** | Partner |
| **Support Link** | [https://www.falconforce.nl/en/](https://www.falconforce.nl/en/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **14 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`BrowserTraffic`](../tables/browsertraffic.md) | Analytics |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Analytics |
| [`DeviceEvents`](../tables/deviceevents.md) | Analytics |
| [`DeviceFileEvents`](../tables/devicefileevents.md) | Analytics |
| [`DeviceImageLoadEvents`](../tables/deviceimageloadevents.md) | Analytics |
| [`DeviceLogonEvents`](../tables/devicelogonevents.md) | Analytics |
| [`DeviceProcessEvents`](../tables/deviceprocessevents.md) | Analytics |
| [`DeviceRegistryEvents`](../tables/deviceregistryevents.md) | Analytics |
| [`PotentialAlerts`](../tables/potentialalerts.md) | Analytics |
| [`RemoteDcomProcs`](../tables/remotedcomprocs.md) | Analytics |
| [`SecurityEvent`](../tables/securityevent.md) | Analytics |
| [`SigninLogs`](../tables/signinlogs.md) | Analytics |
| [`SuspiciousSignings`](../tables/suspicioussignings.md) | Analytics |
| [`serviceNetworkEvents`](../tables/servicenetworkevents.md) | Analytics |

## Content Items

This solution includes **30 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 30 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [ASR Bypassing Writing Executable Content](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/ASRBypassingWritingExecutableContent.yaml) | Medium | DefenseEvasion | [`DeviceFileEvents`](../tables/devicefileevents.md) |
| [Access Token Manipulation - Create Process with Token](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CreateProcessWithToken.yaml) | Medium | PrivilegeEscalation, DefenseEvasion | [`DeviceLogonEvents`](../tables/devicelogonevents.md)<br>[`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Beacon Traffic Based on Common User Agents Visiting Limited Number of Domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/RecognizingBeaconingTraffic.yaml) | Medium | CommandAndControl | [`BrowserTraffic`](../tables/browsertraffic.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`PotentialAlerts`](../tables/potentialalerts.md) |
| [Certified Pre-Owned - TGTs requested with certificate authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-TGTs-requested.yaml) | Medium | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Certified Pre-Owned - backup of CA private key - rule 1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-backup-key-1.yaml) | Medium | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Certified Pre-Owned - backup of CA private key - rule 2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-backup-key-2.yaml) | Medium | DefenseEvasion | [`SecurityEvent`](../tables/securityevent.md) |
| [Component Object Model Hijacking - Vault7 trick](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/COMHijacking.yaml) | Medium | Persistence, PrivilegeEscalation | [`DeviceRegistryEvents`](../tables/deviceregistryevents.md) |
| [DCOM Lateral Movement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DCOMLateralMovement.yaml) | Medium | LateralMovement | [`DeviceProcessEvents`](../tables/deviceprocessevents.md)<br>[`RemoteDcomProcs`](../tables/remotedcomprocs.md) |
| [Detect .NET runtime being loaded in JScript for code execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DotNetToJScript.yaml) | Medium | Execution | [`DeviceImageLoadEvents`](../tables/deviceimageloadevents.md) |
| [Detecting UAC bypass - ChangePK and SLUI registry tampering](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/UACBypass-3-changePK-SLUI-tampering.yaml) | Medium | Impact | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Detecting UAC bypass - elevated COM interface](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/UACBypass-1-elevated-COM.yaml) | Medium | Impact | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Detecting UAC bypass - modify Windows Store settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/UACBypass-2-modify-ms-store.yaml) | Medium | Impact | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Disable or Modify Windows Defender](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DisableOrModifyWindowsDefender.yaml) | Medium | DefenseEvasion | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Excessive share permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/ExcessiveSharePermissions.yaml) | Medium | Collection, Discovery | - |
| [Expired access credentials being used in Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/ExpiredAccessCredentials.yaml) | Medium | CredentialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>[`SuspiciousSignings`](../tables/suspicioussignings.md) |
| [Hijack Execution Flow - DLL Side-Loading](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DLLSideLoading.yaml) | Medium | Persistence, PrivilegeEscalation, DefenseEvasion | [`DeviceFileEvents`](../tables/devicefileevents.md)<br>[`DeviceImageLoadEvents`](../tables/deviceimageloadevents.md) |
| [Ingress Tool Transfer - Certutil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertutilIngressToolTransfer.yaml) | Low | CommandAndControl, DefenseEvasion | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Match Legitimate Name or Location - 2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/MatchLegitimateNameOrLocation.yaml) | Medium | DefenseEvasion | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Microsoft Entra ID Rare UserAgent App Sign-in](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/AzureADRareUserAgentAppSignin.yaml) | Medium | DefenseEvasion | - |
| [Microsoft Entra ID UserAgent OS Missmatch](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/AzureADUserAgentOSmissmatch.yaml) | Medium | DefenseEvasion | - |
| [Office ASR rule triggered from browser spawned office process.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/OfficeASRFromBrowser.yaml) | Medium | InitialAccess | [`DeviceEvents`](../tables/deviceevents.md) |
| [Oracle suspicious command execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/OracleSuspiciousCommandExecution.yaml) | Medium | LateralMovement, PrivilegeEscalation | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Password Spraying](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/PasswordSprayingWithMDE.yaml) | Medium | CredentialAccess | [`DeviceLogonEvents`](../tables/devicelogonevents.md) |
| [Remote Desktop Protocol - SharpRDP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/RemoteDesktopProtocol.yaml) | Medium | LateralMovement | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Rename System Utilities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/RenameSystemUtilities.yaml) | Medium | DefenseEvasion | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [SMB/Windows Admin Shares](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/SMBWindowsAdminShares.yaml) | Medium | LateralMovement | [`serviceNetworkEvents`](../tables/servicenetworkevents.md) |
| [Suspicious Process Injection from Office application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/OfficeProcessInjection.yaml) | Medium | Execution | [`DeviceEvents`](../tables/deviceevents.md) |
| [Suspicious named pipes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/SuspiciousNamedPipes.yaml) | Medium | Execution, DefenseEvasion | [`DeviceEvents`](../tables/deviceevents.md) |
| [Suspicious parentprocess relationship - Office child processes.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/SuspiciousParentProcessRelationship.yaml) | Medium | InitialAccess | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |
| [Trusted Developer Utilities Proxy Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/TrustedDeveloperUtilitiesProxyExecution.yaml) | Medium | DefenseEvasion | [`DeviceProcessEvents`](../tables/deviceprocessevents.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.0       | 24-06-2024                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID and Added missing AMA **Data Connector** reference in **Analytic rules**.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
