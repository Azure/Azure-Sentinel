# AWS Security Hub

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-03-12 |
| **Last Updated** | 2025-03-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [AWS Security Hub Findings (via Codeless Connector Framework)](../connectors/awssecurityhubfindingsccpdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) | [AWS Security Hub Findings (via Codeless Connector Framework)](../connectors/awssecurityhubfindingsccpdefinition.md) | Analytics, Hunting |

## Content Items

This solution includes **11 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 8 |
| Hunting Queries | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [AWS Security Hub - Detect CloudTrail trails lacking KMS encryption](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/CloudTrailTrailEncryptionDisabled.yaml) | Medium | Impact, DefenseEvasion | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect EC2 Security groups allowing unrestricted high-risk ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/EC2SecurityGroupHighRiskOpenPorts.yaml) | High | InitialAccess, LateralMovement, Discovery | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect IAM Policies allowing full administrative privileges](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/IAMPolicyWithFullAdminPriv.yaml) | High | Persistence, PrivilegeEscalation | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect IAM root user Access Key existence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/IAMRootUserWithAccessKey.yaml) | High | PrivilegeEscalation, Persistence | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect SQS Queue lacking encryption at rest](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/SQSQueueNotEncrypted.yaml) | Medium | Impact | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect SQS Queue policy allowing public access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/SQSQueuePublicAccess.yaml) | High | Exfiltration, Collection | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect SSM documents public sharing enabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/SSMDocumentsPublicSharingEnabled.yaml) | High | Execution | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - Detect root user lacking MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Analytic%20Rules/IAMRootUserMFADisabled.yaml) | High | PrivilegeEscalation, Persistence, CredentialAccess, DefenseEvasion | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [AWS Security Hub - CloudTrail trails without log file validation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Hunting%20Queries/CloudTrailLogFileValidationDisabled.yaml) | DefenseEvasion | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - EC2 instances with public IPv4 address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Hunting%20Queries/EC2InstancePublicIPv4.yaml) | InitialAccess, Exfiltration | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |
| [AWS Security Hub - IAM users with console password and no MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Security%20Hub/Hunting%20Queries/IAMUserMFADisabled.yaml) | PrivilegeEscalation, CredentialAccess, DefenseEvasion | [`AWSSecurityHubFindings`](../tables/awssecurityhubfindings.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 27-08-2025                     | AWS Security Hub added **Analytical Rule** and **Hunting Queries** |
| 3.0.1       | 27-06-2025                     | AWS Security Hub **CCF Data Connector** moving to GA |
| 3.0.0       | 14-05-2025                     | New **Data Connector**, Pre Release    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
