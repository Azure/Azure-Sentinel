# SentinelSOARessentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **4 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`SentinelHealth`](../tables/sentinelhealth.md) | Workbooks |
| [`getAmountOfIncidentForRuleId`](../tables/getamountofincidentforruleid.md) | Workbooks |
| [`strcat_array`](../tables/strcat-array.md) | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | Playbooks, Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **29 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 25 |
| Workbooks | 4 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AutomationHealth](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Workbooks/AutomationHealth.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`SentinelHealth`](../tables/sentinelhealth.md)<br>[`strcat_array`](../tables/strcat-array.md) |
| [IncidentOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Workbooks/IncidentOverview.json) | [`getAmountOfIncidentForRuleId`](../tables/getamountofincidentforruleid.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |
| [IncidentTasksWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Workbooks/IncidentTasksWorkbook.json) | *Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md) |
| [SecurityOperationsEfficiency](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Workbooks/SecurityOperationsEfficiency.json) | *Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Incident From Microsoft Forms Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/CreateIncident-MicrosoftForms/azuredeploy.json) | This playbook will create a new Microsoft Sentinel incident when Microsoft Forms response is submitt... | - |
| [Create Incident From Shared Mailbox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/CreateIncident-SharedMailbox/azuredeploy.json) | This playbook will create a new Microsoft Sentinel incident when new email arrives to shared mailbox... | - |
| [HTTP Trigger Entity Analyzer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Http-Trigger-Entity-Analyzer/azuredeploy.json) | This playbook is triggered by HTTP POST requests with entity information and performs automated inve... | - |
| [Incident Assignment Shifts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Assignment-Shifts/azuredeploy.json) | This playbook will assign an Incident to an owner based on the Shifts schedule in Microsoft Teams. W... | - |
| [Incident Trigger Entity Analyzer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Incident-Trigger-Entity-Analyzer/azuredeploy.json) | This playbook is triggered by Microsoft Sentinel incidents and performs automated investigation and ... | - |
| [Incident tasks - Microsoft Defender XDR BEC Playbook for SecOps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Defender_XDR_BEC_Playbook_for_SecOps-Tasks/azuredeploy.json) | This playbook add Incident Tasks based on Microsoft Defender XDR BEC Playbook for SecOps. This playb... | - |
| [Incident tasks - Microsoft Defender XDR Phishing Playbook for SecOps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Defender_XDR_Phishing_Playbook_for_SecOps-Tasks/azuredeploy.json) | This playbook add Incident Tasks based on Microsoft Defender XDR Phishing Playbook for SecOps. This ... | - |
| [Incident tasks - Microsoft Defender XDR Ransomware Playbook for SecOps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Defender_XDR_Ransomware_Playbook_for_SecOps-Tasks/azuredeploy.json) | This playbook add Incident Tasks based on Microsoft Defender XDR Ransomware Playbook for SecOps. Thi... | - |
| [Notify Incident Owner in Microsoft Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Notify-Owner/azuredeploy.json) | This playbook sends a Teams message to the new incident owner. | - |
| [Notify When Incident Is Closed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Notify-IncidentClosed/azuredeploy.json) | This playbook is utilizing new update trigger to notify person/group on Microsoft Teams/Outlook when... | - |
| [Notify When Incident Is Reopened](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Notify-IncidentReopened/azuredeploy.json) | This playbook is utilizing new update trigger to notify person/group on Microsoft Teams/Outlook when... | - |
| [Notify When Incident Severity Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Notify-IncidentSeverityChanged/azuredeploy.json) | This playbook is utilizing new update trigger to notify person/group on Microsoft Teams/Outlook when... | - |
| [Post Message Slack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Post-Message-Slack/alert-trigger/azuredeploy.json) | This playbook will post a message in a Slack channel when an alert is created in Microsoft Sentinel | - |
| [Post Message Slack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Post-Message-Slack/incident-trigger/azuredeploy.json) | This playbook will post a message in a Slack channel when an Incident is created in Microsoft Sentin... | - |
| [Post Message Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Post-Message-Teams/alert-trigger/azuredeploy.json) | This playbook will post a message in a Microsoft Teams channel when an Alert is created in Microsoft... | - |
| [Post Message Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Post-Message-Teams/incident-trigger/azuredeploy.json) | This playbook will post a message in a Microsoft Teams channel when an Incident is created in Micros... | - |
| [Post-Message-Slack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Post-Message-Slack/azuredeploy.json) | - | - |
| [Post-Message-Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Post-Message-Teams/azuredeploy.json) | - | - |
| [Relate alerts to incident by IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/relateAlertsToIncident-basedOnIP/azuredeploy.json) | This playbook looks for other alerts with the same IP as the triggered incident. When such an alert ... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [Send Teams Adaptive Card on incident creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Send-Teams-adaptive-card-on-incident-creation/azuredeploy.json) | This playbook will send Microsoft Teams Adaptive Card on incident creation, with the option to chang... | - |
| [Send basic email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Send-basic-email/azuredeploy.json) | This playbook will be sending email with basic incidents details (Incident title, severity, tactics,... | - |
| [Send email with formatted incident report](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Send-email-with-formatted-incident-report/azuredeploy.json) | This playbook will be sending email with formated incidents report (Incident title, severity, tactic... | - |
| [Send incident Teams Adaptive Card with XDR Portal links](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Send-Incident-Teams-Adaptive-Card-XDRPortal/azuredeploy.json) | This playbook will send a Teams adaptive card with incident and entity information with all links po... | - |
| [Send incident email with XDR Portal links](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Send-Incident-Email-XDRPortal/azuredeploy.json) | This playbook will send an email with incident and entity information with all links pointing to the... | - |
| [URL Trigger Entity Analyzer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelSOARessentials/Playbooks/Url-Trigger-Entity-Analyzer/azuredeploy.json) | This playbook is triggered manually when a URL entity is selected in a Microsoft Sentinel incident a... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)**  | **Change History**                                                                         |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------|
| 3.0.6       | 24-12-2025                     | Added new **playbooks** for the incident alerting.|
| 3.0.5       | 11-12-2025                     | Updated the lookback value to 7 days across all three **Logic Apps** and Renamed the Logic App title to "URL Trigger Entity Analyzer".|
| 3.0.4       | 17-11-2025                     | Added new **playbooks** for the Sentinel SentinelSOARessentials solution.                  |
| 3.0.3       | 30-05-2025                     | This upgrade focused on improving **Playbook** functionality, updating documentation, and refining deployment parameters.               |
| 3.0.2       | 26-10-2023                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR.               |
| 3.0.1       | 11-08-2023                     | Updated timeContextFromParameter with TimeRange in the **Workbook** template.               |
| 3.0.0       | 17-07-2023                     | Updated **Workbook** template to remove unused variables.                                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
