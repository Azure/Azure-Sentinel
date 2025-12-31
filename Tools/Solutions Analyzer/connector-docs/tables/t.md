# T

| Attribute | Value |
|:----------|:------|
| **Solutions** | [Azure Activity](../solutions/azure-activity.md), [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md), [Google Threat Intelligence](../solutions/google-threat-intelligence.md), [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md), [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md), [Malware Protection Essentials](../solutions/malware-protection-essentials.md), [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md), [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md), [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md), [Microsoft Exchange Security - Exchange Online](../solutions/microsoft-exchange-security---exchange-online.md), [Network Session Essentials](../solutions/network-session-essentials.md), [Recorded Future](../solutions/recorded-future.md), [Threat Intelligence](../solutions/threat-intelligence.md), [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md), [ThreatConnect](../solutions/threatconnect.md) |

---

## Content Items Using This Table (53)

### Analytic Rules (23)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntHash.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect Malicious Usage of Recovery Tools to Delete Backup Files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/BackupDeletionDetected.yaml)
- [Process Creation with Suspicious CommandLine Arguments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/SuspiciousProcessCreation.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Imminent Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Campaign/Macaw%20Ransomware/ImminentRansomware.yaml)
- [Possible Phishing with CSL and Network Sessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PossiblePhishingwithCSL%26NetworkSession.yaml)

**In solution [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md):**
- [Server Oriented Cmdlet And User Oriented Cmdlet used](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Analytic%20Rules/ServerOrientedWithUserOrientedAdministration.yaml)
- [VIP Mailbox manipulation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Analytic%20Rules/CriticalCmdletsUsageDetection.yaml)

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

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

### Hunting Queries (21)

**In solution [Azure Activity](../solutions/azure-activity.md):**
- [Anomalous Azure Operation Hunting Model](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Hunting%20Queries/AnomalousAzureOperationModel.yaml)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Certutil (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_CertutilLoLBins.yaml)
- [Windows System Shutdown/Reboot (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_WindowsSystemShutdownReboot.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting Hash](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntHash.yaml)
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)

**In solution [Legacy IOC based Threat Protection](../solutions/legacy-ioc-based-threat-protection.md):**
- [Dev-0322 File Drop Activity November 2021 (ASIM Version)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Legacy%20IOC%20based%20Threat%20Protection/Hunting%20Queries/Dev-0322FileDropActivityNovember2021%28ASIMVersion%29.yaml)

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

### Workbooks (8)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md):**
- [Microsoft Exchange Admin Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Workbooks/Microsoft%20Exchange%20Admin%20Activity.json)
- [Microsoft Exchange Search AdminAuditLog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/Workbooks/Microsoft%20Exchange%20Search%20AdminAuditLog.json)

**In solution [Microsoft Exchange Security - Exchange Online](../solutions/microsoft-exchange-security---exchange-online.md):**
- [Microsoft Exchange Admin Activity - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Admin%20Activity%20-%20Online.json)
- [Microsoft Exchange Search AdminAuditLog - Online](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/Workbooks/Microsoft%20Exchange%20Search%20AdminAuditLog%20-%20Online.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
