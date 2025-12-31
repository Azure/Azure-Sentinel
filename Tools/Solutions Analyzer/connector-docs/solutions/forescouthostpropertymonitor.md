# ForescoutHostPropertyMonitor

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Forescout Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forescout.com/support](https://www.forescout.com/support) |
| **Categories** | domains |
| **First Published** | 2022-06-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ForescoutComplianceStatus_CL`](../tables/forescoutcompliancestatus-cl.md) | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) | Workbooks |
| [`ForescoutHostProperties_CL`](../tables/forescouthostproperties-cl.md) | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) | Analytics, Workbooks |
| [`ForescoutPolicyStatus_CL`](../tables/forescoutpolicystatus-cl.md) | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) | Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Forescout-DNS_Sniff_Event_Monitor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor/Analytic%20Rules/ForeScout-DNSSniffEventMonitor.yaml) | Medium | - | [`ForescoutHostProperties_CL`](../tables/forescouthostproperties-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ForescoutHostPropertyMonitorWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor/Workbooks/ForescoutHostPropertyMonitorWorkbook.json) | [`ForescoutComplianceStatus_CL`](../tables/forescoutcompliancestatus-cl.md)<br>[`ForescoutHostProperties_CL`](../tables/forescouthostproperties-cl.md)<br>[`ForescoutPolicyStatus_CL`](../tables/forescoutpolicystatus-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Forescout-DNS_Sniff_Event_Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor/Playbooks/Forescout-DNSSniffEventPlaybook.json) | This playbook will update incident with action to perform on endpoint | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 18-02-2025                     | Added new **Workbook** Forescout Host Property Monitor Workbook.<br/> Changes to **Analytic Rules** and **Playbook** corresponding to Customer table changes replaced HTTP Data Collector API with Log Ingestion API.|
| 2.0.1       | 26-05-2022                     | Updated Support details from Microsoft to Forescout.                                                 |
| 2.0.0       | 05-11-2023                     | Initial Solution Release.                                                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
