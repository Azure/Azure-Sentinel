# BlinkOps

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Blink Support |
| **Support Tier** | Partner |
| **Support Link** | [https://support.blinkops.com](https://support.blinkops.com) |
| **Categories** | domains |
| **First Published** | 2025-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BlinkOps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BlinkOps) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 2 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Retrieve Alert from Microsoft Sentinel and Trigger a Blink Workflow via Webhook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BlinkOps/Playbooks/Sentinel-Alert-Handler/azuredeploy.json) | Send a webhook request to a Blink workflow trigger whenever a new alert is created in Microsoft Sent... | - |
| [Retrieve Incident from Microsoft Sentinel and Trigger a Blink Workflow via Webhook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BlinkOps/Playbooks/Sentinel-Incident-Handler/azuredeploy.json) | Send a webhook request to a Blink workflow trigger whenever a new Incident is created in Microsoft S... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 06-08-2025                     | Updated **Playbooks** with a minor version bump, improved webhook payload handling, and enhanced documentation and support metadata.      		                        |
| 3.0.1       | 10-07-2025                     | Addition of a new **playbook**      		                        |    
| 3.0.0       | 20-05-2025                     | Initial Solution Release.            		                        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
