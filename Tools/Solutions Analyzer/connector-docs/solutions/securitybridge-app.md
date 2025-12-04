# SecurityBridge App

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SecurityBridge |
| **Support Tier** | Partner |
| **Support Link** | [https://securitybridge.com/contact/](https://securitybridge.com/contact/) |
| **Categories** | domains,verticals |
| **First Published** | 2022-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [SecurityBridge Solution for SAP](../connectors/securitybridge.md)

**Publisher:** SecurityBridge Group GmbH

### [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md)

**Publisher:** SecurityBridge

SecurityBridge is the first and only holistic, natively integrated security platform, addressing all aspects needed to protect organizations running SAP from internal and external threats against their core business applications. The SecurityBridge platform is an SAP-certified add-on, used by organizations around the globe, and addresses the clients’ need for advanced cybersecurity, real-time monitoring, compliance, code security, and patching to protect against internal and external threats.This Microsoft Sentinel Solution allows you to integrate SecurityBridge Threat Detection events from all your on-premise and cloud based SAP instances into your security monitoring.Use this Microsoft Sentinel Solution to receive normalized and speaking security events, pre-built dashboards and out-of-the-box templates for your SAP security monitoring.

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityBridgeLogs_CL` |
| **Connector Definition Files** | [Connector_SecurityBridge.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Data%20Connectors/Connector_SecurityBridge.json) |

[→ View full connector details](../connectors/securitybridgesap.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ABAPAuditLog` | [SecurityBridge Solution for SAP](../connectors/securitybridge.md) |
| `SecurityBridgeLogs_CL` | [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md) |

[← Back to Solutions Index](../solutions-index.md)
