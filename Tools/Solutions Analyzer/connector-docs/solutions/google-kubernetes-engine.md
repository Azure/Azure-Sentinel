# Google Kubernetes Engine

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GKEAPIServer`](../tables/gkeapiserver.md) | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) | - |
| [`GKEApplication`](../tables/gkeapplication.md) | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) | - |
| [`GKEAudit`](../tables/gkeaudit.md) | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) | - |
| [`GKEControllerManager`](../tables/gkecontrollermanager.md) | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) | - |
| [`GKEHPADecision`](../tables/gkehpadecision.md) | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) | - |
| [`GKEScheduler`](../tables/gkescheduler.md) | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 06-10-2025                     | Google Kubernetes Engine CCF **Data Connector** Moving to GA.  |
| 3.0.0       | 08-04-2025                     | Initial Solution Release.<br/>New CCF **Data Connector** 'Google Kubernetes Engine'.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
