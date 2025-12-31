# SpyCloud Enterprise Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Spycloud |
| **Support Tier** | Partner |
| **Support Link** | [https://portal.spycloud.com](https://portal.spycloud.com) |
| **Categories** | domains |
| **First Published** | 2023-09-09 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`SpyCloudBreachDataWatchlist_CL`](../tables/spycloudbreachdatawatchlist-cl.md) | Analytics |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 8 |
| Analytic Rules | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SpyCloud Enterprise Breach Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Analytic%20Rules/SpyCloudEnterpriseProtectionBreachRule.yaml) | High | CredentialAccess | [`SpyCloudBreachDataWatchlist_CL`](../tables/spycloudbreachdatawatchlist-cl.md) |
| [SpyCloud Enterprise Malware Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Analytic%20Rules/SpyCloudEnterpriseProtectionMalwareRule.yaml) | High | CredentialAccess | [`SpyCloudBreachDataWatchlist_CL`](../tables/spycloudbreachdatawatchlist-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Domain Breach Data - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Get-Domain-Breach-Data-Playbook/azuredeploy.json) | The SpyCloud Enterprise API is able to provide breach data for a domain or set of domains associated... | - |
| [Email Address Breach Data - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Get-Email-Breach-Data-Playbook/azuredeploy.json) | The SpyCloud Enterprise API is able to provide breach data for a Email address or set of Email addre... | - |
| [IP Address Breach Data - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Get-IP-Breach-Data-Playbook/azuredeploy.json) | The SpyCloud Enterprise API is able to provide breach data for a IP address or set of IP addresses a... | - |
| [Password Breach Data - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Get-Password-Breach-Data-Playbook/azuredeploy.json) | The SpyCloud Enterprise API is able to provide breach data for a provided password. | - |
| [SpyCloud Breach Information - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Breach-Playbook/azuredeploy.json) | This Playbook will be triggered when an spycloud breach incident is created. | - |
| [SpyCloud Malware Information - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Malware-Playbook/azuredeploy.json) | This Playbook will be triggered when an spycloud malware incident is created. | - |
| [SpyCloud Watachlist data - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Monitor-Watchlist-Data/azuredeploy.json) | This Playbook will run daily, gets the watchlist data from SpyCloud API and saved it into the custom... | - |
| [Username Breach Data - SpyCloud Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud%20Enterprise%20Protection/Playbooks/SpyCloud-Get-Username-Breach-Data-Playbook/azuredeploy.json) | The SpyCloud Enterprise API is able to provide breach data for a username or set of usernames associ... | - |

## Additional Documentation

> 📄 *Source: [SpyCloud Enterprise Protection/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SpyCloud Enterprise Protection/README.md)*

## Table of Contents

1. [Overview](#overview)
2. [Feed](#feed)
3. [Enrichment](#enrichment)
4. [SpyCloud Enterprise Deployment Instructions](#deployorder)


<a name="overview">

## Overview
Cybercriminals continue to utilize stolen corporate credentials as the number one technique for account takeover (ATO). In fact, the FBI estimated that this resulted in estimated losses totaling more than $2.7 billion in 2022. SpyCloud helps prevent account takeover and ransomware attacks by identifying exposed credentials related to a company’s domains, IP addresses and emails. Through this integration, breach and malware data from SpyCloud can be loaded into Sentinel. 

This solution contains the following:

- Eight playbooks,

- Two analytics rules, and 

- One custom connector. 

By identifying exposed assets that are available to criminals, enterprises can protect exposed accounts before criminals have a chance to use them for follow-on attacks These playbooks and actions are designed to meet several use cases.

<a name="feed"></a>
## Feed Usecase
| Playbook | Description |
| --------- | -------------- |
| **SpyCloud-Monitor-Watchlist-Data** | This playbook runs on a daily basis, and fetches all the watchlist data from the SpyCloud Enterprise Protection API, parses the data, and saves the data into the custom logs table. |

This solution provides the following rules which monitor the custom log table created from the above playbook.

### Analytics Rules
| Analytic Rule | Description |
| --------- | -------------- |
| **SpyCloud-Malware-Rule** | This scheduled rule monitors the custom log table, and checks for any new malware records(severity=25). If a record is found, this analytic rule will create an incident with High Priority. |
| **SpyCloud-Breach-Rule** | This scheduled rule monitors the custom log table, and checks for any new breach records(severity=20). If a record is found, this analytic rule will create an incident with High Priority. |

Many actions are available when a malware incident is created from the "SpyCloud Malware Rule." It can:

- Check if the hostname is a managed asset. If no hostname exists in the record it will skip this check.
- Pull all the additional records for the specific machine ID from the appropriate endpoint and add them to the incident, if you have access to SpyCloud Compass data. 
- Escalate the incident for someone to handle the malware infection. 

This solution also provides a "SpyCloud Malware Playbook" template that can be used to achieve the above use case. You can add this playbook to the "SpyCloud Malware Rule" automation section.

The following actions can be taken when a breach incident is created from the "SpyCloud Breach Rule."

- Check if breached password length is >= minimum required by the organization. If not, exit the playbook. 
- Check if the user is currently an active employee. If not, exit the playbook. 

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 18-07-2024                     | Fixed Invalid **Analytic Rule** SpyCloudEnterpriseProtectionMalwareRule.yaml |
| 3.0.0       | 12-09-2023                     | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
