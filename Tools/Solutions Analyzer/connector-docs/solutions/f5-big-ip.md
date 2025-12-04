# F5 BIG-IP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | F5 Networks |
| **Support Tier** | Partner |
| **Support Link** | [https://support.f5.com/csp/home](https://support.f5.com/csp/home) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [F5 BIG-IP](../connectors/f5bigip.md)

**Publisher:** F5 Networks

The F5 firewall connector allows you to easily connect your F5 logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `F5Telemetry_ASM_CL` |
| | `F5Telemetry_LTM_CL` |
| | `F5Telemetry_system_CL` |
| **Connector Definition Files** | [F5BigIp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/F5%20BIG-IP/Data%20Connectors/F5BigIp.json) |

[→ View full connector details](../connectors/f5bigip.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `F5Telemetry_ASM_CL` | [F5 BIG-IP](../connectors/f5bigip.md) |
| `F5Telemetry_LTM_CL` | [F5 BIG-IP](../connectors/f5bigip.md) |
| `F5Telemetry_system_CL` | [F5 BIG-IP](../connectors/f5bigip.md) |

[← Back to Solutions Index](../solutions-index.md)
