# Advanced Security Information Model (ASIM) ProcessEvent parsers 

This folder includes the the Advanced Security Information Model (ASIM)  ProcessEvent parsers. The parsers are provided in YAML and in ARM template formats. The latter can be used to deploy the parsers, while the former is provided for educational purposes. 

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Microsoft Sentinel ProcessEvent normalization schema reference](https://aka.ms/ASimProcessEventDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimProcessEventARM)

<br>

## Parsers

This template deploys the following parsers:

* Source agnostic parsers:
  * imProcess - Process events from all normalized process events sources
  * imProcessCreate - Process creation events from all normalized process events sources
  * imProcessTerminate - Process termination events from all normalized process events sources
  * vimProcessEmpty - Empty ASim Process table

* Source specific parsers:
  * **Microsoft 365 Defender for Endpoints** - vimProcessEventMicrosoft365D
  * **Sysmon for Windows** (Events 1 and 5) - vimProcessCreateMicrosoftSysmon, vimProcessTerminateMicrosoftSysmon 
  * **Sysmon for Linux** - vimProcessCreateLinuxSysmon, vimProcessTerminateLinuxSysmon
  * **Windows Security Events**, collecting using the Log Analytics Agent or Azure Monitor Agent - vimProcessCreateMicrosoftSecurityEvents, vimProcessTerminateMicrosoftSecurityEvents
  * **Windows Events** collecting using the Azure Monitor Agent - vimProcessCreateMicrosoftWindowsEvents, vimProcessCreationMicrosoftWindowsEvents. Note that those are the same original events as Windows Security events, but collected to the WindowsEvent table, for example when collecting using Windows Event Forwarding.
  * **Microsoft Defender for IoT - Endpoint (MD4IoT)** - vimProcessEventMD4IoT  

## Analytics rules

By deploying these parsers, you enable the following out of the box Analytic Rules to work with ASIM:

 - [Probable AdFind Recon Tool Usage (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Detections/ASimProcess/imProcess_AdFind_Usage.yaml)
 - [Base64 encoded Windows process command-lines (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Detections/ASimProcess/imProcess_base64_encoded_pefile.yaml)
 - [Malware in the recycle bin (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Detections/ASimProcess/imProcess_malware_in_recyclebin.yaml)
 - [NOBELIUM - suspicious rundll32.exe execution of vbscript (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Detections/ASimProcess/imProcess_NOBELIUM_SuspiciousRundll32Exec.yaml)
 - [SUNBURST suspicious SolarWinds child processes (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Detections/ASimProcess/imProcess_SolarWinds_SUNBURST_Process-IOCs.yaml)

## Hunting queries

By deploying these parsers, you enable the following out of the box Hunting Queries to work with ASIM:

 - [Cscript script daily summary breakdown (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_cscript_summary.yaml)
 - [Enumeration of users and groups (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_enumeration_user_and_group.yaml)
 - [Exchange PowerShell Snapin Added (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_ExchangePowerShellSnapin.yaml)
 - [Host Exporting Mailbox and Removing Export (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_HostExportingMailboxAndRemovingExport.yaml)
 - [Invoke-PowerShellTcpOneLine Usage (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_Invoke-PowerShellTcpOneLine.yaml)
 - [Nishang Reverse TCP Shell in Base64 (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_NishangReverseTCPShellBase64.yaml)
 - [Summary of users created using uncommon/undocumented commandline switches (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_persistence_create_account.yaml)
 - [Powercat Download (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_PowerCatDownload.yaml)
 - [PowerShell downloads (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_powershell_downloads.yaml)
 - [Entropy for Processes for a given Host (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_ProcessEntropy.yaml)
 - [SolarWinds Inventory (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_SolarWindsInventory.yaml)
 - [Suspicious enumeration using Adfind tool (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_Suspicious_enumeration_using_adfind.yaml)
 - [Windows System Shutdown/Reboot (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_Windows%20System%20Shutdown-Reboot(T1529).yaml)
 - [Certutil (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_Certutil-LOLBins.yaml)
 - [Rundll32 (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/inProcess_SignedBinaryProxyExecutionRundll32.yaml)
 - [Uncommon processes - bottom 5% (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/ASimProcess/imProcess_uncommon_processes.yaml)
 - [Unicode Obfuscation in Command Line](https://github.com/Azure/Azure-Sentinel/blob/master/Hunting%20Queries/MultipleDataSources/UnicodeObfuscationInCommandLine.yaml)
<br>

