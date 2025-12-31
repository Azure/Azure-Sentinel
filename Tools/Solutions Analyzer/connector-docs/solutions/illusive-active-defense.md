# Illusive Active Defense

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Active%20Defense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Active%20Defense) |

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
| [Illusive-SentinelIncident-Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Active%20Defense/Playbooks/Illusive-SentinelIncident-Enrichment/azuredeploy.json) | - | - |
| [Illusive-SentinelIncident-Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive%20Active%20Defense/Playbooks/Illusive-SentinelIncident-Response/azuredeploy.json) | - | - |

## Additional Documentation

> 📄 *Source: [Illusive Active Defense/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illusive Active Defense/README.md)*

[image](./Images/logo.jpg)
<p align="left">  
<img width="300" height="100" src="./Images/logo.jpg"> </a>
</p>

# Illusive Active Defense Sentinel Solution

Instructions for configuring, running, and using the Illusive Active Defense Sentinel solution.

# Table of Contents

 1. [Executive summary](#executive_summary)
 2. [Basic requirements](#BasicRequirements)
 3. [Workflow](#workflowlink)
 4. [Locate the Sentinel workspace](#Sentinel_Workspace)
 5. [Azure application setup](#azureappsetup)
     - [Register an Azure app](#Register_Azure_App)
     - [Collect app information](#Collect_App_Information)
     - [Generate and save a Client Secret](#Generate_ClientSecret)
     - [Add the User Impersonation API permission](#Add_UserImpersonation)
 6. [Generate an Illusive API key](#Illusive_API_Key)
 7. [Configure Illusive to send logs to a Linux-based syslog server](#SIEM_Server)
 8. [Deploy solution package or deploy playbooks](#Deploy_Playbooks)
 9. [Configure the Illusive analytic rule](#Illusive_analytic_rule)
 10. [Access and view the playbook](#Access_playbook)

<a name="executive_summary">

# Executive summary

Configure Sentinel and load custom playbooks to have Illusive open Sentinel incidents, populate them with Illusive-based information, and automate incident response.

This solution contains the following components:

- **Incident Enrichment playbook** – leverages Sentinel analytic rules to discover Illusive-based alerts and report the associated data and forensics as Sentinel incident sets.  
  Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource.
- **Incident Response playbook** – leverages CrowdStrike or Microsoft Defender for Endpoint integration to automate incident response when specified Illusive incidents are discovered.  
 Use this playbook to quickly stop or slow down ransomware attacks and critical incidents detected by Illusive in your organization. Upon detection, Sentinel is instructed to use the triggering process information reported by Illusive remove or kill the process. If the triggering process cannot be killed, Sentinel is instructed to isolate the host. These capabilities are available for organizations with CrowdStrike Falcon or Microsoft Defender for Endpoint.

- **Analytic Rule** - Trigger a Sentinel alert upon detecting an Illusive event and create a Sentinel incident. The Sentinel incident will correspond to the Illusive incident and will include all subsequent associated Illusive events. The Illusive solution playbooks require the analytic rule to operate.

<a name="BasicRequirements">
  
## Basic requirements (set up in advance)

To use the Illusive Active Defense solution, you must have the following:

- An Azure AD subscription with a configured Sentinel workspace
- An Illusive ADS (deceptions) license

*[Content truncated...]*

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
