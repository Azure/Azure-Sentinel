# Zscaler OAuth2 Lookup Sandbox Report Playbook

This playbook enables automated sandbox report lookup in Zscaler Internet Access (ZIA) when triggered by Microsoft Sentinel incidents. It uses OAuth2 authentication to securely query the Zscaler API and retrieve detailed sandbox analysis reports for file hashes found in incidents.

## Overview

The Zscaler-Oauth2-LookupSandboxReport playbook is designed to:

- Automatically extract file hash entities from Microsoft Sentinel incidents
- Parse and extract MD5 hashes from the file hash data
- Authenticate with Zscaler ZIA using OAuth2 via the authentication playbook
- Query Zscaler's Sandbox Report API to retrieve detailed analysis results
- Provide full sandbox report details for threat investigation and enrichment

## Prerequisites

Before deploying this playbook, ensure you have:

1. A Zscaler Internet Access (ZIA) subscription with API access and Cloud Sandbox enabled
2. The **Zscaler-Oauth2-Authentication** playbook deployed in the same resource group
3. An **Integration Account** named "Zscaler-Logicapp" deployed in the same resource group (required for JavaScript code execution)
4. OAuth2 client credentials (Client ID and Client Secret) configured in Azure Key Vault
5. Appropriate permissions to deploy Azure Logic Apps

## Deployment

Click the button below to deploy the Zscaler-Oauth2-LookupSandboxReport playbook to your Azure environment:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2LookupSandboxReport%2Fazuredeploy.json)

## Post-Deployment Configuration

After deployment, complete the following steps:

1. **Create Integration Account** (if not already present)
   - Create an Integration Account named "Zscaler-Logicapp" in the same resource group
   - This is required for the JavaScript code execution action

2. **Authorize API Connections**
   - Navigate to the Logic App in the Azure portal
   - Go to API connections and authorize the Microsoft Sentinel connection
   - Ensure the managed identity has appropriate permissions

3. **Grant Required Permissions**
   - Assign the Logic App managed identity the "Microsoft Sentinel Responder" role on your workspace
   - Verify the Zscaler-Oauth2-Authentication playbook is deployed and accessible

4. **Configure Zscaler API URL** (Optional)
   - The default Base URL is "zsapi.zscaler.net/api/v1"
   - To change, edit the playbook and update the "Get_Base_URL" action

5. **Configure Automation Rules**
   - Create automation rules in Microsoft Sentinel to trigger this playbook
   - Configure rules to run on incidents containing file hash entities

## Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| PlaybookName | Name of the Logic App | Zscaler-Oauth2-LookupSandboxReport |

## Workflow

1. Triggered by Microsoft Sentinel incident creation
2. Initializes the Zscaler API Base URL variable
3. Extracts file hash entities from the incident
4. For each file hash:
   - Parses the file hash entity to extract hash details
   - Executes JavaScript code to extract the MD5 hash value
   - Calls the Zscaler-Oauth2-Authentication playbook to obtain an access token
   - Queries the Zscaler Sandbox Report API (`/sandbox/report/{md5}?details=full`)
5. Returns full sandbox analysis report for each file hash

## Learn More

- [Zscaler API Documentation](https://help.zscaler.com/zia/api)
- [Sandbox Report API](https://help.zscaler.com/zia/sandbox-report-api)
- [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
- [Microsoft Sentinel Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)
