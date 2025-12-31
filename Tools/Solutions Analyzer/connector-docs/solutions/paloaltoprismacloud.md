# PaloAltoPrismaCloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-04-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Palo Alto Prisma Cloud CSPM](../connectors/paloaltoprismacloud.md)
- [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](../connectors/paloaltoprismacloudcspmccpdefinition.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md) | [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](../connectors/paloaltoprismacloudcspmccpdefinition.md) | Analytics, Hunting, Workbooks |
| [`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md) | [[DEPRECATED] Palo Alto Prisma Cloud CSPM](../connectors/paloaltoprismacloud.md) | Analytics, Hunting, Workbooks |
| [`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md) | [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](../connectors/paloaltoprismacloudcspmccpdefinition.md) | Analytics, Hunting, Workbooks |
| [`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) | [[DEPRECATED] Palo Alto Prisma Cloud CSPM](../connectors/paloaltoprismacloud.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **24 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Hunting Queries | 9 |
| Playbooks | 2 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Palo Alto Prisma Cloud - Access keys are not rotated for 90 days](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudAclAccessKeysNotRotated.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Anomalous access key usage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudAnomalousApiKeyActivity.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - High risk score alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudHighRiskScoreAlert.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - High severity alert opened for several days](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudHighSeverityAlertOpenedForXDays.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - IAM Group with Administrator Access Permissions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudIamAdminGroup.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Inactive user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudInactiveUser.yaml) | Low | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Maximum risk score alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudMaxRiskScoreAlert.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Multiple failed logins for user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudMultipleFailedLoginsUser.yaml) | Medium | CredentialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Network ACL allow all outbound traffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudAclAllowAllOut.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Network ACL allow ingress traffic to server administration ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudAclAllowInToAdminPort.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Network ACLs Inbound rule to allow All Traffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Analytic%20Rules/PaloAltoPrismaCloudAclInAllowAll.yaml) | Medium | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Palo Alto Prisma Cloud - Access keys used](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudAccessKeysUsed.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - High risk score opened alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudHighRiskScoreOpenedAlerts.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - High severity alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudHighSeverityAlerts.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudNewUsers.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Opened alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudOpenedAlerts.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Top recources with alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudTopResources.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Top sources of failed logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudFailedLoginsSources.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Top users by failed logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudFailedLoginsUsers.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |
| [Palo Alto Prisma Cloud - Updated resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Hunting%20Queries/PaloAltoPrismaCloudUpdatedResources.yaml) | InitialAccess | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PaloAltoPrismaCloudOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Workbooks/PaloAltoPrismaCloudOverview.json) | [`PaloAltoPrismaCloudAlertV2_CL`](../tables/paloaltoprismacloudalertv2-cl.md)<br>[`PaloAltoPrismaCloudAlert_CL`](../tables/paloaltoprismacloudalert-cl.md)<br>[`PaloAltoPrismaCloudAuditV2_CL`](../tables/paloaltoprismacloudauditv2-cl.md)<br>[`PaloAltoPrismaCloudAudit_CL`](../tables/paloaltoprismacloudaudit-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Fetch Security Posture from Prisma Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Playbooks/PrismaCloudCSPMPlaybooks/PrismaCloudCSPM-Enrichment/azuredeploy.json) | This playbook provides/updates the compliance security posture details of asset in comments section ... | - |
| [Remediate assets on prisma cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Playbooks/PrismaCloudCSPMPlaybooks/PrismaCloudCSPM-Remediation/azuredeploy.json) | This playbook provides/updates the compliance security posture details of asset in comments section ... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PaloAltoPrismaCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Parsers/PaloAltoPrismaCloud.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.4       | 27-10-2025                     | Add missing "detailed" flag to CCF **Data Connector** polling config |
| 3.0.3       | 10-10-2025                     | CCF **Data Connector** Moving to GA.		|
| 3.0.2       | 06-08-2025                     | Change **authentication type** from Basic to JWT Token.		|
| 3.0.1       | 17-07-2025                     | 1 **Analytic Rule** updated with improved rule logic.<br/> Added new **CCF Connector** - *Palo Alto Prisma Cloud CSPM.*   |  
| 3.0.0       | 18-08-2023                     | Manual deployment instructions updated for **Data Connector**		|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
