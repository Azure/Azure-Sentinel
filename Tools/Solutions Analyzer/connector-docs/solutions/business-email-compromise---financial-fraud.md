# Business Email Compromise - Financial Fraud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2023-08-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **8 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AWSS3BucketAPILogParsed`](../tables/awss3bucketapilogparsed.md) | Hunting |
| [`AuditLogs`](../tables/auditlogs.md) | Analytics, Hunting |
| [`AwsBucketAPILogs_CL`](../tables/awsbucketapilogs-cl.md) | Hunting |
| [`EmailEvents`](../tables/emailevents.md) | Hunting |
| [`OfficeActivity`](../tables/officeactivity.md) | Analytics, Hunting |
| [`SAPAuditLog`](../tables/sapauditlog.md) | Hunting |
| [`SigninLogs`](../tables/signinlogs.md) | Hunting |
| [`aadFunc`](../tables/aadfunc.md) | Hunting |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Hunting |
| [`IdentityInfo`](../tables/identityinfo.md) | Hunting |

## Content Items

This solution includes **20 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 13 |
| Analytic Rules | 7 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Account Elevated to New Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/AccountElevatedtoNewRole.yaml) | Medium | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [Authentication Method Changed for Privileged Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/AuthenticationMethodChangedforPrivilegedAccount.yaml) | High | Persistence | - |
| [Malicious BEC Inbox Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/BEC_MailboxRule.yaml) | Medium | Persistence, DefenseEvasion | [`OfficeActivity`](../tables/officeactivity.md) |
| [Privileged Account Permissions Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/PrivilegedAccountPermissionsChanged.yaml) | Medium | PrivilegeEscalation | - |
| [Suspicious access of BEC related documents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/SuspiciousAccessOfBECRelatedDocuments.yaml) | Medium | Collection | - |
| [Suspicious access of BEC related documents in AWS S3 buckets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/SuspiciousAccessOfBECRelatedDocumentsInAWSS3Buckets.yaml) | Medium | Collection | - |
| [User Added to Admin Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Analytic%20Rules/UserAddedtoAdminRole.yaml) | Low | PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Email Forwarding Configuration with SAP download](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/Emailforwarding_SAPdownload.yaml) | InitialAccess, Collection, Exfiltration | [`EmailEvents`](../tables/emailevents.md)<br>[`SAPAuditLog`](../tables/sapauditlog.md) |
| [High count download from a SAP Privileged account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/SAP_HighdownloadfromPriviledgedaccount.yaml) | InitialAccess, Exfiltration | [`SAPAuditLog`](../tables/sapauditlog.md) |
| [Login attempts using Legacy Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/LegacyAuthAttempt.yaml) | InitialAccess, Persistence | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Microsoft Entra ID signins from new locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/new_locations_azuread_signin.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Office Mail Rule Creation with suspicious archive mail move activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/OfficeMailRuleCreationWithMailMoveActivity.yaml) | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Risky Sign-in with new MFA method](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/riskSignInWithNewMFAMethod.yaml) | Persistence | [`AuditLogs`](../tables/auditlogs.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [S3 Bucket outbound Data transfer anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/AWSBucketAPILogs-S3BucketDataTransferTimeSeriesAnomaly.yaml) | Exfiltration | [`AWSS3BucketAPILogParsed`](../tables/awss3bucketapilogparsed.md)<br>[`AwsBucketAPILogs_CL`](../tables/awsbucketapilogs-cl.md) |
| [Successful Signin From Non-Compliant Device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/SuccessfulSigninFromNon-CompliantDevice.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Suspicious Data Access to S3 Bucket from Unknown IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/AWSBucketAPILogs-SuspiciousDataAccessToS3BucketsfromUnknownIP.yaml) | Collection | [`AWSS3BucketAPILogParsed`](../tables/awss3bucketapilogparsed.md) |
| [User Accounts - New Single Factor Auth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserAccounts-NewSingleFactorAuth.yaml) | InitialAccess | [`aadFunc`](../tables/aadfunc.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [User Accounts - Unusual authentications occurring when countries do not conduct normal business operations.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserAccounts-UnusualLogonTimes.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [User Login IP Address Teleportation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserLoginIPAddressTeleportation.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [User detection added to privilege groups based in Watchlist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Business%20Email%20Compromise%20-%20Financial%20Fraud/Hunting%20Queries/UserDetectPrivilegeGroup.yaml) | Reconnaissance, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.10       | 10-11-2025                     | Update in **Analytical Rule** alert description                                          |
| 3.0.9       | 05-06-2024                     | **Analytical Rule** description updated                                          |
| 3.0.8       | 04-04-2024                     | Updated **Entity Mappings**                                                     |
| 3.0.7       | 28-02-2024                     | Removed usage of BlastRadius from **Hunting Queries**                        |
| 3.0.6       | 16-02-2024                     | Updated the solution to fix **Analytic Rules** deployment issue                               |
| 3.0.5       | 08-02-2024                     | Tagged for dependent solutions for deployment                                |
| 3.0.4       | 10-01-2024                     | Updated **Analytic Rule** (AuthenticationMethodChangedforPrivilegedAccount.yaml)         |
| 3.0.3       | 23-11-2023                     | Updated description of **Hunting query**                                     | 
| 3.0.2       | 06-11-2023                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR |
| 3.0.1       | 03-11-2023                     | Updated **Analytic Rule** datatype and descriptions for **Hunting queries**  |
| 3.0.0       | 07-08-2023                     | Initial Solution Release                                                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
