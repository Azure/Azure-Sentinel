# AWSSecurityHubFindings

Reference for AWSSecurityHubFindings table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | AWS |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/awssecurityhubfindings) |

## Solutions (1)

This table is used by the following solutions:

- [AWS Security Hub](../solutions/aws-security-hub.md)

## Connectors (1)

This table is ingested by the following connectors:

- [AWS Security Hub Findings (via Codeless Connector Framework)](../connectors/awssecurityhubfindingsccpdefinition.md)

---

## Content Items Using This Table (11)

### Analytic Rules (8)

**In solution [AWS Security Hub](../solutions/aws-security-hub.md):**
- [AWS Security Hub - Detect CloudTrail trails lacking KMS encryption](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/CloudTrailTrailEncryptionDisabled.yaml)
- [AWS Security Hub - Detect EC2 Security groups allowing unrestricted high-risk ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/EC2SecurityGroupHighRiskOpenPorts.yaml)
- [AWS Security Hub - Detect IAM Policies allowing full administrative privileges](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/IAMPolicyWithFullAdminPriv.yaml)
- [AWS Security Hub - Detect IAM root user Access Key existence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/IAMRootUserWithAccessKey.yaml)
- [AWS Security Hub - Detect SQS Queue lacking encryption at rest](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/SQSQueueNotEncrypted.yaml)
- [AWS Security Hub - Detect SQS Queue policy allowing public access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/SQSQueuePublicAccess.yaml)
- [AWS Security Hub - Detect SSM documents public sharing enabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/SSMDocumentsPublicSharingEnabled.yaml)
- [AWS Security Hub - Detect root user lacking MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/IAMRootUserMFADisabled.yaml)

### Hunting Queries (3)

**In solution [AWS Security Hub](../solutions/aws-security-hub.md):**
- [AWS Security Hub - CloudTrail trails without log file validation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Hunting%20Queries/CloudTrailLogFileValidationDisabled.yaml)
- [AWS Security Hub - EC2 instances with public IPv4 address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Hunting%20Queries/EC2InstancePublicIPv4.yaml)
- [AWS Security Hub - IAM users with console password and no MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Hunting%20Queries/IAMUserMFADisabled.yaml)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
