# ALC-WebCTRL

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ALC-WebCTRL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ALC-WebCTRL) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Automated Logic WebCTRL ](../connectors/automatedlogicwebctrl.md)

**Publisher:** AutomatedLogic

You can stream the audit logs from the WebCTRL SQL server hosted on Windows machines connected to your Microsoft Sentinel. This connection enables you to view dashboards, create custom alerts and improve investigation. This gives insights into your Industrial Control Systems that are monitored or controlled by the WebCTRL BAS application.

| | |
|--------------------------|---|
| **Tables Ingested** | `Event` |
| **Connector Definition Files** | [Connector_WindowsEvents_WebCTRL.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ALC-WebCTRL/Data%20Connectors/Connector_WindowsEvents_WebCTRL.json) |

[→ View full connector details](../connectors/automatedlogicwebctrl.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Event` | [Automated Logic WebCTRL ](../connectors/automatedlogicwebctrl.md) |

[← Back to Solutions Index](../solutions-index.md)
