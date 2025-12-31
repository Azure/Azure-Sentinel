# UrlClickEvents

Safe Links clicks from email messages, Teams, and Office 365 apps

| Attribute | Value |
|:----------|:------|
| **Category** | Security, XDR |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/urlclickevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-urlclickevents-table) |

## Solutions (1)

This table is used by the following solutions:

- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (21)

### Hunting Queries (20)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Blocked Clicks Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Blocked%20Clicks%20Trend.yml)
- [End user malicious clicks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/End%20user%20malicious%20clicks.yaml)
- [MDO_URLClickedinEmail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/MDO_URLClickedinEmail.YAML)
- [Malicious Clicks allowed (click-through)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Malicious%20Clicks%20allowed%20%28click-through%29.yaml)
- [Malicious URL Clicks by workload](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Malicious%20URL%20Clicks%20by%20workload.yml)
- [Teams URL clicks actions summarized by URLs clicked on](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20URL%20clicks%20actions%20summarized%20by%20URLs%20clicked%20on.yaml)
- [Teams URL clicks through actions on Phish or Malware URLs summarized by URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20URL%20clicks%20through%20actions%20on%20Phish%20or%20Malware%20URLs%20summarized%20by%20URLs.yaml)
- [Teams blocked URL clicks daily trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20blocked%20URL%20clicks%20daily%20trend.yaml)
- [Top 10 Users clicking on Malicious URLs (Malware)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Top%2010%20Users%20clicking%20on%20Malicious%20URLs%20%28Malware%29.yaml)
- [Top 10 Users clicking on Malicious URLs (Malware+Phish+Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20Users%20clicking%20on%20Malicious%20URLs%20%28Malware%2BPhish%2BSpam%29.yaml)
- [Top 10 Users clicking on Malicious URLs (Phish)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Top%2010%20Users%20clicking%20on%20Malicious%20URLs%20%28Phish%29.yaml)
- [Top 10 Users clicking on Malicious URLs (Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Top%2010%20Users%20clicking%20on%20Malicious%20URLs%20%28Spam%29.yaml)
- [Top 10 Users clicking on malicious URLs in Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%2010%20Users%20clicking%20on%20malicious%20URLs%20in%20Teams.yaml)
- [Top malicious URLs clicked by users in Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%20malicious%20URLs%20clicked%20by%20users%20in%20Teams.yaml)
- [URL Click attempts by threat type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/URL%20Click%20attempts%20by%20threat%20type.yaml)
- [URL Clicks by Action](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/URL%20Clicks%20by%20Action.yaml)
- [URL click count by click action](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/URL%20click%20count%20by%20click%20action.yaml)
- [URL clicks actions by URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/URL%20clicks%20actions%20by%20URL.yaml)
- [User clicked through events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/User%20clicked%20through%20events.yaml)
- [User clicks on phishing URLs in emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL%20Click/User%20clicks%20on%20phishing%20URLs%20in%20emails.yaml)

### Workbooks (1)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForOffice365detectionsandinsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
