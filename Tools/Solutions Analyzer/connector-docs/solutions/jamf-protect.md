# Jamf Protect

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Jamf Software, LLC |
| **Support Tier** | Partner |
| **Support Link** | [https://www.jamf.com/support/](https://www.jamf.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-10-10 |
| **Last Updated** | 2025-09-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Jamf Protect Push Connector](../connectors/jamfprotectpush.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`JamfProtect`](../tables/jamfprotect.md) | - | Workbooks |
| [`jamfprotect_CL`](../tables/jamfprotect-cl.md) | - | Analytics |
| [`jamfprotectalerts_CL`](../tables/jamfprotectalerts-cl.md) | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) | Analytics, Workbooks |
| [`jamfprotecttelemetryv2_CL`](../tables/jamfprotecttelemetryv2-cl.md) | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) | Workbooks |
| [`jamfprotectunifiedlogs_CL`](../tables/jamfprotectunifiedlogs-cl.md) | [Jamf Protect Push Connector](../connectors/jamfprotectpush.md) | Analytics, Workbooks |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 5 |
| Analytic Rules | 3 |
| Playbooks | 3 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Jamf Protect - Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Analytic%20Rules/JamfProtectAlerts.yaml) | High | - | [`jamfprotectalerts_CL`](../tables/jamfprotectalerts-cl.md) |
| [Jamf Protect - Network Threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Analytic%20Rules/JamfProtectNetworkThreats.yaml) | Informational | InitialAccess | [`jamfprotect_CL`](../tables/jamfprotect-cl.md) |
| [Jamf Protect - Unified Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Analytic%20Rules/JamfProtectUnifiedLogs.yaml) | Informational | - | [`jamfprotectunifiedlogs_CL`](../tables/jamfprotectunifiedlogs-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [JamfProtectDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Workbooks/JamfProtectDashboard.json) | [`JamfProtect`](../tables/jamfprotect.md)<br>[`jamfprotectalerts_CL`](../tables/jamfprotectalerts-cl.md)<br>[`jamfprotecttelemetryv2_CL`](../tables/jamfprotecttelemetryv2-cl.md)<br>[`jamfprotectunifiedlogs_CL`](../tables/jamfprotectunifiedlogs-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Jamf Protect - Remote lock computer with Jamf Pro](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Playbooks/JamfProtect_LockComputer_with_JamfPro/azuredeploy.json) | This Playbook can be used manually or in a Automation Rule to send an remote MDM command with Jamf P... | - |
| [Jamf Protect - Set Alert to In Progress](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Playbooks/JamfProtect_Alert_Status_InProgress/azuredeploy.json) | This Jamf Protect Playbook can be used manually or in a Automation Rule to change the state of the A... | - |
| [Jamf Protect - Set Alert to Resolved](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Playbooks/JamfProtect_Alert_Status_Resolved/azuredeploy.json) | This Jamf Protect Playbook can be used manually or in a Automation Rule to change the state of the A... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [JamfProtectAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Parsers/JamfProtectAlerts.yaml) | - | - |
| [JamfProtectNetworkTraffic](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Parsers/JamfProtectNetworkTraffic.yaml) | - | - |
| [JamfProtectTelemetry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Parsers/JamfProtectTelemetry.yaml) | - | - |
| [JamfProtectThreatEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Parsers/JamfProtectThreatEvents.yaml) | - | - |
| [JamfProtectUnifiedLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Jamf%20Protect/Parsers/JamfProtectUnifiedLogs.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
|3.3.0        | 02-09-2025                     | Adding support for newly added event types in Telemetry, TCC_MODIFY,NETWORK_CONNECT, PTY_GRANT, PTY_CLOSE and some enhancements to mount and process object mapping.
|3.2.4        | 27-03-2025                     | Resolving issues related to the new Push Connector and the DCE/DCRs. Removing support for Telemetry Legacy in this newer Push Connector. Removing Hunting Queries as they were not relevant anymore. Updated Analytic Rules and Workbooks to work with the updated parsers, the single parser got split up to be more useful to customers that only use certain features. 
|3.2.1        | 24-02-2025                     | Adding support for the newly released `gatekeeper_user_override` event and removing totalRetentionInDays from the Push Connector.
| 3.2.0       | 04-02-2025                     | Added new CCP **Data Connector** to the Solution.
| 3.1.1       | 30-04-2024                     | Repackaged for parser issue fix while reinstall.
| 3.1.0       | 12-01-2024                     | Improved data normalization in the parser JamfProtect, ParentProcess is better mapped now, productVersion has been added and more. Added new macOS Hunting Queries including recent malware IOCs.
| 3.0.1       | 05-12-2023                     | Minor tweak to parser related to signerType
| 3.0.0       | 20-10-2023                     | Added **Parser** for parsing jamfprotect_CL raw logs.
|             |                                | Modified existing **Analytic Rules** & **Workbooks** to make use of newly added parser in this release.
|             |                                | Added macOS Threat Hunting **Hunting Queries** for hunting macOS specific threats retrospectivly
|             |                                | Added **Playbooks** for interacting with the Jamf Protect and Jamf Pro API's, including Remote Locking a computer, and changes Alert statusses based on a Microsoft Sentinel incident. 
| 2.1.1       | 03-03-2023                     | Updating **Analytic Rules** to include MITRE Tactics and Techniques.
| 2.1.0       | 10-02-2023                     | Added **Data Connector** for monitoring logs
|             |                                | Added **Analytics Rules** for automated incident creation within Microsoft Sentinel
|             |                                | Improved **Workbook** and added Endpoint Telemetry
| 2.0.0       | 12-10-2022                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
