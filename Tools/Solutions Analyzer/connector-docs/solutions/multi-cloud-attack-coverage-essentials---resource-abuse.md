# Multi Cloud Attack Coverage Essentials - Resource Abuse

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-11-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **4 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AWSCloudTrail`](../tables/awscloudtrail.md) | Analytics |
| [`AWSGuardDuty`](../tables/awsguardduty.md) | Analytics |
| [`GCPAuditLogs`](../tables/gcpauditlogs.md) | Analytics |
| [`SigninLogs`](../tables/signinlogs.md) | Analytics |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`IdentityInfo`](../tables/identityinfo.md) | Analytics |
| [`SecurityAlert`](../tables/securityalert.md) | Analytics |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 9 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cross-Cloud Password Spray detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/BrutforceAttemptOnAzurePortalAndAWSConsolAtSameTime.yaml) | Medium | CredentialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Cross-Cloud Suspicious Compute resource creation in GCP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/Cross-CloudSuspiciousComputeResourcecreationinGCP.yaml) | Low | InitialAccess, Execution, Persistence, PrivilegeEscalation, CredentialAccess, Discovery, LateralMovement | [`AWSGuardDuty`](../tables/awsguardduty.md)<br>[`GCPAuditLogs`](../tables/gcpauditlogs.md) |
| [Cross-Cloud Suspicious user activity observed in GCP Envourment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/CrossCloudSuspiciousUserActivityObservedInGCPEnvourment.yaml) | Medium | InitialAccess, Execution, Persistence, PrivilegeEscalation, CredentialAccess, Discovery | [`GCPAuditLogs`](../tables/gcpauditlogs.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Cross-Cloud Unauthorized Credential Access Detection From AWS RDS Login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/CrossCloudUnauthorizedCredentialsAccessDetection.yaml) | Medium | CredentialAccess, InitialAccess | [`AWSGuardDuty`](../tables/awsguardduty.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [High-Risk Cross-Cloud User Impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/UserImpersonateByRiskyUser.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`SigninLogs`](../tables/signinlogs.md) |
| [Successful AWS Console Login from IP Address Observed Conducting Password Spray](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuccessfulAWSConsoleLoginfromIPAddressObservedConductingPasswordSpray.yaml) | Medium | InitialAccess, CredentialAccess | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Suspicious AWS console logins by credential access alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/SuspiciousAWSConsolLoginByCredentialAceessAlerts.yaml) | Medium | InitialAccess, CredentialAccess | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>*Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Unauthorized user access across AWS and Azure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/Unauthorized_user_access_across_AWS_and_Azure.yaml) | Medium | CredentialAccess, Exfiltration, Discovery | [`AWSGuardDuty`](../tables/awsguardduty.md) |
| [User impersonation by Identity Protection alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Multi%20Cloud%20Attack%20Coverage%20Essentials%20-%20Resource%20Abuse/Analytic%20Rules/UserImpersonateByAAID.yaml) | Medium | PrivilegeEscalation | [`AWSCloudTrail`](../tables/awscloudtrail.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 07-06-2024                     | Analytical Rule description updated                                |
| 3.0.2       | 08-04-2024                     | Added Account and FullName in entity mapping                       |
| 3.0.1       | 23-02-2024                     | Tagged for dependent solutions for deployment                      |
| 3.0.0       | 22-11-2023                     | Initial Release                                                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
