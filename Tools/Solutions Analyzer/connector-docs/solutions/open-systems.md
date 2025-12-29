# Open Systems

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Open Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://www.open-systems.com/support](https://www.open-systems.com/support) |
| **Categories** | domains |
| **First Published** | 2025-05-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Open%20Systems](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Open%20Systems) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Open Systems Data Connector](../connectors/opensystems.md)

**Publisher:** Open Systems

The Open Systems Logs API Microsoft Sentinel Connector provides the capability to ingest Open Systems logs into Microsoft Sentinel using Open Systems Logs API.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `OpenSystemsAuthenticationLogs_CL` |
| | `OpenSystemsFirewallLogs_CL` |
| | `OpenSystemsImAuthentication` |
| | `OpenSystemsImNetworkSessionFirewall` |
| | `OpenSystemsImNetworkSessionProxy` |
| | `OpenSystemsImZTNA` |
| | `OpenSystemsProxyLogs_CL` |
| | `OpenSystemsZtnaLogs_CL` |
| **Connector Definition Files** | [OpenSystems.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Open%20Systems/Data%20Connectors/OpenSystems.json) |

[→ View full connector details](../connectors/opensystems.md)

## Tables Reference

This solution ingests data into **8 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OpenSystemsAuthenticationLogs_CL` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsFirewallLogs_CL` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsImAuthentication` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsImNetworkSessionFirewall` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsImNetworkSessionProxy` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsImZTNA` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsProxyLogs_CL` | [Open Systems Data Connector](../connectors/opensystems.md) |
| `OpenSystemsZtnaLogs_CL` | [Open Systems Data Connector](../connectors/opensystems.md) |

[← Back to Solutions Index](../solutions-index.md)
