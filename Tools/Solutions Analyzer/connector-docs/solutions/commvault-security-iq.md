# Commvault Security IQ

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Commvault |
| **Support Tier** | Partner |
| **Support Link** | [https://www.commvault.com/support](https://www.commvault.com/support) |
| **Categories** | domains |
| **First Published** | 2023-08-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CommvaultSecurityIQ](../connectors/commvaultsecurityiq-cl.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommvaultSecurityIQ_CL`](../tables/commvaultsecurityiq-cl.md) | [CommvaultSecurityIQ](../connectors/commvaultsecurityiq-cl.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Commvault Cloud Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Analytic%20Rules/CommvaultSecurityIQ_Alert.yaml) | Medium | DefenseEvasion, Impact | [`CommvaultSecurityIQ_CL`](../tables/commvaultsecurityiq-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Commvault Disable Data Aging Logic App Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Playbooks/Commvault_Disable_Data_Aging_Logic_App/azuredeploy.json) | This Logic App executes when called upon by an Automation Rule. Accessing the KeyVault to retrieve v... | - |
| [Commvault Disable SAML Provider Logic App Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Playbooks/Commvault_Disable_SAML_Provider_Logic_App/azuredeploy.json) | This Logic App executes when called upon by an Automation Rule. Accessing the KeyVault to retrieve v... | - |
| [Commvault Disable User Logic App Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Playbooks/Commvault_Disable_User_Logic_App/azuredeploy.json) | This Logic App executes when called upon by an Automation Rule. Accessing the KeyVault to retrieve v... | - |

## Additional Documentation

> 📄 *Source: [Commvault Security IQ/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault Security IQ/README.md)*

Commvault Cloud - Microsoft Sentinel Integration
===============================================

This SOAR integration connects Commvault Cloud with Microsoft Sentinel to enable automated incident creation and response through Analytic Rules and Playbooks.

## Overview
This solution provides:
- **Data Ingestion**: Automated collection of Commvault security events and anomalies
- **Incident Creation**: Automatic creation of Sentinel incidents based on Commvault security events
- **Incident Response**: Playbooks for automated remediation actions (disable users, disable data aging, etc.)

## Prerequisites
Before beginning the installation, ensure you have:

### Commvault Requirements
- **Administrative Access**: Admin or Tenant Admin privileges in Commvault Cloud/Metallic
- **API Access**: Ability to generate access tokens for API integration

### Azure Requirements
- **Subscription Access**: Contributor or Owner permissions on the Azure subscription
- **Resource Group Access**: Ability to create and manage resources in the target resource group
- **Microsoft Sentinel**: An active Sentinel workspace deployed in your Azure environment
- **Log Analytics Workspace**: A Log Analytics workspace associated with your Sentinel instance
- **Azure Cloud Shell**: Access to Azure Cloud Shell with PowerShell support

## Required Azure Resources
The following Azure resources will be created or configured during this installation:

### Key Vault
- **Purpose**: Securely stores Commvault credentials and API endpoints
- **Required Secrets**:
  - `access-token`: Your Commvault Cloud access token
  - `environment-endpoint-url`: Your Commvault Cloud API endpoint URL (Commvault/Metallic endpoint URL : https://`hostname`/commandcenter/api )
  - `refresh-token`: Your Commvault Cloud refresh token

Installation
------------

**1\. Create Access Token in Commvault:**

*   Follow the instructions in [Creating an Access Token / Refresh Token](https://documentation.commvault.com/2024e/essential/creating_access_token.html).
*   Ensure the user creating the token has **Admin** or **Tenant Admin** privileges.

**2\. Create KeyVault:**

*   Azure Portal -> KeyVault -> Create -> Basics (select subscription, RG).

**3\. Create KeyVault Secrets:**

*   Azure Portal -> KeyVault -> Secrets -> Generate/Import -> Manual:
    *   Name: access-token, Value: (Your Commvault/Metallic access token), Enabled: Yes -> Create.
    *   Name: refresh-token, Value: (Your Commvault/Metallic refresh token), Enabled: Yes -> Create.
    *   Name: environment-endpoint-url, Value: (Your Commvault/Metallic endpoint's URL), Enabled: Yes -> Create.

**4\. Install Commvault Cloud Solution:**

*   Sentinel -> Content hub -> Search "Commvault Cloud" -> Install.

**5\. Configure Data Connector:**

*   Commvault Cloud -> CommvaultSecurityIQ (using Azure Functions) -> Open connector page -> Deploy to Azure -> Fill details -> Create.

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 12-09-2025                     | Enhanced **Data connector** with configurable event collection and streamlined deployment  |
| 3.0.2       | 28-03-2024                     | Update **Playbook** - Bug fix in disabling data aging  |
| 3.0.1       | 28-03-2024                     | Adding **Data Connector** for Commvault Sentinel Integration|
| 3.0.0       | 21-08-2023                     | Initial Solution Release|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
