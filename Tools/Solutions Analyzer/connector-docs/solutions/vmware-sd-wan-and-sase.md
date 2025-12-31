# VMware SD-WAN and SASE

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | VMware by Broadcom |
| **Support Tier** | Partner |
| **Support Link** | [https://developer.vmware.com/](https://developer.vmware.com/) |
| **Categories** | domains |
| **First Published** | 2023-12-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md)

## Tables Reference

This solution uses **7 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Heartbeat`](../tables/heartbeat.md) | - | Workbooks |
| [`Syslog`](../tables/syslog.md) | - | Analytics, Workbooks |
| [`VMware_CWS_DLPLogs_CL`](../tables/vmware-cws-dlplogs-cl.md) | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) | Analytics |
| [`VMware_CWS_Health_CL`](../tables/vmware-cws-health-cl.md) | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) | Workbooks |
| [`VMware_CWS_Weblogs_CL`](../tables/vmware-cws-weblogs-cl.md) | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) | Analytics, Workbooks |
| [`VMware_SDWAN_FirewallLogs_CL`](../tables/vmware-sdwan-firewalllogs-cl.md) | - | Analytics |
| [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) | [VMware SD-WAN and SASE Connector](../connectors/vmwaresdwan.md) | Analytics, Workbooks |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 14 |
| Hunting Queries | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [VMware Cloud Web Security - Data Loss Prevention Violation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sase-cwsdlp-violation.yaml) | Medium | - | [`VMware_CWS_DLPLogs_CL`](../tables/vmware-cws-dlplogs-cl.md) |
| [VMware Cloud Web Security - Policy Change Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sase-cws-policychange.yaml) | Informational | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware Cloud Web Security - Policy Publish Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sase-cws-policy-publish.yaml) | Informational | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware Cloud Web Security - Web Access Policy Violation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sase-cws-policyviolation.yaml) | Medium | - | [`VMware_CWS_Weblogs_CL`](../tables/vmware-cws-weblogs-cl.md) |
| [VMware Edge Cloud Orchestrator - New LAN-Side Client Device Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-lanside-devicedetect.yaml) | Informational | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware SD-WAN - Orchestrator Audit Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-orchestrator-config-change.yaml) | Informational | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware SD-WAN Edge - All Cloud Security Service Tunnels DOWN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-nsd-cssdown.yaml) | Medium | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware SD-WAN Edge - Device Congestion Alert - Packet Drops](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-device-congestion.yaml) | Medium | Impact | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware SD-WAN Edge - IDS/IPS Alert triggered (Search API)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-idps-alert-api.yaml) | High | LateralMovement | [`VMware_SDWAN_FirewallLogs_CL`](../tables/vmware-sdwan-firewalllogs-cl.md) |
| [VMware SD-WAN Edge - IDS/IPS Alert triggered (Syslog)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-idps-alert-syslog.yaml) | High | LateralMovement | [`Syslog`](../tables/syslog.md) |
| [VMware SD-WAN Edge - IDS/IPS Signature Update Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-idps-updatefailed.yaml) | High | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware SD-WAN Edge - IDS/IPS Signature Update Succeeded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-idps-update-success.yaml) | Informational | - | [`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |
| [VMware SD-WAN Edge - Network Anomaly Detection - Potential Fragmentation Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-ipfrag-attempt.yaml) | Low | Impact, DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [VMware SD-WAN Edge - Network Anomaly Detection - RPF Check Failure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Analytic%20Rules/vmw-sdwan-rpfcheck.yaml) | Low | Impact | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [VMware Edge Cloud Orchestrator - High number of login failures from a source IP address](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Hunting%20Queries/VECOfrequentFailedLogins.yaml) | CredentialAccess, InitialAccess | - |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [VMwareSASESOCDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20SD-WAN%20and%20SASE/Workbooks/VMwareSASESOCDashboard.json) | [`Heartbeat`](../tables/heartbeat.md)<br>[`Syslog`](../tables/syslog.md)<br>[`VMware_CWS_Health_CL`](../tables/vmware-cws-health-cl.md)<br>[`VMware_CWS_Weblogs_CL`](../tables/vmware-cws-weblogs-cl.md)<br>[`VMware_VECO_EventLogs_CL`](../tables/vmware-veco-eventlogs-cl.md) |

## Additional Documentation

> 📄 *Source: [VMware SD-WAN and SASE/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware SD-WAN and SASE/README.md)*

VMware SASE and SD-WAN are cloud-native networking and security solutions that offer a comprehensive approach to securing and optimizing branch connectivity for today's distributed enterprises. By integrating VMware SASE and SD-WAN with Microsoft Sentinel, you can gain a unified view of your network and security posture, enabling you to proactively identify and remediate threats, improve application performance, and reduce operational complexity. 

# Release Notes:
v1.0.0 (Initial release):

## Solutions supported:
1. VMware SD-WAN
2. VMware Cloud Web Security

## Events collected:

Via Syslog (Using AMA):
1. Edge Firewall Events
2. Edge Firewall IDS/IPS Events

Via API (Function App):
1. Edge Firewall IDS/IPS Events (Backup)
2. VMware SD-WAN Audit Events
3. VMware Cloud Web Security Audit Events
4. VMware Cloud Web Security Web Logs
5. VMware Cloud Web Security DLP Logs
6. VMware SD-WAN Events
7. VMware SD-WAN NSD/CSS Events

# Deployment Guide
A detailed implementation plan will be provided as soon as the solution is published. This readme will be updated with a link to the documentation as soon as its published.

## VECO API Authorization
The solution contains a function app that deploys in Microsoft Azure. It is worth testing the ARM template in a test RG/subscription so that created tables, rules, incidents do not collide with your existing integration or other data streams.

The solution is using API Token-based authorization in a VECO enterprise. Partner/Operator-level integrations are not supported by the Function App. All API calls require an enterprise-level admin user accunt. Please follow the instructions to create an API token:
https://docs.vmware.com/en/VMware-SD-WAN/5.2/VMware-SD-WAN-Administration-Guide/GUID-2FA3763F-835C-4D10-A32B-450FEB5397D8.html

## Function App Authorization:

The Function App requires authentication to be able to call the Log Ingestion API. The ARM template does not contain these settings, so please ensure that you authorize access for each DCR (Data Collection Rule) by following the steps "Create Microsoft Entra application" and "Assign permissions to the DCR" from the following guide: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#assign-permissions-to-the-dcr.


# Solution support
All components of the solution are provided as-is. If you find a bug or if you have an idea, please share it with us on: sase-siem-integration@vmware.com Thank you!

# Function App: SD-WAN Events Collected
The Function App collects various Events from the VECO API. The list of these events can be expanded to adjust your requirements
## Cloud Security Service / Non-SD-WAN Destination:
- "ALL_CSS_DOWN",
- "CSS_UP",
- "VPN_DATACENTER_STATUS"
## Audit Events:
- BROWSER_ENTERPRISE_LOGIN",
- "USER_LOGIN_FAILURE",
- "USER_LOGIN_SSO",
- "USER_LOGIN_FAILURE_SSO",
- "EDGE_SSH_LOGIN",
- "NEW_INTEGRATED_CA",
- "CERTIFICATE_REVOCATION",
- "CERTIFICATE_RENEWAL",

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                            |
|-------------|--------------------------------|---------------------------------------------------------------|
| 3.0.0       | 13-03-2024                     | Initial Solution Release                                      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
