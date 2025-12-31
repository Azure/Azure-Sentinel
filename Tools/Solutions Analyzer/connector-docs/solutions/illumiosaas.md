# IllumioSaaS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Illumio |
| **Support Tier** | Partner |
| **Support Link** | [https://www.illumio.com/support/support](https://www.illumio.com/support/support) |
| **Categories** | domains |
| **First Published** | 2024-05-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Illumio SaaS](../connectors/illumiosaasdataconnector.md)
- [Illumio Saas](../connectors/illumiosaasccfdefinition.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`IllumioFlowEventsV2_CL`](../tables/illumiofloweventsv2-cl.md) | [Illumio Saas](../connectors/illumiosaasccfdefinition.md) | - |
| [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) | [Illumio SaaS](../connectors/illumiosaasdataconnector.md) | Analytics, Workbooks |
| [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md) | [Illumio SaaS](../connectors/illumiosaasdataconnector.md) | Workbooks |
| [`Illumio_Workloads_Summarized_API_CL`](../tables/illumio-workloads-summarized-api-cl.md) | - | Workbooks |
| [`Syslog`](../tables/syslog.md) | - | Workbooks |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 6 |
| Workbooks | 4 |
| Playbooks | 4 |
| Parsers | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Illumio Enforcement Change Analytic Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Analytic%20Rules/Illumio_VEN_Enforcement_Change_Detection_Query.yaml) | Medium | DefenseEvasion | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |
| [Illumio Firewall Tampering Analytic Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Analytic%20Rules/Illumio_VEN_Firewall_Tampering_Detection_Query.yaml) | Medium | DefenseEvasion | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |
| [Illumio VEN Clone Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Analytic%20Rules/Illumio_VEN_Clone_Detection_Query.yaml) | High | DefenseEvasion | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |
| [Illumio VEN Deactivated Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Analytic%20Rules/Illumio_VEN_Deactivated_Query.yaml) | High | DefenseEvasion | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |
| [Illumio VEN Offline Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Analytic%20Rules/Illumio_VEN_Offline_Detection_Query.yaml) | High | DefenseEvasion | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |
| [Illumio VEN Suspend Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Analytic%20Rules/Illumio_VEN_Suspend_Query.yaml) | High | DefenseEvasion | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [IllumioAuditableEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Workbooks/IllumioAuditableEvents.json) | [`Illumio_Auditable_Events_CL`](../tables/illumio-auditable-events-cl.md) |
| [IllumioFlowData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Workbooks/IllumioFlowData.json) | [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`Syslog`](../tables/syslog.md) |
| [IllumioOnPremHealth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Workbooks/IllumioOnPremHealth.json) | [`Syslog`](../tables/syslog.md) |
| [IllumioWorkloadsStats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Workbooks/IllumioWorkloadsStats.json) | [`Illumio_Workloads_Summarized_API_CL`](../tables/illumio-workloads-summarized-api-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Illumio Containment Switch Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Playbooks/Illumio-Port-Blocking-Switch/azuredeploy.json) | This playbook leverages Illumio workloads API to contain and isolate a workload based on user inputs... | - |
| [Illumio Get Ven Details Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Playbooks/Illumio-Get-Ven-Details/azuredeploy.json) | This playbook leverages Illumio workloads API to enrich IP, Hostname and Labels, found in Microsoft ... | - |
| [Illumio Workload Quarantine Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Playbooks/Illumio-Quarantine-Workload/azuredeploy.json) | This playbook leverages Illumio workloads API to quarantine a workload based on user inputs. <img sr... | - |
| [IllumioSaaS_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Playbooks/CustomConnector/IllumioSaaS_FunctionAppConnector/azuredeploy.json) | - | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [IllumioSyslogAuditEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Parsers/IllumioSyslogAuditEvents.yaml) | - | - |
| [IllumioSyslogNetworkTrafficEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IllumioSaaS/Parsers/IllumioSyslogNetworkTrafficEvents.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     				 |
|-------------|--------------------------------|---------------------------------------------------------|
| 3.4.0       | 03-02-2025                     | Added 2 new **Parser**. <br/> Added new connectorid SyslogAma to **Analytic Rules**. <br/> Resolved **Playbook** deployment error.<br/> Made minor visualization changes to **Workbooks**.                   |
| 3.3.0       | 12-12-2024                     | Version fixed 3.2.3 to 3.3.0.                          |
| 3.2.2       | 24-10-2024                     | Bump up package to 3.2.2 version.                        |
| 3.2.0       | 01-10-2024                     | Added new **Analytic Rules**.                            |
| 3.1.0       | 04-08-2024                     | Solution packaged with Modified logo link.               |
| 3.0.0       | 13-05-2024                     | Initial Solution Release.         					     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
