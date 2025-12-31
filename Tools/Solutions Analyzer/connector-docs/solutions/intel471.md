# Intel471

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Intel 471 |
| **Support Tier** | Partner |
| **Support Link** | [https://intel471.com/company/contact](https://intel471.com/company/contact) |
| **Categories** | domains |
| **First Published** | 2023-06-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Intel471](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Intel471) |

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
| [Intel 471 Malware Intelligence to Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Intel471/Playbooks/Intel471-ImportMalwareIntelligenceToSentinel/azuredeploy.json) | This playbook ingests malware indicators from Intel 471's Titan or Verity API into Microsoft Sentine... | - |
| [[Deprecated] Intel 471 Malware Intelligence to Graph Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Intel471/Playbooks/Intel471-ImportMalwareIntelligenceToGraphSecurity/azuredeploy.json) | This playbook ingests malware indicators from Intel 471's Titan API into Microsoft Graph Security as... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 02-12-2025                     |  Added **Playbook** 'Intel 471 Malware Intelligence to Graph Security' using new upload indicators API to Intel 471 Solution. <br/> Added the Verity471 backend in the Intel471 solution for ingesting malware indicators.|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
