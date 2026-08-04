# Zscaler OAuth2 Unblock URL Playbook

This playbook enables automated removal of URLs from a Zscaler Internet Access (ZIA) block category when triggered by Microsoft Sentinel incidents. It uses OAuth2 authentication to securely communicate with the Zscaler API and remove URLs from the designated URL category.

## Overview

The Zscaler-Oauth2-UnblockURL playbook is designed to:

- Automatically extract URL entities from Microsoft Sentinel incidents
- Authenticate with Zscaler ZIA using OAuth2 via the authentication playbook
- Remove URLs from a specified Zscaler URL category
- Process multiple URLs sequentially to ensure reliable API communication

## Prerequisites

Before deploying this playbook, ensure you have:

1. A Zscaler Internet Access (ZIA) subscription with API access enabled
2. The **Zscaler-Oauth2-Authentication** playbook deployed in the same resource group
3. OAuth2 client credentials (Client ID and Client Secret) configured in Azure Key Vault
4. A URL category in Zscaler containing the URLs to be removed (default: "OTHER_MISCELLANEOUS")
5. Appropriate permissions to deploy Azure Logic Apps

## Deployment

Click the button below to deploy the Zscaler-Oauth2-UnblockURL playbook to your Azure environment:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2UnblockURL%2Fazuredeploy.json)

## Post-Deployment Configuration

After deployment, complete the following steps:

1. **Authorize API Connections**
   - Navigate to the Logic App in the Azure portal
   - Go to API connections and authorize the Microsoft Sentinel connection
   - Ensure the managed identity has appropriate permissions

2. **Grant Required Permissions**
   - Assign the Logic App managed identity the "Microsoft Sentinel Responder" role on your workspace
   - Verify the Zscaler-Oauth2-Authentication playbook is deployed and accessible

3. **Configure URL Category** (Optional)
   - The default category is "OTHER_MISCELLANEOUS"
   - To change, edit the playbook and update the "Define_URL_Category" action

4. **Configure Zscaler API URL** (Optional)
   - The default Base URL is "zsapi.zscaler.net/api/v1"
   - To change, edit the playbook and update the "Define_Base_URL" action

5. **Configure Automation Rules**
   - Create automation rules in Microsoft Sentinel to trigger this playbook
   - Configure rules to run on incidents containing URL entities that need to be unblocked

## Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| PlaybookName | Name of the Logic App | Zscaler-Oauth2-UnblockURL |

## Workflow

1. Triggered by Microsoft Sentinel incident creation
2. Extracts URL entities from the incident
3. Initializes the URL Category variable (default: OTHER_MISCELLANEOUS)
4. Initializes the Zscaler API Base URL variable
5. Calls the Zscaler-Oauth2-Authentication playbook to obtain an access token
6. For each URL, removes it from the configured Zscaler URL category using the API (`/urlCategories/{category}?action=REMOVE_FROM_LIST`)
7. URLs are processed sequentially (concurrency set to 1) for reliable execution

## Learn More

- [Zscaler API Documentation](https://help.zscaler.com/zia/api)
- [URL Categories API](https://help.zscaler.com/zia/url-categories)
- [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
- [Microsoft Sentinel Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)
