# Proofpoint On demand(POD) Email Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Proofpoint, Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://proofpoint.my.site.com/community/s/](https://proofpoint.my.site.com/community/s/) |
| **Categories** | domains |
| **First Published** | 2021-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md)
- [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md)

## Tables Reference

This solution uses **8 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md) | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md), [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) | Analytics, Hunting, Workbooks |
| [`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md) | [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md), [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) | Analytics, Hunting, Workbooks |
| [`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md) | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) | Analytics, Hunting, Workbooks |
| [`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md) | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) | Analytics, Hunting, Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Analytics |
| [`maillog_CL`](../tables/maillog-cl.md) | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) | Analytics, Hunting, Workbooks |
| [`message_CL`](../tables/message-cl.md) | [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md) | Analytics, Hunting, Workbooks |
| [`trend_result`](../tables/trend-result.md) | - | Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [ProofpointPOD - Binary file in attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODBinaryInAttachment.yaml) | Medium | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Email sender IP in TI list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODEmailSenderIPinTIList.yaml) | Medium | Exfiltration, InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Email sender in TI list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODEmailSenderInTIList.yaml) | Medium | Exfiltration, InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - High risk message not discarded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODHighRiskNotDiscarded.yaml) | Low | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Multiple archived attachments to the same recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODMultipleArchivedAttachmentsToSameRecipient.yaml) | Medium | Exfiltration | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Multiple large emails to the same recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODMultipleLargeEmailsToSameRecipient.yaml) | Medium | Exfiltration | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Multiple protected emails to unknown recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODMultipleProtectedEmailsToUnknownRecipient.yaml) | Medium | Exfiltration | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Possible data exfiltration to private email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODDataExfiltrationToPrivateEmail.yaml) | Medium | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Suspicious attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODSuspiciousAttachment.yaml) | Medium | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Weak ciphers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODWeakCiphers.yaml) | Low | CommandAndControl | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [ProofpointPOD - Emails with high score of 'adult' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreAdultValue.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Emails with high score of 'malware' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreMalwareValue.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Emails with high score of 'phish' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScorePhishValue.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Emails with high score of 'spam' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreSpamValue.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Emails with high score of 'suspect' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreSuspectValue.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Large size outbound emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODLargeOutboundEmails.yaml) | Exfiltration | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Recipients with high number of discarded or rejected emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODRecipientsHighNumberDiscardReject.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Recipients with large number of corrupted emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODRecipientsLargeNumberOfCorruptedEmails.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Senders with large number of corrupted messages](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODSendersLargeNumberOfCorruptedEmails.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |
| [ProofpointPOD - Suspicious file types in attachments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODSuspiciousFileTypesInAttachments.yaml) | InitialAccess | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ProofpointPOD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Workbooks/ProofpointPOD.json) | [`ProofpointPODMailLog_CL`](../tables/proofpointpodmaillog-cl.md)<br>[`ProofpointPODMessage_CL`](../tables/proofpointpodmessage-cl.md)<br>[`ProofpointPOD_maillog_CL`](../tables/proofpointpod-maillog-cl.md)<br>[`ProofpointPOD_message_CL`](../tables/proofpointpod-message-cl.md)<br>[`maillog_CL`](../tables/maillog-cl.md)<br>[`message_CL`](../tables/message-cl.md)<br>[`trend_result`](../tables/trend-result.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ProofpointPOD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Parsers/ProofpointPOD.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                   |
|-------------|--------------------------------|------------------------------------------------------|
| 3.1.2       | 08-12-2025                     | Update **ProofpointPOD_PollingConfig.json** to remove start and end time query params, it impacts time frames at server side and causes duplicate data ingestion.|  
| 3.1.1       | 03-11-2025                     | Update support url in **SolutionMetadata.json**.|  
| 3.1.0       | 31-07-2025                     | Updated Support details and publisherId in **SolutionMetadata.json**, updated Author details and Logo in **Solution_ProofPointPOD.json** from Microsoft to Proofpoint.|
| 3.0.5       | 28-07-2025                     | Removed Deprecated **Data Connector**.							|  
| 3.0.4       | 06-05-2025                     | Launching CCP **Data Connector** - *Proofpoint On Demand Email Security* from Public Preview to Global Availability.           |
| 3.0.3       | 12-03-2025                     | Added new CCP **Data Connector** - *Proofpoint On Demand Email Security*.            |
| 3.0.2       | 06-09-2024                     | Updated the python runtime version to 3.11 in **Data Connector** Function App.           |
| 3.0.1       | 02-05-2024                     | Optimized **Parser**.                                      |
| 3.0.0       | 01-08-2023                     | Updated solution logo with Microsoft Sentinel logo.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
