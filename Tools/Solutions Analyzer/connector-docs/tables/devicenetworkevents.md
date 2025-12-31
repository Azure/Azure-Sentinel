# DeviceNetworkEvents

Network connection and related events

| Attribute | Value |
|:----------|:------|
| **Category** | MDE |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/devicenetworkevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table) |

## Solutions (13)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [Cyware](../solutions/cyware.md)
- [DORA Compliance](../solutions/dora-compliance.md)
- [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md)
- [Google Threat Intelligence](../solutions/google-threat-intelligence.md)
- [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Network Session Essentials](../solutions/network-session-essentials.md)
- [Recorded Future](../solutions/recorded-future.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)
- [ThreatConnect](../solutions/threatconnect.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (49)

### Analytic Rules (27)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Analytic%20Rules/ThreatHunting/ThreatHuntIp.yaml)

**In solution [GreyNoiseThreatIntelligence](../solutions/greynoisethreatintelligence.md):**
- [GreyNoise TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GreyNoiseThreatIntelligence/Analytic%20Rules/GreyNoise_IPEntity_imNetworkSession.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Possible Phishing with CSL and Network Sessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/PossiblePhishingwithCSL%26NetworkSession.yaml)
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/RareProcessAsService.yaml)
- [Regsvr32 Rundll32 Image Loads Abnormal Extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Defense%20Evasion/Regsvr32Rundll32ImageLoadsAbnormalExtension.yaml)
- [Regsvr32 Rundll32 with Anomalous Parent Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Defense%20Evasion/Regsvr32Rundll32WithAnomalousParentProcess.yaml)
- [SUNBURST network beacons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/SolarWinds_SUNBURST_Network-IOCs.yaml)

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
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Analytic%20Rules/ThreatHunting/RecordedFutureThreatHuntingIPAllActors.yaml)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map Domain Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_DeviceNetworkEvents.yaml)
- [TI Map IP Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_DeviceNetworkEvents.yaml)
- [TI Map URL Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/URLEntity_DeviceNetworkEvents.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI Map Domain Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_DeviceNetworkEvents_Updated.yaml)
- [TI Map IP Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_DeviceNetworkEvents_Updated.yaml)
- [TI Map URL Entity to DeviceNetworkEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/URLEntity_DeviceNetworkEvents_Updated.yaml)
- [TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_imNetworkSession.yaml)

**In solution [ThreatConnect](../solutions/threatconnect.md):**
- [ThreatConnect TI map IP entity to Network Session Events (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ThreatConnect/Analytic%20Rules/ThreatConnect_IPEntity_NetworkSessions.yaml)

### Hunting Queries (16)

**In solution [Cyware](../solutions/cyware.md):**
- [Detecting Suspicious PowerShell Command Executions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyware/Hunting%20Queries/UnusualNetworkConnectionsToRareExternalDomains.yaml)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Download of New File Using Curl](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/DownloadOfNewFileUsingCurl.yaml)

**In solution [Google Threat Intelligence](../solutions/google-threat-intelligence.md):**
- [Google Threat Intelligence - Threat Hunting IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Threat%20Intelligence/Hunting%20Queries/ThreatHuntIp.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/RareProcessAsService.yaml)
- [Recon with Rundll](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Command%20and%20Control/ReconWithRundll.yaml)
- [Regsvr32 Rundll32 Image Loads Abnormal Extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/Regsvr32Rundll32ImageLoadsAbnormalExtension.yaml)
- [Regsvr32 Rundll32 with Anomalous Parent Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/Regsvr32Rundll32WithAnomalousParentProcess.yaml)
- [Snip3 Malicious Network Connectivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Snip3MaliciousNetworkConnectivity.yaml)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [Detect Outbound LDAP Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Detect%20Outbound%20LDAP%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)
- [Detect port misuse by anomaly (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByAnomalyHunting.yaml)
- [Detect port misuse by static threshold (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectPortMisuseByStaticThresholdHunting.yaml)
- [Detects several users with the same MAC address (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/DetectsSeveralUsersWithTheSameMACAddress.yaml)
- [Mismatch between Destination App name and Destination Port (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/MismatchBetweenDestinationAppNameAndDestinationPort.yaml)
- [Protocols passing authentication in cleartext (ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Protocols%20passing%20authentication%20in%20cleartext%20%28ASIM%20Network%20Session%20schema%29.yaml)
- [Remote Desktop Network Traffic(ASIM Network Session schema)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Hunting%20Queries/Remote%20Desktop%20Network%20Traffic%28ASIM%20Network%20Session%20schema%29.yaml)

**In solution [Recorded Future](../solutions/recorded-future.md):**
- [RecordedFuture Threat Hunting IP All Actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/Hunting%20Queries/RecordedFutureIPThreatActorHunt.yaml)

### Workbooks (5)

**In solution [DORA Compliance](../solutions/dora-compliance.md):**
- [DORACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DORA%20Compliance/Workbooks/DORACompliance.json)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForEndPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForEndPoint.json)

**In solution [Network Session Essentials](../solutions/network-session-essentials.md):**
- [NetworkSessionEssentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentials.json)
- [NetworkSessionEssentialsV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Network%20Session%20Essentials/Workbooks/NetworkSessionEssentialsV2.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
