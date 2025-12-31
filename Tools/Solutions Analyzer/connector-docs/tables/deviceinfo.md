# DeviceInfo

Machine information, including OS information

| Attribute | Value |
|:----------|:------|
| **Category** | MDE |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/deviceinfo) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceinfo-table) |

## Solutions (4)

This table is used by the following solutions:

- [HIPAA Compliance](../solutions/hipaa-compliance.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)
- [Zinc Open Source](../solutions/zinc-open-source.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (5)

### Analytic Rules (4)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [AV detections related to SpringShell Vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/AVSpringShell.yaml)
- [AV detections related to Tarrask malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/AVTarrask.yaml)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [[Deprecated] Explicit MFA Deny](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/ExplicitMFADeny.yaml)

**In solution [Zinc Open Source](../solutions/zinc-open-source.md):**
- [AV detections related to Zinc actors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zinc%20Open%20Source/Analytic%20Rules/ZincOctober2022_AVHits_IOC.yaml)

### Workbooks (1)

**In solution [HIPAA Compliance](../solutions/hipaa-compliance.md):**
- [HIPAACompliance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/HIPAA%20Compliance/Workbooks/HIPAACompliance.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
