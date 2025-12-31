# Palo Alto Cortex XDR CCP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-12-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20XDR%20CCP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Cortex%20XDR%20CCP) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PaloAltoCortexXDR_Alerts_CL`](../tables/paloaltocortexxdr-alerts-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Audit_Agent_CL`](../tables/paloaltocortexxdr-audit-agent-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Audit_Management_CL`](../tables/paloaltocortexxdr-audit-management-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Endpoints_CL`](../tables/paloaltocortexxdr-endpoints-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Incidents_CL`](../tables/paloaltocortexxdr-incidents-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.4       | 14-10-2025                     | Updating CCF Polling file to implement parameters                           |
| 3.0.3       | 09-04-2025                     | Updating CCF connector parameters                                        |
| 3.0.2       | 10-02-2025                     | Advancing CCF **Data Connector** from Public preview to Global Availability.|
| 3.0.1       | 22-01-2025                     | Added Preview tag to **Data Connector**                                                 |
| 3.0.0       | 17-12-2024                     | Initial Solution Release                                                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
