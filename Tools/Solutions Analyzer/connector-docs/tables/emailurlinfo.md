# EmailUrlInfo

Information about URLs on emails

| Attribute | Value |
|:----------|:------|
| **Category** | Defender |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/emailurlinfo) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailurlinfo-table) |

## Solutions (4)

This table is used by the following solutions:

- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (12)

### Analytic Rules (2)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map Domain entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_EmailUrlInfo.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to EmailUrlInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_EmailUrlInfo_Updated.yaml)

### Hunting Queries (9)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Appspot Phishing Abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Appspot%20Phishing%20Abuse.yaml)
- [Appspot Phishing Abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Appspot%20phishing%20abuse.yaml)
- [Custom detection-Emails with QR from non-prevalent senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Custom%20detection-Emails%20with%20QR%20from%20non-prevalent%20senders.yaml)
- [Emails containing links to IP addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Emails%20containing%20links%20to%20IP%20addresses.yaml)
- [Malicious Emails with QR code Urls](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Malicious%20Emails%20with%20QR%20code%20Urls.yaml)
- [Message with URL listed on OpenPhish delivered into Inbox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Custom%20Detections/Message%20with%20URL%20listed%20on%20OpenPhish%20delivered%20into%20Inbox.yaml)
- [PhishingEmailUrlRedirector (1)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Phishing%20Email%20Url%20Redirector.yaml)
- [Potential OAuth phishing email delivered into Inbox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Custom%20Detections/Potential%20OAuth%20phishing%20email%20delivered%20into%20Inbox.yaml)
- [URLs by location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/URLs%20by%20location.yaml)

### Workbooks (1)

**In solution [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md):**
- [MicrosoftDefenderForOffice365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Workbooks/MicrosoftDefenderForOffice365.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
