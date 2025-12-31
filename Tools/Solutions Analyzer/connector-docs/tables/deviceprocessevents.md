# DeviceProcessEvents

Process creation and related events

| Attribute | Value |
|:----------|:------|
| **Category** | MDE |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/deviceprocessevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table) |

## Solutions (9)

This table is used by the following solutions:

- [Attacker Tools Threat Protection Essentials](../solutions/attacker-tools-threat-protection-essentials.md)
- [Cyware](../solutions/cyware.md)
- [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md)
- [FalconFriday](../solutions/falconfriday.md)
- [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [MicrosoftDefenderForEndpoint](../solutions/microsoftdefenderforendpoint.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (86)

### Analytic Rules (36)

**In solution [Attacker Tools Threat Protection Essentials](../solutions/attacker-tools-threat-protection-essentials.md):**
- [Probable AdFind Recon Tool Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Attacker%20Tools%20Threat%20Protection%20Essentials/Analytic%20Rules/AdFind_Usage.yaml)

**In solution [FalconFriday](../solutions/falconfriday.md):**
- [Access Token Manipulation - Create Process with Token](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CreateProcessWithToken.yaml)
- [DCOM Lateral Movement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DCOMLateralMovement.yaml)
- [Detecting UAC bypass - ChangePK and SLUI registry tampering](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/UACBypass-3-changePK-SLUI-tampering.yaml)
- [Detecting UAC bypass - elevated COM interface](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/UACBypass-1-elevated-COM.yaml)
- [Detecting UAC bypass - modify Windows Store settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/UACBypass-2-modify-ms-store.yaml)
- [Disable or Modify Windows Defender](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DisableOrModifyWindowsDefender.yaml)
- [Ingress Tool Transfer - Certutil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/CertutilIngressToolTransfer.yaml)
- [Match Legitimate Name or Location - 2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/MatchLegitimateNameOrLocation.yaml)
- [Oracle suspicious command execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/OracleSuspiciousCommandExecution.yaml)
- [Remote Desktop Protocol - SharpRDP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/RemoteDesktopProtocol.yaml)
- [Rename System Utilities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/RenameSystemUtilities.yaml)
- [Suspicious parentprocess relationship - Office child processes.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/SuspiciousParentProcessRelationship.yaml)
- [Trusted Developer Utilities Proxy Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/TrustedDeveloperUtilitiesProxyExecution.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect Malicious Usage of Recovery Tools to Delete Backup Files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/BackupDeletionDetected.yaml)
- [Process Creation with Suspicious CommandLine Arguments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/SuspiciousProcessCreation.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Account Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/AccountCreation.yaml)
- [Bitsadmin Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Execution/BITSAdminActivity.yaml)
- [Clearing of forensic evidence from event logs using wevtutil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/LogDeletionUsingWevtutil.yaml)
- [Deletion of data on multiple drives using cipher exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/DataDeletionOnMulipleDrivesUsingCipherExe.yaml)
- [Detect Suspicious Commands Initiated by Webserver Processes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Discovery/SuspiciousCommandInitiatedByWebServerProcess.yaml)
- [Disabling Security Services via Registry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/DEV-0270/DisableSecurityServiceViaRegistry.yaml)
- [Doppelpaymer Stop Services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Defense%20Evasion/DoppelpaymerStopService.yaml)
- [DopplePaymer Procdump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Credential%20Access/DoppelPaymerProcDump.yaml)
- [Imminent Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Campaign/Macaw%20Ransomware/ImminentRansomware.yaml)
- [Java Executing cmd to run Powershell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Campaign/Sysrv-botnet/MaliciousCMDExecutionByJava.yaml)
- [LSASS Credential Dumping with Procdump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Credential%20Access/LSASSCredDumpProcdump.yaml)
- [LaZagne Credential Theft](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/LaZagneCredTheft.yaml)
- [Office Apps Launching Wscipt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Execution/OfficeAppsLaunchingWscript.yaml)
- [Potential Build Process Compromise - MDE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PotentialBuildProcessCompromiseMDE.yaml)
- [Qakbot Campaign Self Deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Defense%20Evasion/QakbotCampaignSelfDeletion.yaml)
- [Qakbot Discovery Activies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/QakbotDiscoveryActivities.yaml)
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/RareProcessAsService.yaml)
- [Regsvr32 Rundll32 with Anomalous Parent Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Defense%20Evasion/Regsvr32Rundll32WithAnomalousParentProcess.yaml)
- [Shadow Copy Deletions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/ShadowCopyDeletion.yaml)
- [Stopping multiple processes using taskkill](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/MultiProcessKillWithTaskKill.yaml)

### Hunting Queries (48)

**In solution [Cyware](../solutions/cyware.md):**
- [Detecting Suspicious PowerShell Command Executions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Hunting%20Queries/DetectingSuspiciousPowerShellCommandExecutions.yaml)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Certutil (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_CertutilLoLBins.yaml)
- [Rare Windows Firewall Rule updates using Netsh](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/WindowsFirewallUpdateUsingNetsh.yaml)
- [Windows System Shutdown/Reboot (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_WindowsSystemShutdownReboot.yaml)

**In solution [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md):**
- [Dev-0322 Command Line Activity November 2021](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/Dev-0322CommandLineActivityNovember2021.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect New Scheduled Task Creation that Run Executables From Non-Standard Location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/NewMaliciousScheduledTask.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Account Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/AccountCreation.yaml)
- [Anomalous Payload Delivered from ISO files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/AnomalousPayloadDeliveredWithISOFile.yaml)
- [Bitsadmin Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/BitsadminActivity.yaml)
- [Check for multiple signs of Ransomware Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/DetectMultipleSignsOfRamsomwareActivity.yaml)
- [Clear System Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/ClearSystemLogs.yaml)
- [Clearing of forensic evidence from event logs using wevtutil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/LogDeletionUsingWevtutil.yaml)
- [Credential Harvesting Using LaZagne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Credential%20Access/LaZagne.yaml)
- [DLLHost.exe WMIC domain discovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/DEV-0270/DomainDiscoveryWMICwithDLLHostExe.yaml)
- [Deletion of data on multiple drives using cipher exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/DataDeletionOnMulipleDrivesUsingCipherExe.yaml)
- [Detect MaiSniper](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Initial%20Access/DetectMailSniper.yaml)
- [Detect Malicious use of MSIExec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/MaliciousUseOfMSIExec.yaml)
- [Detect Malicious use of Msiexec Mimikatz](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/MaliciousUseOfMsiExecMimikatz.yaml)
- [Detect Suspicious Commands Initiated by Webserver Processes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Discovery/SuspiciousCommandInitiatedByWebServerProcess.yaml)
- [Detect Suspicious Mshta Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/SuspiciousMshtaUsage.yaml)
- [Disabling Services via Registry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/DEV-0270/DisableSecurityServiceViaRegistry.yaml)
- [Doppelpaymer Stop Services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/DoppelpaymerStopServices.yaml)
- [DopplePaymer Procdump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Credential%20Access/DoppelPaymerProcdump.yaml)
- [Enumeration of Users & Groups for Lateral Movement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Discovery/User%26GroupEnumWithNetCommand.yaml)
- [Imminent Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Macaw%20Ransomware/ImminentRansomware.yaml)
- [Java Executing cmd to run Powershell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Sysrv-botnet/MaliciousCMDExecutionByJava.yaml)
- [Judgement Panda Exfil Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/JudgementPandaExfilActivity.yaml)
- [LSASS Credential Dumping with Procdump](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Credential%20Access/LSASSCredDumpProcdump.yaml)
- [LaZagne Credential Theft](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/LaZagneCredTheft.yaml)
- [MITRE - Suspicious Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/General%20Queries/MITRESuspiciousEvents.yaml)
- [Malicious Use of MSBuild as LOLBin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Macaw%20Ransomware/MaliciousUseOfMSBuildAsLoLBin.yaml)
- [Office Apps Launching Wscipt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/OfficeAppsLaunchingWscript.yaml)
- [Possible Teams phishing activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Possible%20Teams%20phishing%20activity.yaml)
- [PowerShell Downloads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/PowerShellDownloads.yaml)
- [PowerShell adding exclusion path for Microsoft Defender of ProgramData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/DEV-0270/MDEExclusionUsingPowerShell.yaml)
- [Qakbot Campaign Self Deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/QakbotCampaignSelfDeletion.yaml)
- [Qakbot Discovery Activies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/QakbotDiscoveryActivities.yaml)
- [Qakbot Reconnaissance Activities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Qakbot/QakbotReconActivities.yaml)
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/RareProcessAsService.yaml)
- [Regsvr32 Rundll32 with Anomalous Parent Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/Regsvr32Rundll32WithAnomalousParentProcess.yaml)
- [Shadow Copy Deletions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/ShadowCopyDeletion.yaml)
- [Spoolsv Spawning Rundll32](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/Print%20Spooler%20RCE/SpoolsvSpawningRundll32.yaml)
- [Stopping multiple processes using taskkill](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/MultiProcessKillWithTaskKill.yaml)
- [Suspicious Tomcat Confluence Process Launch](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/CVE-2022-26134-Confluence.yaml)
- [Turning off services using sc exe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/TurningOffServicesWithSCCommad.yaml)
- [Webserver Executing Suspicious Applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/SuspiciousAppExeutedByWebserver.yaml)

**In solution [MicrosoftDefenderForEndpoint](../solutions/microsoftdefenderforendpoint.md):**
- [Probable AdFind Recon Tool Usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Hunting%20Queries/MDE_Usage.yaml)
- [SUNBURST suspicious SolarWinds child processes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Hunting%20Queries/MDE_Process-IOCs.yaml)

### Workbooks (2)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
