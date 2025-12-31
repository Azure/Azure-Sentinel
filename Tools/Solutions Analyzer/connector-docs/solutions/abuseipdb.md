# AbuseIPDB

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbuseIPDB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbuseIPDB) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AbuseIPDB Blacklist Ip To Threat Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbuseIPDB/Playbooks/AbuseIPDB-BlacklistIpToThreatIntelligence/azuredeploy.json) | By every day reccurence, this playbook gets triggered and performs the following actions: 1. Gets [l... | - |
| [AbuseIPDB Enrich Incident By IP Info](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbuseIPDB/Playbooks/AbuseIPDB-EnrichIncidentByIPInfo/azuredeploy.json) | Once a new sentinal incident is created, this playbook gets triggered and performs the following act... | - |
| [AbuseIPDB Report IPs To AbuseIPDB After User Response In MSTeams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AbuseIPDB/Playbooks/AbuseIPDB-ReportIPsAfterUserResponseInMSTeams/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                               |
|-------------|--------------------------------|----------------------------------------------------------------------------------|
| 3.0.2       | 09-12-2025                     | Fix typos and update img Source in AbuseIPDB **Playbook** Solutions	      |
| 3.0.1       | 29-03-2024                     | Updated **playbook** description and corrected sentense formatting			      |
| 3.0.0       | 31-07-2023                     | Updated prerequisites for  AbuseIPDB-BlacklistIpToThreatIntelligence **playbook**    |
|             |                                | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.         |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
