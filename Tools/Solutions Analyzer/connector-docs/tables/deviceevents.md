# DeviceEvents

Multiple event types, including events triggered by security controls such as Microsoft Defender Antivirus and exploit protection

| Attribute | Value |
|:----------|:------|
| **Category** | MDE |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/deviceevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceevents-table) |

## Solutions (7)

This table is used by the following solutions:

- [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md)
- [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md)
- [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md)
- [FalconFriday](../solutions/falconfriday.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [SOC Handbook](../solutions/soc-handbook.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (23)

### Analytic Rules (11)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Suspicious Powershell Commandlet Executed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Analytic%20Rules/SuspiciousPowerShellCommandExecuted.yaml)

**In solution [FalconFriday](../solutions/falconfriday.md):**
- [Office ASR rule triggered from browser spawned office process.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/OfficeASRFromBrowser.yaml)
- [Suspicious Process Injection from Office application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/OfficeProcessInjection.yaml)
- [Suspicious named pipes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/SuspiciousNamedPipes.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress in DeviceEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_DeviceEvents.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [C2-NamedPipe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Command%20and%20Control/C2-NamedPipe.yaml)
- [Deimos Component Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Campaign/Jupyter-Solarmaker/DeimosComponentExecution.yaml)
- [Files Copied to USB Drives](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Exfiltration/FilesCopiedToUSBDrives.yaml)
- [Local Admin Group Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/LocalAdminGroupChanges.yaml)
- [SUNSPOT malware hashes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/SUNSPOTHashes.yaml)
- [TEARDROP memory-only dropper](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/SolarWinds_TEARDROP_Process-IOCs.yaml)

### Hunting Queries (8)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Suspicious Powershell Commandlet Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/SuspiciousPowerShellCommandExecution.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Anomalous Payload Delivered from ISO files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Execution/AnomalousPayloadDeliveredWithISOFile.yaml)
- [C2-NamedPipe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Command%20and%20Control/C2-NamedPipe.yaml)
- [Deimos Component Execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Jupyter-Solarmaker/DeimosComponentExecution.yaml)
- [Files Copied to USB Drives](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exfiltration/FilesCopiedToUSBDrives.yaml)
- [LemonDuck Registration Function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/LemonDuck/LemonDuckRegistrationFunction.yaml)
- [Local Admin Group Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/LocalAdminGroupChanges.yaml)
- [Scheduled Task Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/ScheduledTaskCreation.yaml)

### Workbooks (4)

**In solution [ContinuousDiagnostics&Mitigation](../solutions/continuousdiagnostics&mitigation.md):**
- [ContinuousDiagnostics&Mitigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContinuousDiagnostics%26Mitigation/Workbooks/ContinuousDiagnostics%26Mitigation.json)

**In solution [CybersecurityMaturityModelCertification(CMMC)2.0](../solutions/cybersecuritymaturitymodelcertification%28cmmc%292.0.md):**
- [CybersecurityMaturityModelCertification_CMMCV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CybersecurityMaturityModelCertification%28CMMC%292.0/Workbooks/CybersecurityMaturityModelCertification_CMMCV2.json)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForEndPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForEndPoint.json)

**In solution [SOC Handbook](../solutions/soc-handbook.md):**
- [AttackSurfaceReduction](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Handbook/Workbooks/AttackSurfaceReduction.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
