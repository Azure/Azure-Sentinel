# DeviceImageLoadEvents

DLL loading events

| Attribute | Value |
|:----------|:------|
| **Category** | MDE |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/deviceimageloadevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceimageloadevents-table) |

## Solutions (2)

This table is used by the following solutions:

- [FalconFriday](../solutions/falconfriday.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (8)

### Analytic Rules (4)

**In solution [FalconFriday](../solutions/falconfriday.md):**
- [Detect .NET runtime being loaded in JScript for code execution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DotNetToJScript.yaml)
- [Hijack Execution Flow - DLL Side-Loading](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FalconFriday/Analytic%20Rules/DLLSideLoading.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Persistence/RareProcessAsService.yaml)
- [Regsvr32 Rundll32 Image Loads Abnormal Extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Defense%20Evasion/Regsvr32Rundll32ImageLoadsAbnormalExtension.yaml)

### Hunting Queries (4)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Rare Process as a Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Persistence/RareProcessAsService.yaml)
- [Regsvr32 Rundll32 Image Loads Abnormal Extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Defense%20Evasion/Regsvr32Rundll32ImageLoadsAbnormalExtension.yaml)
- [Suspicious Image Load related to IcedId](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/IcedIdSuspiciousImageLoad.yaml)
- [Suspicious Spoolsv Child Process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Exploits/Print%20Spooler%20RCE/SuspiciousSpoolsvChildProcess.yaml)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
