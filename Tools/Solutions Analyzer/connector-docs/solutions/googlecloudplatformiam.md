# GoogleCloudPlatformIAM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Google Cloud Platform IAM (via Codeless Connector Framework)](../connectors/gcpiamccpdefinition.md)
- [[DEPRECATED] Google Cloud Platform IAM](../connectors/gcpiamdataconnector.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPIAM`](../tables/gcpiam.md) | [Google Cloud Platform IAM (via Codeless Connector Framework)](../connectors/gcpiamccpdefinition.md) | - |
| [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) | [[DEPRECATED] Google Cloud Platform IAM](../connectors/gcpiamdataconnector.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **25 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Playbooks | 3 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [GCP IAM - Disable Data Access Logging](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMDisableDataAccessLogging.yaml) | Medium | DefenseEvasion | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Empty user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMEmptyUA.yaml) | Medium | DefenseEvasion | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - High privileged role added to service account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMHighPrivilegedRoleAdded.yaml) | High | PrivilegeEscalation | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - New Authentication Token for Service Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMNewAuthenticationToken.yaml) | Medium | LateralMovement | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - New Service Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMNewServiceAccount.yaml) | Low | Persistence | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - New Service Account Key](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMNewServiceAccountKey.yaml) | Low | LateralMovement | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Privileges Enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMPrivilegesEnumeration.yaml) | Low | Discovery | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Publicly exposed storage bucket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMPublicBucket.yaml) | Medium | Discovery | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Service Account Enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMServiceAccountEnumeration.yaml) | Low | Discovery | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Service Account Keys Enumeration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Analytic%20Rules/GCPIAMServiceAccountKeysEnumeration.yaml) | Low | Discovery | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [GCP IAM - Changed roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMChangedRoles.yaml) | PrivilegeEscalation | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Deleted service accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMDeletedServiceAccounts.yaml) | Impact | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Disabled service accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMDisabledServiceAccounts.yaml) | Impact | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - New custom roles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMNewCustomRoles.yaml) | PrivilegeEscalation | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - New service account keys](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMNewServiceAccountsKeys.yaml) | LateralMovement | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - New service accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMNewServiceAccounts.yaml) | Persistence | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Rare IAM actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMRareActionUser.yaml) | InitialAccess | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Rare user agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMRareUA.yaml) | DefenseEvasion | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Top service accounts by failed actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMTopServiceAccountsFailedActions.yaml) | Discovery | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |
| [GCP IAM - Top source IP addresses with failed actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Hunting%20Queries/GCPIAMTopSrcIpAddrFailedActions.yaml) | Discovery | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [GCP_IAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Workbooks/GCP_IAM.json) | [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GCP-DisableServiceAccountFromTeams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Playbooks/GCP-DisableServiceAccountFromTeams/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [GCP-DisableServiceAccountKey](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Playbooks/GCP-DisableServiceAccountKey/azuredeploy.json) | Once a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [GCP-EnrichServiseAccountInfo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Playbooks/GCP-EnrichServiseAccountInfo/azuredeploy.json) | Once a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GCP_IAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformIAM/Parsers/GCP_IAM.yaml) | - | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.7      | 28-08-2025                    | Improved type handling in the parser query by explicitly converting certain fields to bool and datetime.|
| 3.0.6      | 31-07-2025                    | Removed deprecated **Data Connector** |
| 3.0.5      | 27-06-2025                    | GoogleCloudPlatformIAM **CCF Data Connector** moving to GA |
| 3.0.4      | 13-06-2025                    | Updated Standard Table configuration in **CCF Data Connector**.   |
| 3.0.3      | 28-05-2025                    | Implementation of Standard Table functionality to **CCF Data Connector**.    |
| 3.0.2      | 18-02-2025                    | Migrated the **Function app** connector to CCP **Data Connctor** and Updated **Parser**.   |
| 3.0.1      | 10-09-2024                    | Repackaged solution to add existing **Parser**.                                            |
| 3.0.0      | 04-09-2024                    | Updated the python runtime version to 3.11.                                                |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
