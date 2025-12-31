# SecurityEvent

Reference for SecurityEvent table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Windows |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityevent) |

## Solutions (27)

This table is used by the following solutions:

- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [Cyborg Security HUNTER](../solutions/cyborg-security-hunter.md)
- [EatonForeseer](../solutions/eatonforeseer.md)
- [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md)
- [FalconFriday](../solutions/falconfriday.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md)
- [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md)
- [NISTSP80053](../solutions/nistsp80053.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [PCI DSS Compliance](../solutions/pci-dss-compliance.md)
- [Recorded Future](../solutions/recorded-future.md)
- [SOC Handbook](../solutions/soc-handbook.md)
- [SOX IT Compliance](../solutions/sox-it-compliance.md)
- [Semperis Directory Services Protector](../solutions/semperis-directory-services-protector.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatConnect](../solutions/threatconnect.md)
- [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md)
- [Windows Firewall](../solutions/windows-firewall.md)
- [Windows Security Events](../solutions/windows-security-events.md)

## Connectors (6)

This table is ingested by the following connectors:

- [Cyborg Security HUNTER Hunt Packages](../connectors/cyborgsecurity-hunter.md)
- [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md)
- [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md)
- [Security Events via Legacy Agent](../connectors/securityevents.md)
- [Semperis Directory Services Protector](../connectors/semperisdsp.md)
- [Windows Security Events via AMA](../connectors/windowssecurityevents.md)

---

## Content Items Using This Table (163)

### Analytic Rules (59)

**In solution [EatonForeseer](../solutions/eatonforeseer.md):**
- [EatonForeseer - Unauthorized Logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer/Analytic%20Rules/EatonUnautorizedLogins.yaml)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Potential Remote Desktop Tunneling](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/PotentialRemoteDesktopTunneling.yaml)
- [Security Event log cleared](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/SecurityEventLogCleared.yaml)
- [Windows Binaries Executed from Non-Default Directory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/WindowsBinariesExecutedfromNon-DefaultDirectory.yaml)

