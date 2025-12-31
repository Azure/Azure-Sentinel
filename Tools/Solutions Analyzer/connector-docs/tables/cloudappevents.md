# CloudAppEvents

Events involving accounts and objects in Office 365 and other cloud apps and services

| Attribute | Value |
|:----------|:------|
| **Category** | Security, XDR |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/cloudappevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table) |

## Solutions (4)

This table is used by the following solutions:

- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (70)

### Analytic Rules (4)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [Preview - TI map Domain entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/DomainEntity_CloudAppEvents.yaml)
- [Preview - TI map IP entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_CloudAppEvents.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map Domain entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/DomainEntity_CloudAppEvents_Updated.yaml)
- [TI map IP entity to Cloud App Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_CloudAppEvents_Updated.yaml)

### Hunting Queries (64)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [AIR investigation actions insight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Remediation/AIR%20investigation%20actions%20insight.yaml)
- [ATP policy status check](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Attachment/ATP%20policy%20status%20check.yaml)
- [Admin Submission Trend (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submission%20Trend%20-%20FN.yaml)
- [Admin Submission Trend (FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submission%20Trend%20-%20FP.yaml)
- [Admin Submissions by Detection Type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Detection%20Type.yaml)
- [Admin Submissions by DetectionMethod (Phish FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Detection%20Method%20-%20Phish%20FP.yaml)
- [Admin Submissions by DetectionMethod (Spam FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Detection%20Method%20-%20Spam%20FP.yaml)
- [Admin Submissions by Grading verdict (FN-FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Grading%20Verdict%20-%20FN-FP.yaml)
- [Admin Submissions by Submission State (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Submission%20State%20-%20FN.yaml)
- [Admin Submissions by Submission State (FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Submission%20State%20-%20FP.yaml)
- [Admin Submissions by Submission Type (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Submission%20Type%20-%20FN.yaml)
- [Admin Submissions by Submission Type (FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Admin%20Submissions%20by%20Submission%20Type%20-%20FP.yaml)
- [Audit Email Preview-Download action](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Audit%20Email%20Preview-Download%20action.yaml)
- [BEC - File sharing tactics - Dropbox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/BEC%20-%20File%20sharing%20tactics%20-%20Dropbox.yaml)
- [BEC - File sharing tactics - OneDrive or SharePoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/BEC%20-%20File%20sharing%20tactics%20-%20OneDrive%20or%20SharePoint.yaml)
- [Calculate overall MDO efficacy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Calculate%20MDO%20Efficacy.yaml)
- [File Malware Detection Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/File%20Malware%20Detection%20Trend.yaml)
- [File Malware by Top Malware Families (Anti Virus)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/File%20Malware%20Top%20Families%20by%20AV.yaml)
- [File Malware by Top Malware Families (Safe Attachments)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/File%20Malware%20Top%20Families%20by%20Safe%20Attachments.yaml)
- [Group quarantine release](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Group%20quarantine%20release.yaml)
- [High Confidence Phish Released](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/High%20Confidence%20Phish%20Released.yaml)
- [Hunt for Admin email access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Hunt%20for%20Admin%20email%20access.yaml)
- [Hunt for TABL changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Hunt%20for%20TABL%20changes.yaml)
- [Inbox rule changes which forward-redirect email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Inbox%20rule%20change%20which%20forward-redirect%20email.yaml)
- [MDO daily detection summary report](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/MDO%20daily%20detection%20summary%20report.yaml)
- [Mail item accessed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Mail%20item%20accessed.yaml)
- [Malware detections by Workload Locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Malware%20detections%20by%20Workload%20Locations.yaml)
- [Malware detections by Workload Type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Malware%20detections%20by%20Workload%20Type.yaml)
- [New TABL Items](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/New%20TABL%20Items.yaml)
- [Number of unique accounts performing Teams message Admin submissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Number%20of%20unique%20accounts%20performing%20Teams%20message%20Admin%20submissions.yaml)
- [Number of unique accounts performing Teams message User  submissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Number%20of%20unique%20accounts%20performing%20Teams%20message%20User%20%20submissions.yaml)
- [Quarantine Release Email Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20Release%20Email%20Details.yaml)
- [Quarantine release trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20release%20trend.yaml)
- [Suspicious sign-in attempts from QR code phishing campaigns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Suspicious%20sign-in%20attempts%20from%20QR%20code%20phishing%20campaigns.yaml)
- [Teams Admin submission of Malware and Phish daily trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20Admin%20submission%20of%20Malware%20and%20Phish%20daily%20trend.yaml)
- [Teams Admin submission of No Threats daily trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20Admin%20submission%20of%20No%20Threats%20daily%20trend.yaml)
- [Teams Admin-User Submissions Grading Verdicts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20Admin-User%20Submissions%20Grading%20Verdicts.yaml)
- [Teams User submissions daily trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Teams%20User%20submissions%20daily%20trend.yaml)
- [Top 10 Detection Overrides - Admin Email Submissions (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Top%20Detection%20Overrides%20-%20Admin%20Submissions.yaml)
- [Top 10 sender domains - Admin Teams message submissions FN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%2010%20sender%20domains%20-%20Admin%20Teams%20message%20submissions%20FN.yaml)
- [Top 10 sender domains - Admin email submissions (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Top%20Sender%20Domains%20-%20Admin%20Submissions%20FN.yaml)
- [Top 10 sender domains - Admin email submissions (FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Top%20Sender%20Domains%20-%20Admin%20Submissions%20FP.yaml)
- [Top 10 sender domains - Teams user submissions FN or FP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%2010%20sender%20domains%20-%20Teams%20user%20submissions%20FN%20or%20FP.yaml)
- [Top 10 senders - Teams users submissions FN or FP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%2010%20senders%20-%20Teams%20users%20submissions%20FN%20or%20FP.yaml)
- [Top 10 senders of  Admin Teams message submissions FN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%2010%20senders%20of%20%20Admin%20Teams%20message%20submissions%20FN.yaml)
- [Top 10 senders of  Admin Teams message submissions FP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%2010%20senders%20of%20%20Admin%20Teams%20message%20submissions%20FP.yaml)
- [Top accounts performing Teams admin submissions FN or FP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%20accounts%20performing%20Teams%20admin%20submissions%20FN%20or%20FP.yaml)
- [Top accounts performing Teams user submissions FN or FP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Microsoft%20Teams%20protection/Top%20accounts%20performing%20Teams%20user%20submissions%20FN%20or%20FP.yaml)
- [Top accounts performing admin submissions (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Top%20accounts%20performing%20admin%20submissions%20-%20FN.yaml)
- [Top accounts performing admin submissions (FP)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Top%20accounts%20performing%20admin%20submissions%20-%20FP.yaml)
- [Top accounts performing user submissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Top%20accounts%20performing%20user%20submissions.yaml)
- [Total Submissions by Submission Type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Total%20Submissions%20by%20Submission%20Status.yaml)
- [Total Submissions by Submission Type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/Total%20Submissions%20by%20Submission%20Type.yaml)
- [User Email Submission Trend (FN)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20Trend%20-%20FN.yaml)
- [User Email Submissions (FN) - Top Detection Overrides by Admins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20-%20Top%20detection%20overrides%20by%20Admins.yaml)
- [User Email Submissions (FN) - Top Detection Overrides by Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20-%20Top%20detection%20overrides%20by%20Users.yaml)
- [User Email Submissions (FN) - Top Intra-Org P2 Senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20-%20Top%20Intra-Org%20P2%20senders.yaml)
- [User Email Submissions (FN) - Top Intra-Org Subjects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20-%20Top%20Intra-Org%20Subjects.yaml)
- [User Email Submissions (FN) by Submission Type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20by%20Submission%20Type.yaml)
- [User Email Submissions (FN-FP) by Grading verdict](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20by%20Grading%20Verdict%20-%20FN-FP.yaml)
- [User Email Submissions accuracy vs Admin review verdict](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submission%20Accuracy%20versus%20Admin%20Verdicts.yaml)
- [User Email Submissions by Admin review status (Mark and Notify)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20by%20Admin%20review%20status.yaml)
- [User email submissions (FN) from Junk Folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20from%20Junk%20Folder.yaml)
- [User reported submissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20reported%20submissions.yaml)

### Workbooks (2)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForOffice365detectionsandinsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
