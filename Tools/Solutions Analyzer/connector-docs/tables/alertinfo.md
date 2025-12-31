# AlertInfo

Alerts from Microsoft Defender for Endpoint, Microsoft Defender for Office 365, Microsoft Defender for Cloud Apps, and Microsoft Defender for Identity, including severity information and threat categorization

| Attribute | Value |
|:----------|:------|
| **Category** | Internal |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/alertinfo) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table) |

## Solutions (1)

This table is used by the following solutions:

- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)

---

## Content Items Using This Table (7)

### Analytic Rules (1)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Potential Ransomware activity related to Cobalt Strike](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Ransomware/PotentialCobaltStrikeRansomwareActivity.yaml)

### Hunting Queries (6)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Alerts Related to Log4j Vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Log4j/Log4jVulnRelatedAlerts.yaml)
- [Devices with Log4j vulnerability alerts and additional other alert related context](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Campaigns/Log4j/DeviceWithLog4jAlerts.yaml)
- [Microsoft Teams chat initiated by a suspicious external user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Microsoft%20Teams%20chat%20initiated%20by%20a%20suspicious%20external%20user.yaml)
- [Potential Ransomware activity related to Cobalt Strike](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Ransomware/PotentialCobaltStrikeRansomwareActivity.yaml)
- [URL click on ZAP email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/URL%20click%20on%20ZAP%20Email.yaml)
- [URLClick details based on malicious URL click alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/URLClick%20details%20based%20on%20malicious%20URL%20click%20alert.yaml)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
