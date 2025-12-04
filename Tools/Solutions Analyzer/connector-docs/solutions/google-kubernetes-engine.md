# Google Kubernetes Engine

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md)

**Publisher:** Microsoft

The Google Kubernetes Engine (GKE) Logs enable you to capture cluster activity, workload behavior, and security events, allowing you to monitor Kubernetes workloads, analyze performance, and detect potential threats across GKE clusters.

| | |
|--------------------------|---|
| **Tables Ingested** | `GKEAPIServer` |
| | `GKEApplication` |
| | `GKEAudit` |
| | `GKEControllerManager` |
| | `GKEHPADecision` |
| | `GKEScheduler` |
| **Connector Definition Files** | [GoogleKubernetesEngineLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine/Data%20Connectors/GoogleKubernetesEngineLogs_ccp/GoogleKubernetesEngineLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gkeccpdefinition.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GKEAPIServer` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEApplication` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEAudit` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEControllerManager` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEHPADecision` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEScheduler` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