**In solution [FalconFriday](../solutions/falconfriday.md):**
- [Certified Pre-Owned - TGTs requested with certificate authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-TGTs-requested.yaml)
- [Certified Pre-Owned - backup of CA private key - rule 1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-backup-key-1.yaml)
- [Certified Pre-Owned - backup of CA private key - rule 2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertifiedPreOwned-backup-key-2.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntHash.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress in SecurityEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_SecurityEvent.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect Malicious Usage of Recovery Tools to Delete Backup Files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/BackupDeletionDetected.yaml)
- [Detect Print Processors Registry Driver Key Creation/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/PrintProcessersModified.yaml)
- [Detect Registry Run Key Creation/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/StartupRegistryModified.yaml)
- [Detect Windows Allow Firewall Rule Addition/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/WindowsAllowFirewallRuleAdded.yaml)
- [Detect Windows Update Disabled from Registry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/WindowsUpdateDisabled.yaml)
- [Process Creation with Suspicious CommandLine Arguments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/SuspiciousProcessCreation.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Imminent Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Campaign/Macaw%20Ransomware/ImminentRansomware.yaml)
- [Possible Phishing with CSL and Network Sessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PossiblePhishingwithCSL%26NetworkSession.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Anomaly found in Network Session Traffic (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/AnomalyFoundInNetworkSessionTraffic.yaml)
- [Anomaly in SMB Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/Anomaly%20in%20SMB%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly based detection (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/DetectPortMisuseByAnomalyBasedDetection.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/DetectPortMisuseByStaticThreshold.yaml)
- [Excessive number of failed connections from a single source (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/ExcessiveHTTPFailuresFromSource.yaml)
- [Network Port Sweep from External Network (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/NetworkPortSweepFromExternalNetwork.yaml)
- [Port scan detected  (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/PortScan.yaml)
- [Potential beaconing activity (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/PossibleBeaconingActivity.yaml)
- [Remote Desktop Network Brute force (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Analytic%20Rules/Remote%20Desktop%20Network%20Brute%20force%20%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingHashAllActors.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml)

**In solution [Semperis Directory Services Protector](../solutions/semperis-directory-services-protector.md):**
- [Semperis DSP Failed Logons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_Failed_Logons.yaml)
- [Semperis DSP Kerberos krbtgt account with old password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_KerberoskrbtgtAccount.yaml)
- [Semperis DSP Mimikatz's DCShadow Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_EvidenceOfMimikatzDCShadowAttack.yaml)
- [Semperis DSP Operations Critical Notifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_Operations_Critical_Notifications_.yaml)
- [Semperis DSP RBAC Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/Semperis_DSP_RBAC_Changes.yaml)
- [Semperis DSP Recent sIDHistory changes on AD objects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_RecentsIDHistoryChangesOnADObjects.yaml)
- [Semperis DSP Well-known privileged SIDs in sIDHistory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_WellKnownPrivilegedSIDsInsIDHistory.yaml)
- [Semperis DSP Zerologon vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Analytic%20Rules/SemperisDSP_ZerologonVulnerability.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

**In solution [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md):**
- [Identify SysAid Server web shell creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Analytic%20Rules/PotentialMercury_Webshell.yaml)

**In solution [Windows Security Events](../solutions/windows-security-events.md):**
- [AD FS Remote Auth Sync Connection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ADFSRemoteAuthSyncConnection.yaml)
- [Excessive Windows Logon Failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ExcessiveLogonFailures.yaml)
- [Exchange OAB Virtual Directory Attribute Containing Potential Webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ExchangeOABVirtualDirectoryAttributeContainingPotentialWebshell.yaml)
- [Gain Code Execution on ADFS Server via SMB + Remote Service or Scheduled Task](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/GainCodeExecutionADFSViaSMB.yaml)
- [Microsoft Entra ID Local Device Join Information and Transport Key Registry Keys Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/LocalDeviceJoinInfoAndTransportKeyRegKeysAccess.yaml)
- [NRT Base64 Encoded Windows Process Command-lines](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_base64_encoded_pefile.yaml)
- [NRT Process executed from binary hidden in Base64 encoded file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_execute_base64_decodedpayload.yaml)
- [NRT Security Event log cleared](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NRT_SecurityEventLogCleared.yaml)
- [New EXE deployed via Default Domain or Default Domain Controller Policies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NewEXEdeployedviaDefaultDomainorDefaultDomainControllerPolicies.yaml)
- [Non Domain Controller Active Directory Replication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/NonDCActiveDirectoryReplication.yaml)
- [Potential Fodhelper UAC Bypass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/PotentialFodhelperUACBypass.yaml)
- [Potential re-named sdelete usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/Potentialre-namedsdeleteusage.yaml)
- [Process Execution Frequency Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/TimeSeriesAnomaly-ProcessExecutions.yaml)
- [Scheduled Task Hide](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/ScheduleTaskHide.yaml)
- [Sdelete deployed via GPO and run recursively](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/SdeletedeployedviaGPOandrunrecursively.yaml)
- [SecurityEvent - Multiple authentication failures followed by a success](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/MultipleFailedFollowedBySuccess.yaml)
- [Starting or Stopping HealthService to Avoid Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Analytic%20Rules/StartStopHealthService.yaml)

### Hunting Queries (84)

**In solution [Cyborg Security HUNTER](../solutions/cyborg-security-hunter.md):**
- [Attempted VBScript Stored in Non-Run CurrentVersion Registry Key Value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Attempted%20VBScript%20Stored%20in%20Non-Run%20CurrentVersion%20Registry%20Key%20Value.yaml)
- [Excessive Windows Discovery and Execution Processes - Potential Malware Installation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Excessive%20Windows%20Discovery%20and%20Execution%20Processes%20-%20Potential%20Malware%20Installation.yaml)
- [LSASS Memory Dumping using WerFault.exe - Command Identification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/LSASS%20Memory%20Dumping%20using%20WerFault.exe%20-%20Command%20Identification.yaml)
- [Metasploit / Impacket PsExec Process Creation Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Metasploit%20Impacket%20PsExec%20Process%20Creation%20Activity.yaml)
- [Potential Maldoc Execution Chain Observed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Potential%20Maldoc%20Execution%20Chain%20Observed.yaml)
- [PowerShell Pastebin Download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/PowerShell%20Pastebin%20Download.yaml)
- [Powershell Encoded Command Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Powershell%20Encoded%20Command%20Execution.yaml)
- [Prohibited Applications Spawning cmd.exe or powershell.exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Prohibited%20Applications%20Spawning%20cmd.exe%20or%20powershell.exe.yaml)
- [Proxy VBScript Execution via CurrentVersion Registry Key](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Proxy%20VBScript%20Execution%20via%20CurrentVersion%20Registry%20Key.yaml)
- [Rundll32 or cmd Executing Application from Explorer - Potential Malware Execution Chain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyborg%20Security%20HUNTER/Hunting%20Queries/Rundll32%20or%20cmd%20Executing%20Application%20from%20Explorer%20-%20Potential%20Malware%20Execution%20Chain.yaml)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Certutil (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_CertutilLoLBins.yaml)
- [Persisting via IFEO Registry Key](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/PersistViaIFEORegistryKey.yaml)
- [Potential Microsoft Security Services Tampering](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/PotentialMicrosoftSecurityServicesTampering.yaml)
- [Rare Windows Firewall Rule updates using Netsh](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/WindowsFirewallUpdateUsingNetsh.yaml)
- [Remote Login Performed with WMI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/RemoteLoginPerformedwithWMI.yaml)
- [Remote Scheduled Task Creation or Update using ATSVC Named Pipe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/RemoteScheduledTaskCreationUpdateUsingATSVCNamedPipe.yaml)
- [Scheduled Task Creation or Update from User Writable Directory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ScheduledTaskCreationUpdateFromUserWritableDrectory.yaml)
- [Windows System Shutdown/Reboot (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_WindowsSystemShutdownReboot.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntHash.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)

**In solution [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md):**
- [Dev-0322 File Drop Activity November 2021 (ASIM Version)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/Dev-0322FileDropActivityNovember2021%28ASIMVersion%29.yaml)
- [Known Nylon Typhoon Registry modifications patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/NylonTyphoonRegIOCPatterns.yaml)
- [SolarWinds Inventory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/SolarWindsInventory.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect File Creation in Startup Folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/FileCretaedInStartupFolder.yaml)
- [Detect Files with Ramsomware Extensions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/FilesWithRansomwareExtensions.yaml)
- [Detect Modification to System Files or Directories by User Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/SystemFilesModifiedByUser.yaml)
- [Detect New Scheduled Task Creation that Run Executables From Non-Standard Location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/NewMaliciousScheduledTask.yaml)
- [Detect New Scheduled Task Entry Creations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/NewScheduledTaskCreation.yaml)
- [Executable Files Created in Uncommon Locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/ExecutableInUncommonLocation.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Detect Outbound LDAP Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Detect%20Outbound%20LDAP%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByAnomalyHunting.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByStaticThresholdHunting.yaml)
- [Detects several users with the same MAC address (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectsSeveralUsersWithTheSameMACAddress.yaml)
- [Mismatch between Destination App name and Destination Port (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/MismatchBetweenDestinationAppNameAndDestinationPort.yaml)
- [Protocols passing authentication in cleartext (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Protocols%20passing%20authentication%20in%20cleartext%20%28ASIM%20Network%20Session%20schema%29.yaml)
- [Remote Desktop Network Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Remote%20Desktop%20Network%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureHashThreatActorHunt.yaml)
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map File Entity to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_SecurityEvent.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map File Entity to Security Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Hunting%20Queries/FileEntity_SecurityEvent.yaml)

**In solution [Windows Security Events](../solutions/windows-security-events.md):**
- [AD Account Lockout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ADAccountLockouts.yaml)
- [Crash dump disabled on host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Crashdumpdisabledonhost.yaml)
- [Cscript script daily summary breakdown](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/cscript_summary.yaml)
- [Decoy User Account Authentication Attempt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/DecoyUserAccountAuthenticationAttempt.yaml)
- [Discord download invoked from cmd line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Discorddownloadinvokedfromcmdline.yaml)
- [Entropy for Processes for a given Host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ProcessEntropy.yaml)
- [Enumeration of users and groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/enumeration_user_and_group.yaml)
- [Exchange PowerShell Snapin Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/ExchangePowerShellSnapin.yaml)
- [Group added to Built in Domain Local or Global Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/GroupAddedToPrivlegeGroup.yaml)
- [Host Exporting Mailbox and Removing Export](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/HostExportingMailboxAndRemovingExport.yaml)
- [Hosts Running a Rare Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcess_forWinHost.yaml)
- [Hosts Running a Rare Process with Commandline](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcessWithCmdLine.yaml)
- [Hosts with new logons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/HostsWithNewLogons.yaml)
- [Invoke-PowerShellTcpOneLine Usage.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Invoke-PowerShellTcpOneLine.yaml)
- [Least Common Parent And Child Process Pairs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Parent_Child_Process.yaml)
- [Least Common Processes Including Folder Depth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Process_With_Depth.yaml)
- [Least Common Processes by Command Line](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Least_Common_Process_Command_Lines.yaml)
- [Long lookback User Account Created and Deleted within 10mins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAccountCreatedDeleted.yaml)
- [Masquerading files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/masquerading_files.yaml)
- [Multiple Explicit Credential Usage - 4648 events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/MultipleExplicitCredentialUsage4648Events.yaml)
- [New Child Process of W3WP.exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/NewChildProcessOfW3WP.yaml)
- [New PowerShell scripts encoded on the commandline](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/powershell_newencodedscipts.yaml)
- [New processes observed in last 24 hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/new_processes.yaml)
- [Nishang Reverse TCP Shell in Base64](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/NishangReverseTCPShellBase64.yaml)
- [Potential Exploitation of MS-RPRN printer bug](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/MSRPRN_Printer_Bug_Exploitation.yaml)
- [PowerShell downloads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/powershell_downloads.yaml)
- [Powercat Download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/PowerCatDownload.yaml)
- [Rare Process Path](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcessPath.yaml)
- [Rare Processes Run by Service Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RareProcbyServiceAccount.yaml)
- [Remote Task Creation/Update using Schtasks Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/RemoteScheduledTaskCreationUpdateviaSchtasks.yaml)
- [Summary of failed user logons by reason of failure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/FailedUserLogons.yaml)
- [Summary of user logons by logon type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/User%20Logons%20By%20Logon%20Type.yaml)
- [Summary of users created using uncommon/undocumented commandline switches](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/persistence_create_account.yaml)
- [Suspected LSASS Dump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/SuspectedLSASSDump.yaml)
- [Suspicious Enumeration using Adfind Tool](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Suspicious_enumeration_using_adfind.yaml)
- [Suspicious Windows Login Outside Normal Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/Suspicious_Windows_Login_outside_normal_hours.yaml)
- [Suspicious command line tokens in LolBins or LolScripts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/SuspiciousCommandlineTokenLolbas.yaml)
- [Uncommon processes - bottom 5%](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/uncommon_processes.yaml)
- [User Account added to Built in Sensitive or Privileged Domain Local or Global Group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAccountAddedToPrivlegeGroup.yaml)
- [User account added or removed from a security group by an unauthorized user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserAdd_RemToGroupByUnauthorizedUser.yaml)
- [User created by unauthorized user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/UserCreatedByUnauthorizedUser.yaml)
- [VIP account more than 6 failed logons in 10](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/CustomUserList_FailedLogons.yaml)
- [VIP account more than 6 failed logons in 10](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/VIPAccountFailedLogons.yaml)
- [Windows System Time changed on hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Hunting%20Queries/WindowsSystemTimeChange.yaml)

### Workbooks (19)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [EatonForeseer](../solutions/eatonforeseer.md):**
- [EatonForeseerHealthAndAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/EatonForeseer/Workbooks/EatonForeseerHealthAndAccess.json)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [MicrosoftPurviewInsiderRiskManagement](../solutions/microsoftpurviewinsiderriskmanagement.md):**
- [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json)

**In solution [NISTSP80053](../solutions/nistsp80053.md):**
- [NISTSP80053](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NISTSP80053/Workbooks/NISTSP80053.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

**In solution [PCI DSS Compliance](../solutions/pci-dss-compliance.md):**
- [PCIDSSCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PCI%20DSS%20Compliance/Workbooks/PCIDSSCompliance.json)

**In solution [SOC Handbook](../solutions/soc-handbook.md):**
- [InvestigationInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/InvestigationInsights.json)
- [SecurityStatus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/SecurityStatus.json)

**In solution [SOX IT Compliance](../solutions/sox-it-compliance.md):**
- [SOXITCompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOX%20IT%20Compliance/Workbooks/SOXITCompliance.json)

**In solution [Semperis Directory Services Protector](../solutions/semperis-directory-services-protector.md):**
- [SemperisDSPNotifications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPNotifications.json)
- [SemperisDSPQuickviewDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPQuickviewDashboard.json)
- [SemperisDSPSecurityIndicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPSecurityIndicators.json)
- [SemperisDSPWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Semperis%20Directory%20Services%20Protector/Workbooks/SemperisDSPWorkbook.json)

**In solution [Windows Firewall](../solutions/windows-firewall.md):**
- [WindowsFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Workbooks/WindowsFirewall.json)

**In solution [Windows Security Events](../solutions/windows-security-events.md):**
- [EventAnalyzer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Workbooks/EventAnalyzer.json)
- [IdentityAndAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Workbooks/IdentityAndAccess.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/securityinsights`
- `microsoft.compute/virtualmachines`
- `microsoft.conenctedvmwarevsphere/virtualmachines`
- `microsoft.azurestackhci/virtualmachines`
- `microsoft.scvmm/virtualmachines`
- `microsoft.compute/virtualmachinescalesets`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
