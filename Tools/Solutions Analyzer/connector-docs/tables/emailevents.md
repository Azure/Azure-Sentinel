# EmailEvents

Microsoft 365 email events, including email delivery and blocking events

| Attribute | Value |
|:----------|:------|
| **Category** | Defender |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/emailevents) |
| **Defender XDR Docs** | [View Documentation](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailevents-table) |

## Solutions (6)

This table is used by the following solutions:

- [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md)
- [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md)
- [Microsoft Business Applications](../solutions/microsoft-business-applications.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md)
- [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Defender XDR](../connectors/microsoftthreatprotection.md)

---

## Content Items Using This Table (128)

### Analytic Rules (1)

**In solution [Microsoft Business Applications](../solutions/microsoft-business-applications.md):**
- [Dataverse - Terminated employee exfiltration over email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Business%20Applications/Analytic%20Rules/Dataverse%20-%20Terminated%20employee%20exfiltration%20over%20email.yaml)

### Hunting Queries (123)

**In solution [Business Email Compromise - Financial Fraud](../solutions/business-email-compromise---financial-fraud.md):**
- [Email Forwarding Configuration with SAP download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/Emailforwarding_SAPdownload.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Authentication failures by time and authentication type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/Authentication%20failures.yaml)
- [Automated email notifications and suspicious sign-in activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Automated%20email%20notifications%20and%20suspicious%20sign-in%20activity.yaml)
- [Bad email percentage of Inbound emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Bad%20email%20percentage%20-%20Inbound%20emails.yaml)
- [Bulk Emails by Sender Bulk Complaint level](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Mails%20with%20BCL.yaml)
- [Calculate overall MDO efficacy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Calculate%20MDO%20Efficacy.yaml)
- [Campaign with suspicious keywords](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Campaign%20with%20suspicious%20keywords.yaml)
- [CompAuth Failure Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/CompAuth%20Failure%20Trend.yaml)
- [Custom detection-Emails with QR from non-prevalent senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Custom%20detection-Emails%20with%20QR%20from%20non-prevalent%20senders.yaml)
- [DKIM Failure Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/DKIM%20Failure%20Trend.yaml)
- [DMARC Failure Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/DMARC%20Failure%20Trend.yaml)
- [Detections by detection methods](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Detections%20by%20detection%20methods.yaml)
- [Determine Successfully Delivered Phishing Emails by top IP Addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Delivered%20Bad%20Emails%20from%20Top%20bad%20IPv4%20addresses.yaml)
- [Determine Successfully Delivered Phishing Emails to Inbox/Junk folder.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/EmailDelivered-ToInbox.yaml)
- [Display Name - Spoof and Impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Display%20Name%20-%20Spoof%20and%20Impersonation.yaml)
- [Email Top 10 Domains sending Spam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Top10%20Domains.yaml)
- [Email Top 10 Targeted Users (Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Top10%20Users.yaml)
- [Email Top 15 Domains sending Spam with Additional Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Top15%20Domains%20Details.yaml)
- [Email Top 15 Targeted Users (Spam) with Additional Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Top15%20Users%20Details.yaml)
- [Email Top Domains sending Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Top%20Domains%20sending%20Malware.yaml)
- [Email Top Domains sending Phish](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Top%20Domains%20sending%20Phish.yaml)
- [Email bombing attacks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Email%20bombing.yaml)
- [Email containing malware sent by an internal sender](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Email%20containing%20malware%20sent%20by%20an%20internal%20sender.yaml)
- [Email malware detection report](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Email%20malware%20detection%20report.yaml)
- [Email sender IP address Geo location information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Email%20sender%20IP%20address%20Geo%20location%20information.yaml)
- [Emails delivered having URLs from QR codes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Emails%20delivered%20having%20URLs%20from%20QR%20codes.yaml)
- [Emails with QR codes and suspicious keywords in subject](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Emails%20with%20QR%20codes%20and%20suspicious%20keywords%20in%20subject.yaml)
- [Emails with QR codes from non-prevalent sender](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Emails%20with%20QR%20codes%20from%20non-prevalent%20sender.yaml)
- [Files share contents and suspicious sign-in activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Files%20share%20contents%20and%20suspicious%20sign-in%20activity.yaml)
- [Good emails from senders with bad patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Good%20emails%20from%20senders%20with%20bad%20patterns.yaml)
- [High Confidence Phish Released](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/High%20Confidence%20Phish%20Released.yaml)
- [Hunt for email bombing attacks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Hunt%20for%20email%20bombing%20attacks.yaml)
- [Hunt for email conversation take over attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Hunt%20for%20email%20conversation%20take%20over%20attempts.yaml)
- [Hunting for sender patterns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Hunting%20for%20sender%20patterns.yaml)
- [Hunting for user signals-clusters](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Hunting%20for%20user%20signals-clusters.yaml)
- [Impersonation Detections Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Impersonation%20Phishing%20detections%20trend.yaml)
- [Impersonation Detections by Detection Technology](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Impersonation%20Phishing%20detections%20by%20Detection%20Technology.yaml)
- [Impersonation Detections by Detection Technology Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Impersonation%20Phishing%20detections%20by%20Detection%20Technology%20Trend.yaml)
- [Inbound emails with QR code URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Inbound%20emails%20with%20QR%20code%20URLs.yaml)
- [Listing Email Remediation Actions via Explorer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Remediation/Email%20remediation%20action%20list.yaml)
- [Local time to UTC time conversion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Local%20time%20to%20UTC%20time%20conversion.yaml)
- [MDO Threat Protection Detections trend over time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Total%20number%20of%20detections%20by%20MDO%20over%20time.yaml)
- [MDO_CountOfRecipientsEmailaddressbySubject](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/MDO_CountOfRecipientsEmailaddressbySubject.YAML)
- [MDO_CountOfSendersEmailaddressbySubject](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/MDO_CountOfSendersEmailaddressbySubject.YAML)
- [MDO_Countofrecipientsemailaddressesbysubject](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/MDO_Countofrecipientsemailaddressesbysubject.YAML)
- [MDO_SummaryOfSenders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/MDO_SummaryOfSenders.YAML)
- [Mail reply to new domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Mail%20reply%20to%20new%20domain.yaml)
- [Mailflow by directionality](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Mailflow%20by%20directionality.yaml)
- [Malicious Emails with QR code Urls](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/Malicious%20Emails%20with%20QR%20code%20Urls.yaml)
- [Malicious email senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Malicious%20email%20senders.yaml)
- [Malicious emails detected per day](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Malicious%20emails%20detected%20per%20day.yaml)
- [Malicious mails by sender IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Top%20Attacks/Malicious%20mails%20by%20sender%20IPs.yaml)
- [Malware Detections Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Malware%20Detection%20Trend.yaml)
- [Malware Detections by Detection technology](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Malware%20Detections%20by%20Detection%20Technology.yaml)
- [Malware Detections by Detection technology Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Malware%20Detections%20by%20Detection%20Technology%20Trend.yaml)
- [Malware Detections by delivery location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Malware%20Detections%20by%20Delivery%20Location.yaml)
- [Message from an Accepted Domain with DMARC TempError](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Custom%20Detections/Message%20from%20Accepted%20Domain%20with%20DMARC%20TempError.yaml)
- [Personalized campaigns based on the first few keywords](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Personalized%20campaigns%20based%20on%20the%20first%20few%20keywords.yaml)
- [Personalized campaigns based on the last few keywords](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/QR%20code/Personalized%20campaigns%20based%20on%20the%20last%20few%20keywords.yaml)
- [Phish Detections (High) by delivery location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Phish%20Detections%20by%20Delivery%20Location%20-%20High.yaml)
- [Phish Detections (Normal) by delivery location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Phish%20Detections%20by%20Delivery%20Location%20-%20Medium.yaml)
- [Phish Detections Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Phish%20Detection%20Trend.yaml)
- [Phish Detections by Detection technology](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Phish%20Detections%20by%20Detection%20Technology.yaml)
- [Phish Detections by Detection technology Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Phish%20Detections%20by%20Detection%20Technology%20Trend.yaml)
- [Phish Detections by delivery location trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Phish%20Detections%20by%20Delivery%20Location%20Trend.yaml)
- [Quarantine Phish Reason](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20Phish%20reason.yaml)
- [Quarantine Phish Reason trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20Phish%20reason%20trend.yaml)
- [Quarantine Release Email Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20Release%20Email%20Details.yaml)
- [Quarantine Spam Reason](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20Spam%20reason.yaml)
- [Quarantine Spam Reason trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Quarantine/Quarantine%20Spam%20reason%20trend.yaml)
- [SPF Failure Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/SPF%20Failure%20Trend.yaml)
- [Safe Attachments detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Attachment/Safe%20attachment%20detection.yaml)
- [SafeLinks URL detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/URL/SafeLinks%20URL%20detections.yaml)
- [Sender recipient contact establishment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Sender%20recipient%20contact%20establishment.yaml)
- [Spam Detections (High) by delivery location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Spam%20Detections%20by%20Delivery%20Location%20-%20High.yaml)
- [Spam Detections (Normal) by delivery location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Spam%20Detections%20by%20Delivery%20Location%20-%20Medium.yaml)
- [Spam Detections by Detection technology](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detections%20by%20Detection%20technology.yaml)
- [Spam and Phish allowed to inbox by Admin Overrides](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Spam%20and%20Phish%20delivered%20to%20Inbox%20due%20to%20Admin%20Overrides.yaml)
- [Spam and Phish allowed to inbox by User Overrides](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Spam%20and%20Phish%20delivered%20to%20Inbox%20due%20to%20User%20Overrides.yaml)
- [Spam detection by IP and its location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20IP%20and%20Geo%20Position.yaml)
- [Spam detection by delivery location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Delivery%20Location.yaml)
- [Spam detection technologies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Tech.yaml)
- [Spam detection trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Spam%20Detection%20Trend.yaml)
- [Spoof Detections Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Spoof%20detections%20trend.yaml)
- [Spoof Detections by Detection Technology](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Spoof%20detections%20by%20Detection%20Technology.yaml)
- [Spoof Detections by Detection Technology Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Spoof%20detections%20by%20Detection%20Technology%20Trend.yaml)
- [Spoof and impersonation detections by sender IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Spoof%20and%20impersonation%20detections%20by%20sender%20IP.yaml)
- [Spoof and impersonation phish detections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Spoof%20and%20impersonation%20phish%20detections.yaml)
- [Spoof attempts with auth failure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/Spoof%20attempts%20with%20auth%20failure.yaml)
- [Spoofing attempts from Specific Domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Check%20for%20spoofing%20attempts%20on%20the%20domain%20with%20Authentication%20failures.yaml)
- [Top 10 Domains sending Malicious Emails (Malware+Phish+Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20Domains%20sending%20Malicious%20Emails%20%28Malware%2BPhish%2BSpam%29.yaml)
- [Top 10 External Senders (Malware)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20External%20Senders%20%28Malware%29.yaml)
- [Top 10 External Senders (Phish)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20External%20Senders%20%28Phish%29.yaml)
- [Top 10 External Senders (Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20External%20Senders%20%28Spam%29.yaml)
- [Top 10 External Senders (Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20External%20Senders.yaml)
- [Top 10 Targeted Users (Malware+Phish+Spam)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Top%2010%20Targeted%20Users%20%28Malware%2BPhish%2BSpam%29.yaml)
- [Top 10 URL domains attacking organization](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Top%20Attacks/Top%2010%20URL%20domains%20attacking%20organization.yaml)
- [Top 10 domains sending Bulk email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spam/Bulk%20Detection%20Top10%20Domains.yaml)
- [Top 100 malicious email senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Top%20100%20malicious%20email%20senders.yaml)
- [Top 100 senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Top%20100%20senders.yaml)
- [Top Domains Outbound with Emails with Threats Inbound (Partner BEC)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Top%20Domains%20with%20BEC%20Threats%20inbound.yaml)
- [Top Malware Families](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Top%20Email%20Malware%20Families.yaml)
- [Top Spoof DMARC detections by Sender domain (P1/P2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/Top%20Spoof%20DMARC%20detections%20by%20Sender%20Domain.yaml)
- [Top Spoof external domain detections by Sender domain (P1/P2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/Top%20Spoof%20detections%20by%20Sender%20Domain.yaml)
- [Top Spoof intra-org detections by Sender domain (P1/P2)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Authentication/Top%20Spoof%20Intra-Org%20detections%20by%20SenderDomain.yaml)
- [Top Users receiving Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Top%20Users%20receiving%20Malware.yaml)
- [Top Users receiving Phish](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Top%20Users%20receiving%20Phish.yaml)
- [Top external malicious senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Top%20Attacks/Top%20external%20malicious%20senders.yaml)
- [Top outbound recipient domains sending inbound emails with threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Hunting/Top%20outbound%20recipient%20domains%20sending%20inbound%20emails%20with%20threats.yaml)
- [Top policies performing admin overrides](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Top%20policies%20performing%20admin%20overrides.yaml)
- [Top policies performing user overrides](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Top%20policies%20performing%20user%20overrides.yaml)
- [Top targeted users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Top%20Attacks/Top%20targeted%20users.yaml)
- [Total Emails with Admin Overrides (Allow)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Total%20Emails%20with%20Admin%20Overrides%20-%20Allow.yaml)
- [Total Emails with Admin Overrides (Block)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Total%20Emails%20with%20Admin%20Overrides%20-%20Block.yaml)
- [Total Emails with User Overrides (Allow)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Total%20Emails%20with%20User%20Overrides%20-%20Allow.yaml)
- [Total Emails with User Overrides (Block)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Overrides/Total%20Emails%20with%20User%20Overrides%20-%20Block.yaml)
- [Total number of detections by MDO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/General/Total%20number%20of%20detections%20by%20MDO.yaml)
- [User Email Submissions (FN) - Top Inbound P2 Senders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20-%20Top%20email%20%28P2%29%20senders.yaml)
- [User Email Submissions (FN) - Top Inbound P2 Senders domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Submissions/User%20Submissions%20-%20Top%20email%20%28P2%29%20senders%20domains.yaml)
- [Zero day threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Mailflow/Zero%20day%20threats.yaml)
- [Zero-day Malware Detections Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Malware/Zero-day%20Malware%20Detections%20Trend.yaml)
- [Zero-day Phish Detections Trend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Phish/Zero-day%20Phish%20Detections%20Trend.yaml)
- [referral-phish-emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Hunting%20Queries/Email%20and%20Collaboration%20Queries/Spoof%20and%20Impersonation/Referral%20phish%20emails.yaml)

### Workbooks (4)

**In solution [MaturityModelForEventLogManagementM2131](../solutions/maturitymodelforeventlogmanagementm2131.md):**
- [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [MicrosoftDefenderForOffice365detectionsandinsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Workbooks/MicrosoftDefenderForOffice365detectionsandinsights.json)

**In solution [Microsoft Defender for Office 365](../solutions/microsoft-defender-for-office-365.md):**
- [MicrosoftDefenderForOffice365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Office%20365/Workbooks/MicrosoftDefenderForOffice365.json)

**In solution [ZeroTrust(TIC3.0)](../solutions/zerotrust%28tic3.0%29.md):**
- [ZeroTrustTIC3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroTrust%28TIC3.0%29/Workbooks/ZeroTrustTIC3.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
