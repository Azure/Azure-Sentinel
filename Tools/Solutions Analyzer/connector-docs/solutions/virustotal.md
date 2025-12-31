# VirusTotal

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **4 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`VTDomainReport_CL`](../tables/vtdomainreport-cl.md) | Playbooks (writes) |
| [`VTFileReport_CL`](../tables/vtfilereport-cl.md) | Playbooks (writes) |
| [`VTIPReport_CL`](../tables/vtipreport-cl.md) | Playbooks (writes) |
| [`VTURLReport_CL`](../tables/vturlreport-cl.md) | Playbooks (writes) |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 9 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [FileHash Enrichment - Virus Total Report - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalFileInfo/alert-trigger/azuredeploy.json) | This playbook will take each File Hash entity and query VirusTotal for file report (https://develope... | [`VTFileReport_CL`](../tables/vtfilereport-cl.md) *(write)* |
| [FileHash Enrichment - Virus Total Report - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalFileInfo/incident-trigger/azuredeploy.json) | This playbook will take each File Hash entity and query VirusTotal for file report (https://develope... | [`VTFileReport_CL`](../tables/vtfilereport-cl.md) *(write)* |
| [IP Enrichment - Virus Total Report  - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalIPReport/incident-trigger/azuredeploy.json) | This playbook will take each IP entity and query VirusTotal for IP Address Report (https://developer... | [`VTIPReport_CL`](../tables/vtipreport-cl.md) *(write)* |
| [IP Enrichment - Virus Total Report - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalIPReport/alert-trigger/azuredeploy.json) | This playbook will take each IP entity and query VirusTotal for IP Address Report (https://developer... | [`VTIPReport_CL`](../tables/vtipreport-cl.md) *(write)* |
| [IP Enrichment - Virus Total Report - Entity Trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalIPReport/entity-trigger/azuredeploy.json) | This playbook will query VirusTotal Report for the selected IP Address (https://developers.virustota... | - |
| [URL Enrichment - Virus Total Domain Report - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalDomainReport/alert-trigger/azuredeploy.json) | This playbook will take each URL entity and query VirusTotal for Domain info (https://developers.vir... | [`VTDomainReport_CL`](../tables/vtdomainreport-cl.md) *(write)* |
| [URL Enrichment - Virus Total Domain Report - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalDomainReport/incident-trigger/azuredeploy.json) | This playbook will take each URL entity and query VirusTotal for Domain Report (https://developers.v... | [`VTDomainReport_CL`](../tables/vtdomainreport-cl.md) *(write)* |
| [URL Enrichment - Virus Total Report - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalURLReport/alert-trigger/azuredeploy.json) | This playbook will take each URL entity and query VirusTotal for info (https://developers.virustotal... | [`VTURLReport_CL`](../tables/vturlreport-cl.md) *(write)* |
| [URL Enrichment - Virus Total Report - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirusTotal/Playbooks/Get-VirusTotalURLReport/incident-trigger/azuredeploy.json) | This playbook will take each URL entity and query VirusTotal for info (https://developers.virustotal... | [`VTURLReport_CL`](../tables/vturlreport-cl.md) *(write)* |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.1       | 02-06-2025                     | Updated Playbook instructions for clarity                          |
| 3.0.0       | 11-01-2024                     | Updated solution to 3.0.0 to fix IP Enrichment - Virus Total report playbook|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
