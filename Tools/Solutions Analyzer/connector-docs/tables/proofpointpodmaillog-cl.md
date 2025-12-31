# ProofpointPODMailLog_CL

## Solutions (1)

This table is used by the following solutions:

- [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand%28pod%29-email-security.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Proofpoint On Demand Email Security (via Codeless Connector Platform)](../connectors/proofpointccpdefinition.md)
- [[Deprecated] Proofpoint On Demand Email Security](../connectors/proofpointpod.md)

---

## Content Items Using This Table (21)

### Analytic Rules (10)

**In solution [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand%28pod%29-email-security.md):**
- [ProofpointPOD - Binary file in attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODBinaryInAttachment.yaml)
- [ProofpointPOD - Email sender IP in TI list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODEmailSenderIPinTIList.yaml)
- [ProofpointPOD - Email sender in TI list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODEmailSenderInTIList.yaml)
- [ProofpointPOD - High risk message not discarded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODHighRiskNotDiscarded.yaml)
- [ProofpointPOD - Multiple archived attachments to the same recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODMultipleArchivedAttachmentsToSameRecipient.yaml)
- [ProofpointPOD - Multiple large emails to the same recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODMultipleLargeEmailsToSameRecipient.yaml)
- [ProofpointPOD - Multiple protected emails to unknown recipient](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODMultipleProtectedEmailsToUnknownRecipient.yaml)
- [ProofpointPOD - Possible data exfiltration to private email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODDataExfiltrationToPrivateEmail.yaml)
- [ProofpointPOD - Suspicious attachment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODSuspiciousAttachment.yaml)
- [ProofpointPOD - Weak ciphers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Analytic%20Rules/ProofpointPODWeakCiphers.yaml)

### Hunting Queries (10)

**In solution [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand%28pod%29-email-security.md):**
- [ProofpointPOD - Emails with high score of 'adult' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreAdultValue.yaml)
- [ProofpointPOD - Emails with high score of 'malware' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreMalwareValue.yaml)
- [ProofpointPOD - Emails with high score of 'phish' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScorePhishValue.yaml)
- [ProofpointPOD - Emails with high score of 'spam' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreSpamValue.yaml)
- [ProofpointPOD - Emails with high score of 'suspect' filter classifier value](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODHighScoreSuspectValue.yaml)
- [ProofpointPOD - Large size outbound emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODLargeOutboundEmails.yaml)
- [ProofpointPOD - Recipients with high number of discarded or rejected emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODRecipientsHighNumberDiscardReject.yaml)
- [ProofpointPOD - Recipients with large number of corrupted emails](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODRecipientsLargeNumberOfCorruptedEmails.yaml)
- [ProofpointPOD - Senders with large number of corrupted messages](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODSendersLargeNumberOfCorruptedEmails.yaml)
- [ProofpointPOD - Suspicious file types in attachments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Hunting%20Queries/ProofpointPODSuspiciousFileTypesInAttachments.yaml)

### Workbooks (1)

**In solution [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand%28pod%29-email-security.md):**
- [ProofpointPOD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Workbooks/ProofpointPOD.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
