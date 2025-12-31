# Recorded Future Identity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Recorded Future Support Team |
| **Support Tier** | Partner |
| **Support Link** | [https://support.recordedfuture.com/](https://support.recordedfuture.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-06 |
| **Last Updated** | 2025-04-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **2 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`null)`](../tables/null%29.md) | Playbooks (writes) |
| [`parameters`](../tables/parameters.md) | Playbooks |

## Content Items

This solution includes **8 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 8 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [RFI-Playbook-Alert-Importer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/RFI-Playbook-Alert-Importer/azuredeploy.json) | This playbook fetches identity compromises from Recorded Future, places users in a security group an... | - |
| [RFI-Playbook-Alert-Importer-LAW](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/RFI-Playbook-Alert-Importer-LAW/azuredeploy.json) | This playbook fetches identity compromises from Recorded Future, places users in a security group an... | - |
| [RFI-Playbook-Alert-Importer-LAW-Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/RFI-Playbook-Alert-Importer-LAW-Sentinel/azuredeploy.json) | This playbook fetches identity compromises from Recorded Future, places users in a security group an... | - |
| [RFI-add-EntraID-security-group-user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/v3.0/RFI-add-EntraID-security-group-user/azuredeploy.json) | This playbook adds a compromised user to an EntraID security group. Triage and remediation should be... | - |
| [RFI-confirm-EntraID-risky-user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/v3.0/RFI-confirm-EntraID-risky-user/azuredeploy.json) | This playbook confirms compromise of users deemed 'high risk' by EntraID. | - |
| [RFI-lookup-and-save-user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/v3.0/RFI-lookup-and-save-user/azuredeploy.json) | This playbook gets compromise identity details from Recorded Future Identity Intelligence and saves ... | [`null)`](../tables/null%29.md) *(write)* |
| [RFI-search-external-user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/v3.0/RFI-search-external-user/azuredeploy.json) | This playbook searches the Recorded Future Identity Intelligence Module for compromised external (cu... | [`parameters`](../tables/parameters.md) *(read)* |
| [RFI-search-workforce-user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future%20Identity/Playbooks/v3.0/RFI-search-workforce-user/azuredeploy.json) | This playbook searches the Recorded Future Identity Intelligence Module for compromised workforce us... | [`parameters`](../tables/parameters.md) *(read)* |

## Additional Documentation

> 📄 *Source: [Recorded Future Identity/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded Future Identity/README.md)*

<img src="./Playbooks/images/logo.png" alt="RecordedFuture logo" width="50%"/>

Link to [Recorded Future main readme](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/readme.md)
# Recorded Future Identity Solution

Recorded Future Identity Intelligence enables security and IT teams to detect identity compromises.

Recorded Future automates the collection, analysis, and production of identity intelligence from a vast range of sources.

You can incorporate identity intelligence into automated workflows that regularly monitor for compromised credentials and take immediate action using Recorded Future Identity data and Microsoft Entra ID.

There are many ways organizations can utilize Recorded Future Identity Intelligence. The Azure Logic Apps in this Solution provided as examples and are a quick introduction to some of those ways.

These playbooks include several actions that can be coordinated, or used separately.

They include:

1. Ingest novel identity exposures for specified domains
1. Adding a compromised user to an Entra ID security group
1. Confirming high risk Microsoft Entra ID users
1. Looking up existing users and saving the compromised user data to a Log file

[Installation guide](Playbooks/readme.md)



### **Identity exposure ingestion**

The **recommended** playbook workflow relies on Recorded Future Playbook Alerts, where organizations configure domains to monitor for Novel Identity exposures, which can be automatically ingested and acted upon.

This playbook workflow focuses on the following actions:
- Ingesting Novel Identity Exposures
- Verifies that users exist in Entra ID
- Place the compromised users in a security group
- If possible, confirm user as risky within Entra ID
- (Optional) - Save detailed identity exposure information to Log Analytics Workspace (LAW)
- (Optional) - Create a Microsoft Sentinel incident for triage and further investigation
- Update corresponding Recorded Future Playbook Alert with remediation

Other possible remediations include password resets, user privilege revocation, and user quarantining. Advanced teams may also choose to flag users suspected of takeover by a threat actor to track usage through their system.

### Identity lookup
An alternative workflow exists, that in some cases might fit organizational needs to a higher degree.

These playbooks and actions are designed to meet the following use cases:

1. **My Organization ("Workforce" use case)**

- when suspicious employee behavior is noticed (e.g. logins from uncommon geographic locations, or large downloads of information during non business hours), query Recorded Future identity intelligence (via "Credential Lookup" Action) to check if that user has had credentials exposed in prior dumps or malware logs.


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.2       | 29-04-2025                     | Removed `Get Risky User` action from **Playbooks** due to Recorded Future can act as a authority on compromise.|
| 3.1.1       | 02-04-2025                     | Updated documentation, restructured solution and added correct paths for **Playbooks**.|
| 3.1.0       | 10-02-2025                     | Refactored solution to be based on Recorded Future **Playbook** Alerts, moved old solution to `v3.0` folder.<br> Added new **Playbooks**. |
| 3.0.1       | 27-08-2024                     | Fixedhardcoded Resource Group and Analytics Workspace Name in search **Playbooks**. |
| 3.0.0       | 15-04-2024                     | Fixedhardcoded SubscriptionID.<br> Entra ID renaming of **Playbooks** and readme.<br> Using solution format V3<br>Change prefix on all logic app installation names from RecordedFutureIdentity to RFI due to logic app name size limitation of 64 characters. |
| 2.0.0       | 14-09-2022                     | Initial Solution Release. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
