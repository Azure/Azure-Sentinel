# SlashNext

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SlashNext |
| **Support Tier** | Partner |
| **Support Link** | [https://support@slashnext.com](https://support@slashnext.com) |
| **Categories** | domains |
| **First Published** | 2022-08-12 |
| **Last Updated** | 2022-08-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SlashNext Function App](../connectors/slashnextfunctionapp.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [SlashNext Function App](../connectors/slashnextfunctionapp.md) | - |
| [`AzureMetrics`](../tables/azuremetrics.md) | [SlashNext Function App](../connectors/slashnextfunctionapp.md) | - |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 2 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SlashNext Phishing Incident Investigation Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext/Playbooks/SlashNextPhishingIncidentInvestigation/azuredeploy.json) | Enhance your security with threat hunting and incident investigation using this playbook. Scan with ... | - |
| [SlashNext Web Access Log Assessment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SlashNext/Playbooks/SlashNextWebAccessLogAssessment/azuredeploy.json) | Designed to analyze Web Access logs from Web Gateways and Firewalls. Scan your logs for continuous d... | - |

## Release Notes

| **Version**   | **Date Modified (DD-MM-YYYY)**   | **Change History**                                                                                  |
|---------------|----------------------------------|-----------------------------------------------------------------------------------------------------|
| 3.0.0         | 17-12-2024                       | Modified the Phishing Investigation application in **Data Connector** Function App. <br/> Added new **Playbook** Phishing Incident Investigation. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
