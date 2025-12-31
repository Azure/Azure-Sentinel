# Morphisec

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Morphisec |
| **Support Tier** | Partner |
| **Support Link** | [https://support.morphisec.com/support/home](https://support.morphisec.com/support/home) |
| **Categories** | domains |
| **First Published** | 2022-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Morphisec API Data Connector (via Codeless Connector Framework)](../connectors/morphisecccf.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MorphisecAlerts_CL`](../tables/morphisecalerts-cl.md) | [Morphisec API Data Connector (via Codeless Connector Framework)](../connectors/morphisecccf.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Critical Severity Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec/Analytic%20Rules/MorphisecCriticalSeverityIncident.yaml) | High | Execution, DefenseEvasion | [`MorphisecAlerts_CL`](../tables/morphisecalerts-cl.md) |
| [Device Alert Surge](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec/Analytic%20Rules/MorphisecDeviceAlertSurge.yaml) | High | Execution, DefenseEvasion | [`MorphisecAlerts_CL`](../tables/morphisecalerts-cl.md) |
| [Process-Level Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec/Analytic%20Rules/MorphisecProcessLevelAnomaly.yaml) | Medium | Execution, DefenseEvasion | [`MorphisecAlerts_CL`](../tables/morphisecalerts-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Morphisec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec/Parsers/Morphisec.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                |
|-------------|--------------------------------|---------------------------------------------------|
| 3.1.0       | 10-09-2025                     | 	Adding CCF connector                             |
| 3.0.1       | 26-06-2024                     | 	Deprecating data connectors                      |
| 3.0.0       | 07-09-2023                     | 	Addition of new Morphisec AMA **Data Connector** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
