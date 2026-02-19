# Zscaler OAuth2 Lookup IP Playbook

This playbook enables automated IP address classification lookup in Zscaler Internet Access (ZIA) when triggered by Microsoft Sentinel incidents. It uses OAuth2 authentication to securely query the Zscaler API and retrieve URL category information for IP addresses found in incidents.

## Overview

The Zscaler-Oauth2-LookupIP playbook is designed to:

- Automatically extract IP entities from Microsoft Sentinel incidents
- Authenticate with Zscaler ZIA using OAuth2 via the authentication playbook
- Query Zscaler's URL lookup API to retrieve classification information for each IP
- Return URL classifications and security alert categories for enrichment purposes

## Prerequisites

Before deploying this playbook, ensure you have:

1. A Zscaler Internet Access (ZIA) subscription with API access enabled
2. The **Zscaler-Oauth2-Authentication** playbook deployed in the same resource group
3. OAuth2 client credentials (Client ID and Client Secret) configured in Azure Key Vault
4. Appropriate permissions to deploy Azure Logic Apps

## Deployment

Click the button below to deploy the Zscaler-Oauth2-LookupIP playbook to your Azure environment:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2LookupIP%2Fazuredeploy.json)

## Post-Deployment Configuration

After deployment, complete the following steps:

1. **Authorize API Connections**
   - Navigate to the Logic App in the Azure portal
   - Go to API connections and authorize the Microsoft Sentinel connection
   - Ensure the managed identity has appropriate permissions

2. **Grant Required Permissions**
   - Assign the Logic App managed identity the "Microsoft Sentinel Responder" role on your workspace
   - Verify the Zscaler-Oauth2-Authentication playbook is deployed and accessible

3. **Configure Zscaler API URL** (Optional)
   - The default Base URL is "zsapi.zscaler.net/api/v1"
   - To change, edit the playbook and update the "Initialize_variable" action for BaseURL

4. **Configure Automation Rules**
   - Create automation rules in Microsoft Sentinel to trigger this playbook
   - Configure rules to run on incidents containing IP entities

## Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| PlaybookName | Name of the Logic App | Zscaler-Oauth2-LookupIP |

## Workflow

1. Triggered by Microsoft Sentinel incident creation
2. Extracts IP entities from the incident
3. Initializes the Zscaler API Base URL variable
4. Calls the Zscaler-Oauth2-Authentication playbook to obtain an access token
5. For each IP address, queries the Zscaler URL lookup API (`/urlLookup`)
6. Parses the response containing:
   - `url`: The queried IP address
   - `urlClassifications`: Array of URL category classifications
   - `urlClassificationsWithSecurityAlert`: Security-related classifications
7. IPs are processed sequentially (concurrency set to 1) for reliable execution

## Learn More

- [Zscaler API Documentation](https://help.zscaler.com/zia/api)
- [URL Lookup API](https://help.zscaler.com/zia/url-lookup)
- [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
- [Microsoft Sentinel Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)
