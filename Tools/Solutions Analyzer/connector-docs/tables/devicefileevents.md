# DeviceFileEvents

File creation, modification, and other file system events

| Attribute | Value |
|:----------|:------|
| **Category** | MDE |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/devicefileevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicefileevents-table) |

## Solutions (8)

This table is used by the following solutions:

- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [FalconFriday](../solutions/falconfriday.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Recorded Future](../solutions/recorded-future.md)
- [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (31)

### Analytic Rules (8)

**In solution [FalconFriday](../solutions/falconfriday.md):**
- [ASR Bypassing Writing Executable Content](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/ASRBypassingWritingExecutableContent.yaml)
- [Hijack Execution Flow - DLL Side-Loading](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DLLSideLoading.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntHash.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Potential Build Process Compromise - MDE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PotentialBuildProcessCompromiseMDE.yaml)
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/RareProcessAsService.yaml)
- [Remote File Creation with PsExec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Lateral%20Movement/RemoteFileCreationWithPsExec.yaml)
- [SUNBURST and SUPERNOVA backdoor hashes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/SolarWinds_SUNBURST_%26_SUPERNOVA_File-IOCs.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingHashAllActors.yaml)

### Hunting Queries (20)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntHash.yaml)

**In solution [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md):**
- [Dev-0322 File Drop Activity November 2021](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/Dev-0322FileDropActivityNovember2021.yaml)
- [Dev-0322 File Drop Activity November 2021 (ASIM Version)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/Dev-0322FileDropActivityNovember2021%28ASIMVersion%29.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect File Creation in Startup Folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/FileCretaedInStartupFolder.yaml)
- [Detect Files with Ramsomware Extensions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/FilesWithRansomwareExtensions.yaml)
- [Detect Modification to System Files or Directories by User Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/SystemFilesModifiedByUser.yaml)
- [Detect New Scheduled Task Entry Creations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/NewScheduledTaskCreation.yaml)
- [Executable Files Created in Uncommon Locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/ExecutableInUncommonLocation.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Dropping Payload via certutil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Bazacall/PayloadDropUsingCertUtil.yaml)
- [PrintNightmare CVE-2021-1675 usage Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/PrintNightmareUsageDetection-CVE-2021-1675.yaml)
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/RareProcessAsService.yaml)
- [Remote File Creation with PsExec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Lateral%20Movement/RemoteFileCreationWithPsExec.yaml)
- [Robbinhood Driver](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/RobbinhoodDriver.yaml)
- [Suspicious DLLs in spool Folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/Print%20Spooler%20RCE/SuspiciousDLLInSpoolFolder.yaml)
- [Suspicious Files in spool Folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/Print%20Spooler%20RCE/SuspiciousFilesInSpoolFolder.yaml)
- [Windows Print Spooler Service Suspicious File Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/SuspiciousFileCreationByPrintSpoolerService.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting Hash All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureHashThreatActorHunt.yaml)

**In solution [Web Shells Threat Protection](../solutions/web-shells-threat-protection.md):**
- [Exchange IIS Worker Dropping Webshells](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/exchange-iis-worker-dropping-webshell.yaml)
- [Possible webshell drop](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/Possible%20webshell%20drop.yaml)
- [UMWorkerProcess Creating Webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Web%20Shells%20Threat%20Protection/Hunting%20Queries/umworkerprocess-creating-webshell.yaml)

### Workbooks (3)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForEndPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForEndPoint.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
