# CyberArkAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CyberArk Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support-contact/](https://www.cyberark.com/services-support/technical-support-contact/) |
| **Categories** | domains |
| **First Published** | 2024-03-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CyberArkAudit](../connectors/cyberarkaudit.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyberArkAudit`](../tables/cyberarkaudit.md) | [CyberArkAudit](../connectors/cyberarkaudit.md) | - |
| [`CyberArk_AuditEvents_CL`](../tables/cyberark-auditevents-cl.md) | [CyberArkAudit](../connectors/cyberarkaudit.md) | Analytics |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CyberArk - High-Risk Actions Outside Business Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit/Analytic%20Rules/CyberArkAuditHighRiskActions.yaml) | High | DefenseEvasion | [`CyberArk_AuditEvents_CL`](../tables/cyberark-auditevents-cl.md) |
| [CyberArk - Multiple Failed Actions Followed by Success (15m)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit/Analytic%20Rules/CyberArkAuditMultiFailedAndSuccess.yaml) | Medium | CredentialAccess | [`CyberArk_AuditEvents_CL`](../tables/cyberark-auditevents-cl.md) |
| [CyberArk - Sensitive Safe/Permission/Entitlement Changes (with customData)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkAudit/Analytic%20Rules/CyberArkAuditSensitiveChanges.yaml) | Low | PrivilegeEscalation | [`CyberArk_AuditEvents_CL`](../tables/cyberark-auditevents-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                    |
|-------------|--------------------------------|-------------------------------------------------------|
| 3.0.2       | 16-10-2025                     | Add Analytics Rules.                                  |
| 3.0.1       | 29-04-2024                     | Configuration procedure update.      	              	 |  
| 3.0.0       | 03-04-2024                     | Initial Solution Release.        	              	     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
