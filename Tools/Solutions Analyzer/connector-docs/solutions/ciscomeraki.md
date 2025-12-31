# CiscoMeraki

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-09-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [[Deprecated] Cisco Meraki](../connectors/ciscomeraki.md)
- [Cisco Meraki (using REST API)](../connectors/ciscomeraki%28usingrestapi%29.md)
- [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CiscoMerakiNativePoller_CL`](../tables/ciscomerakinativepoller-cl.md) | [Cisco Meraki (using REST API)](../connectors/ciscomeraki(usingrestapi).md), [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md), [[Deprecated] Cisco Meraki](../connectors/ciscomeraki.md) | Workbooks |
| [`meraki_CL`](../tables/meraki-cl.md) | [Cisco Meraki (using REST API)](../connectors/ciscomeraki(usingrestapi).md), [Cisco Meraki (using REST API)](../connectors/ciscomerakinativepoller.md), [[Deprecated] Cisco Meraki](../connectors/ciscomeraki.md) | Workbooks |

## Content Items

This solution includes **7 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 5 |
| Workbooks | 1 |
| Parsers | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CiscoMerakiWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Workbooks/CiscoMerakiWorkbook.json) | [`CiscoMerakiNativePoller_CL`](../tables/ciscomerakinativepoller-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block Device Client - Cisco Meraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Playbooks/Block-Device-Client/azuredeploy.json) | This playbook checks if malicious device client is blocked by Cisco Meraki network. | - |
| [Block IP Address - Cisco Meraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Playbooks/Block-IP-Address/azuredeploy.json) | This playbook checks if malicious IP address is blocked or unblocked by Cisco Meraki MX network. | - |
| [Block URL - Cisco Meraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Playbooks/Block-URL/azuredeploy.json) | This playbook checks if malicious URL is blocked in Cisco Meraki network. | - |
| [IP Address Enrichment - Cisco Meraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Playbooks/IP-Address-Enrichment/azuredeploy.json) | This playbook checks if malicious IP address is blocked or unblocked by Cisco Meraki MX network. | - |
| [URL Enrichment - Cisco Meraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Playbooks/URL-Enrichment/azuredeploy.json) | This playbook checks if malicious URL is blocked or unblocked by Cisco Meraki network. | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoMeraki](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Parsers/CiscoMeraki.yaml) | - | - |

## Additional Documentation

> 📄 *Source: [CiscoMeraki/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/README.md)*

# Cisco Meraki Logic Apps Custom Connector and Playbook Templates

![meraki](./Connector/MerakiConnector/logo.jpg)


## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 5 Playbook templates](#deploy)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Limitations](#limitations)


<a name="overview">

# Overview
Cisco Meraki connector connects to Cisco Meraki Dashboard API service endpoint and programmatically manages and monitors Meraki networks at scale.


<a name="deploy">

# Deploy Custom connector + 5 Playbook templates
This package includes:
* Custom connector for Cisco Meraki.
* Five playbook templates leverage Cisco Meraki custom connector.

You can choose to deploy the whole package : Connector + all five playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoMeraki%2FConsolidatedTemplate.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoMeraki%2FConsolidatedTemplate.json)



# Cisco Meraki documentation 

<a name="authentication">

# Authentication
API Key Authentication

<a name="prerequisites">

# Prerequisites for using and deploying Custom connector + 5 playbooks
1. Cisco Meraki API Key should be known to establish a connection with Cisco Meraki Custom Connector. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/authorization)
2. Cisco Meraki Dashboard API service endpoint should be known. (e.g. https://{CiscoMerakiDomain}/api/{VersionNumber}) [Refer here](https://developer.cisco.com/meraki/api-v1/#!schema)
3. Organization name should be known. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-organization-id) 
4. Network name should be known.[Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-network-id)
5. Network Group Policy name should be known. [Refer here](https://developer.cisco.com/meraki/api-v1/#!get-network-group-policy)

<a name="deployment">

# Deployment instructions 
1. Deploy the Custom connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameter  | Description |
| ------------- | ------------- |
|**For Playbooks**|                 |
|**Block Device Client Playbook Name** | Enter the Block Device Client playbook name without spaces |
|**Block IP Address Playbook Name** | Enter the Block IP Address playbook name without spaces |

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.5       | 11-06-2025                     | Correct name shown on **Data Types** to match query used..  |
| 3.0.4       | 23-07-2025                     | **Workbook** updated with new ThreatIntelIndicators table.  |
| 3.0.3       | 02012-2024                     | Removed Deprecated **Data Connectors**                      |
| 3.0.2       | 12-08-2024                     | Deprecating data connector                                  |
| 3.0.1       | 26-07-2023                     | Updated **Workbook** template to remove unused variables.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
