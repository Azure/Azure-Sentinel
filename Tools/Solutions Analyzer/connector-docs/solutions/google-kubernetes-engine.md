# Google Kubernetes Engine

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Google Kubernetes Engine (via Codeless Connector Framework)

**Publisher:** Microsoft

The Google Kubernetes Engine (GKE) Logs enable you to capture cluster activity, workload behavior, and security events, allowing you to monitor Kubernetes workloads, analyze performance, and detect potential threats across GKE clusters.

**Tables Ingested:**

- `GKEAPIServer`
- `GKEApplication`
- `GKEAudit`
- `GKEControllerManager`
- `GKEHPADecision`
- `GKEScheduler`

**Connector Definition Files:**

- [GoogleKubernetesEngineLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine/Data%20Connectors/GoogleKubernetesEngineLogs_ccp/GoogleKubernetesEngineLogs_ConnectorDefinition.json)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GKEAPIServer` | 1 connector(s) |
| `GKEApplication` | 1 connector(s) |
| `GKEAudit` | 1 connector(s) |
| `GKEControllerManager` | 1 connector(s) |
| `GKEHPADecision` | 1 connector(s) |
| `GKEScheduler` | 1 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n