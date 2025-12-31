# SailPointIdentityNow

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SailPoint |
| **Support Tier** | Partner |
| **Categories** | domains |
| **First Published** | 2021-10-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SailPoint IdentityNow](../connectors/sailpointidentitynow.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SailPointIDN_Events_CL`](../tables/sailpointidn-events-cl.md) | [SailPoint IdentityNow](../connectors/sailpointidentitynow.md) | Analytics |
| [`SailPointIDN_Triggers_CL`](../tables/sailpointidn-triggers-cl.md) | [SailPoint IdentityNow](../connectors/sailpointidentitynow.md) | Analytics |
| [`declare`](../tables/declare.md) | - | Analytics |

## Content Items

This solution includes **7 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 6 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SailPointIdentityNowAlertForTriggers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Analytic%20Rules/SailPointIdentityNowAlertsForTriggers.yaml) | Informational | InitialAccess, Collection | [`SailPointIDN_Triggers_CL`](../tables/sailpointidn-triggers-cl.md)<br>[`declare`](../tables/declare.md) |
| [SailPointIdentityNowEventType](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Analytic%20Rules/SailPointIdentityNowEventType.yaml) | High | InitialAccess | [`SailPointIDN_Events_CL`](../tables/sailpointidn-events-cl.md)<br>[`declare`](../tables/declare.md) |
| [SailPointIdentityNowEventTypeTechnicalName](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Analytic%20Rules/SailPointIdentityNowEventTypeTechnicalName.yaml) | High | InitialAccess | [`SailPointIDN_Events_CL`](../tables/sailpointidn-events-cl.md)<br>[`declare`](../tables/declare.md) |
| [SailPointIdentityNowFailedEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Analytic%20Rules/SailPointIdentityNowFailedEvents.yaml) | High | InitialAccess | [`SailPointIDN_Events_CL`](../tables/sailpointidn-events-cl.md)<br>[`declare`](../tables/declare.md) |
| [SailPointIdentityNowFailedEventsBasedOnTime](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Analytic%20Rules/SailPointIdentityNowFailedEventsBasedOnTime.yaml) | High | InitialAccess | [`SailPointIDN_Events_CL`](../tables/sailpointidn-events-cl.md)<br>[`declare`](../tables/declare.md) |
| [SailPointIdentityNowUserWithFailedEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Analytic%20Rules/SailPointIdentityNowUserWithFailedEvents.yaml) | High | InitialAccess | [`SailPointIDN_Events_CL`](../tables/sailpointidn-events-cl.md)<br>[`declare`](../tables/declare.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SailPointIdentityNow-swagger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Playbooks/Custom%20Connector/SailPointIdentityNow-swagger.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 28-08-2024                     | **Data Connector** instruction updated      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
