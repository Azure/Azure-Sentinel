# Cisco SD-WAN

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cisco Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://globalcontacts.cloudapps.cisco.com/contacts/contactDetails/en_US/c1o1-c2o2-c3o8](https://globalcontacts.cloudapps.cisco.com/contacts/contactDetails/en_US/c1o1-c2o2-c3o8) |
| **Categories** | domains |
| **First Published** | 2023-06-01 |
| **Last Updated** | 2024-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cisco Software Defined WAN](../connectors/ciscosdwan.md)

## Tables Reference

This solution uses **6 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CiscoSDWANNetflow_CL`](../tables/ciscosdwannetflow-cl.md) | [Cisco Software Defined WAN](../connectors/ciscosdwan.md) | Workbooks |
| [`NetflowFlowFieldSGT`](../tables/netflowflowfieldsgt.md) | - | Workbooks |
| [`NetflowFwPolicy`](../tables/netflowfwpolicy.md) | - | Workbooks |
| [`Syslog`](../tables/syslog.md) | [Cisco Software Defined WAN](../connectors/ciscosdwan.md) | Analytics, Workbooks |
| [`external_data`](../tables/external-data.md) | - | Workbooks |
| [`todynamic`](../tables/todynamic.md) | - | Workbooks |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Parsers | 4 |
| Playbooks | 3 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cisco SDWAN - IPS Event Threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Analytic%20Rules/CiscoSDWANSentinelIPSEventThreshold.yaml) | High | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco SDWAN - Intrusion Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Analytic%20Rules/CiscoSDWANSentinelIntrusionEvents.yaml) | High | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco SDWAN - Maleware Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Analytic%20Rules/CiscoSDWANSentinelMalwareEvents.yaml) | High | ResourceDevelopment | [`Syslog`](../tables/syslog.md) |
| [Cisco SDWAN - Monitor Critical IPs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Analytic%20Rules/CiscoSDWANSentinelMonitorCriticalIP.yaml) | High | CommandAndControl | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CiscoSDWAN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Workbooks/CiscoSDWAN.json) | [`CiscoSDWANNetflow_CL`](../tables/ciscosdwannetflow-cl.md)<br>[`NetflowFlowFieldSGT`](../tables/netflowflowfieldsgt.md)<br>[`NetflowFwPolicy`](../tables/netflowfwpolicy.md)<br>[`Syslog`](../tables/syslog.md)<br>[`external_data`](../tables/external-data.md)<br>[`todynamic`](../tables/todynamic.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoSDWANIntrusionLogicAPP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Playbooks/CiscoSDWANIntrusionLogicAPP/azuredeploy.json) | This playbook provides an end-to-end example of adding a comment in the generated incident. | - |
| [CiscoSDWANLogicAPP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Playbooks/CiscoSDWANLogicAPP/azuredeploy.json) | This playbook provides an end-to-end example of sending an email, posting a message to the Microsoft... | - |
| [CiscoSDWANReport](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Playbooks/CiscoSDWANReport/azuredeploy.json) | This playbook provides an end-to-end example of sending an email for suspicious activity found in th... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoSDWANNetflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Parsers/CiscoSDWANNetflow.yaml) | - | - |
| [CiscoSyslogFW6LogSummary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Parsers/CiscoSyslogFW6LogSummary.yaml) | - | - |
| [CiscoSyslogUTD](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Parsers/CiscoSyslogUTD.yaml) | - | - |
| [MapNetflowUsername](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20SD-WAN/Parsers/MapNetflowUsername.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
