# Authomize

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Authomize |
| **Support Tier** | Partner |
| **Support Link** | [https://support.authomize.com](https://support.authomize.com) |
| **Categories** | domains,verticals |
| **First Published** | 2023-06-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Authomize Data Connector](../connectors/authomize.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) | [Authomize Data Connector](../connectors/authomize.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **28 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 21 |
| Hunting Queries | 6 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [AWS role with admin privileges](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/AWS_role_with_admin_privileges.yaml) | High | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [AWS role with shadow admin privileges](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/AWS_role_with_shadow_admin_privileges.yaml) | High | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Access to AWS without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Access_to_AWS_without_MFA.yaml) | Medium | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Admin SaaS account detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Admin_SaaS_account_detected.yaml) | Low | InitialAccess, PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Admin password not updated in 30 days](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Admin_password_wasnt_updated.yaml) | Medium | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Detect AWS IAM Users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Detect_AWS_IAM_Users.yaml) | High | PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Empty group with entitlements](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Empty_group_with_entitlements.yaml) | Informational | PrivilegeEscalation, Persistence | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [IaaS admin detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/IaaS_admin_detected.yaml) | Medium | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [IaaS policy not attached to any identity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/IaaS_policy_not_attached_to_any_identity.yaml) | Informational | PrivilegeEscalation, Persistence | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [IaaS shadow admin detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/IaaS_shadow_admin_detected.yaml) | High | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Lateral Movement Risk - Role Chain Length](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Chain_of_3_or_more_roles.yaml) | Informational | PrivilegeEscalation, Persistence | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [New direct access policy was granted against organizational policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/New_direct_access_policy_was_granted.yaml) | Low | InitialAccess, PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [New service account gained access to IaaS resource](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/New_service_account_gained_access_to_IaaS_resource.yaml) | Informational | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Password Exfiltration over SCIM application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Password_Exfiltration_over_SCIM.yaml) | High | CredentialAccess, InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Privileged Machines Exposed to the Internet](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Privileged_Machines_Exposed_to_the_Internet.yaml) | High | Discovery, Impact | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Refactor AWS policy based on activities in the last 60 days](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Refactor_AWS_policy_based_on_activities.yaml) | High | PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Stale AWS policy attachment to identity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Stale_AWS_policy_attachment_to_identity.yaml) | Low | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Stale IAAS policy attachment to role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Stale_IAAS_policy_attachment_to_role.yaml) | Informational | PrivilegeEscalation, Persistence | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Unused IaaS Policy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/Unused_IaaS_Policy.yaml) | High | InitialAccess, PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [User assigned to a default admin role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/User_assigned_to_a_default_admin_role.yaml) | High | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [User without MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Analytic%20Rules/User_without_MFA.yaml) | Medium | InitialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Admin SaaS account detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Hunting%20Queries/Admin_SaaS_account_detected.yaml) | PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [IaaS admin detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Hunting%20Queries/IaaS_admin_detected.yaml) | PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [IaaS shadow admin detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Hunting%20Queries/IaaS_shadow_admin_detected.yaml) | PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Password Exfiltration over SCIM application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Hunting%20Queries/Password_Exfiltration_over_SCIM_application.yaml) | CredentialAccess | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [Privileged Machines Exposed to the Internet](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Hunting%20Queries/Privileged_Machines_Exposed_to_the_Internet.yaml) | Discovery | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |
| [ateral Movement Risk - Role Chain Length](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Hunting%20Queries/Chain_of_3_or_more_roles.yaml) | PrivilegeEscalation | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Authomize](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Workbooks/Authomize.json) | [`Authomize_v2_CL`](../tables/authomize-v2-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       |  12-12-2023                    | Added Entity Mapping to **Analytic rules**  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
