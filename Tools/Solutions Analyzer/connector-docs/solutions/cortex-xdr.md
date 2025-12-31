# Cortex XDR

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md)
- [Cortex XDR - Incidents](../connectors/cortexxdrincidents.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PaloAltoCortexXDR_Alerts_CL`](../tables/paloaltocortexxdr-alerts-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Audit_Agent_CL`](../tables/paloaltocortexxdr-audit-agent-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Audit_Management_CL`](../tables/paloaltocortexxdr-audit-management-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Endpoints_CL`](../tables/paloaltocortexxdr-endpoints-cl.md) | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | - |
| [`PaloAltoCortexXDR_Incidents_CL`](../tables/paloaltocortexxdr-incidents-cl.md) | [Cortex XDR - Incidents](../connectors/cortexxdrincidents.md), [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cortex XDR Incident - High](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Analytic%20Rules/CortexXDR_High.yaml) | High | - | [`PaloAltoCortexXDR_Incidents_CL`](../tables/paloaltocortexxdr-incidents-cl.md) |
| [Cortex XDR Incident - Low](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Analytic%20Rules/CortexXDR_Low.yaml) | Low | - | [`PaloAltoCortexXDR_Incidents_CL`](../tables/paloaltocortexxdr-incidents-cl.md) |
| [Cortex XDR Incident - Medium](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Analytic%20Rules/CortexXDR_Medium.yaml) | Medium | - | [`PaloAltoCortexXDR_Incidents_CL`](../tables/paloaltocortexxdr-incidents-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PaloAltoCortexXDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Parsers/PaloAltoCortexXDR.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 28-07-2023                     | Initial Solution Release                                                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
