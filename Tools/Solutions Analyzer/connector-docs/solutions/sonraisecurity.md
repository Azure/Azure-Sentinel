# SonraiSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Sonrai |
| **Support Tier** | Partner |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Sonrai Data Connector](../connectors/sonraidataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) | [Sonrai Data Connector](../connectors/sonraidataconnector.md) | Analytics, Workbooks |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 9 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [New Sonrai Ticket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiNewTicket.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Assigned](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketAssigned.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Closed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketClosed.yaml) | Low | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Escalation Executed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketCommentAdded.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Escalation Executed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketEscalationExecuted.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Reopened](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketReopened.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Risk Accepted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketRiskAccepted.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Snoozed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketSnoozed.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |
| [Sonrai Ticket Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Analytic%20Rules/SonraiTicketUpdated.yaml) | Medium | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Sonrai](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SonraiSecurity/Workbooks/Sonrai.json) | [`Sonrai_Tickets_CL`](../tables/sonrai-tickets-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 04-12-2023                     | Added entity mapping to **Analytic Rules**                               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
