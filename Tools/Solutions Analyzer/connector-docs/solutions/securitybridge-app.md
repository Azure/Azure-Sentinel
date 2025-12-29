# SecurityBridge App

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

SecurityBridge enhances SAP security by integrating seamlessly with Microsoft Sentinel, enabling real-time monitoring and threat detection across SAP environments. This integration allows Security Operations Centers (SOCs) to consolidate SAP security events with other organizational data, providing a unified view of the threat landscape . Leveraging AI-powered analytics and Microsoft’s Security Copilot, SecurityBridge identifies sophisticated attack patterns and vulnerabilities within SAP applications, including ABAP code scanning and configuration assessments . The solution supports scalable deployments across complex SAP landscapes, whether on-premises, in the cloud, or hybrid environments . By bridging the gap between IT and SAP security teams, SecurityBridge empowers organizations to proactively detect, investigate, and respond to threats, enhancing overall security posture.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ABAPAuditLog` |
| **Connector Definition Files** | [SecurityBridge_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Data%20Connectors/SecurityBridge_PUSH_CCP/SecurityBridge_connectorDefinition.json) |

[→ View full connector details](../connectors/securitybridge.md)

### [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md)

**Publisher:** SecurityBridge

SecurityBridge is the first and only holistic, natively integrated security platform, addressing all aspects needed to protect organizations running SAP from internal and external threats against their core business applications. The SecurityBridge platform is an SAP-certified add-on, used by organizations around the globe, and addresses the clients’ need for advanced cybersecurity, real-time monitoring, compliance, code security, and patching to protect against internal and external threats.This Microsoft Sentinel Solution allows you to integrate SecurityBridge Threat Detection events from all your on-premise and cloud based SAP instances into your security monitoring.Use this Microsoft Sentinel Solution to receive normalized and speaking security events, pre-built dashboards and out-of-the-box templates for your SAP security monitoring.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityBridgeLogs_CL` |
| **Connector Definition Files** | [Connector_SecurityBridge.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Data%20Connectors/Connector_SecurityBridge.json) |

[→ View full connector details](../connectors/securitybridgesap.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ABAPAuditLog` | [SecurityBridge Solution for SAP](../connectors/securitybridge.md) |
| `SecurityBridgeLogs_CL` | [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                      |
|-------------|--------------------------------|-----------------------------------------|
| 3.2.1       | 22-09-2025                     | adding SecurityBridge_CL table          |
| 3.2.0       | 15-07-2025                     | adding push API data connector          |
| 3.1.0       | 12-02-2025                     | Adjusted contact and support            |
| 3.0.1       | 07-01-2025                     | Removed Deprecated **Data connector**   |
| 3.0.0       | 08-08-2024                     | Deprecating data connectors             |

[← Back to Solutions Index](../solutions-index.md)
