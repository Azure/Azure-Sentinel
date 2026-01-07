# Zscaler OAuth2 Whitelist URL Playbook

This playbook enables automated addition of URLs to the Zscaler Internet Access (ZIA) security whitelist when triggered by Microsoft Sentinel incidents. It uses OAuth2 authentication to securely communicate with the Zscaler API and add URLs to the allow list while preserving existing whitelist entries.

## Overview

The Zscaler-Oauth2-WhitelistURL playbook is designed to:

- Automatically extract URL entities from Microsoft Sentinel incidents
- Authenticate with Zscaler ZIA using OAuth2 via the authentication playbook
- Retrieve the existing URL whitelist to preserve current entries
- Merge new URLs with the existing whitelist
- Update the security policy with the combined whitelist

## Prerequisites

Before deploying this playbook, ensure you have:

1. A Zscaler Internet Access (ZIA) subscription with API access enabled
2. The **Zscaler-Oauth2-Authentication** playbook deployed in the same resource group
3. OAuth2 client credentials (Client ID and Client Secret) configured in Azure Key Vault
4. Appropriate permissions to deploy Azure Logic Apps

## Deployment

Click the button below to deploy the Zscaler-Oauth2-WhitelistURL playbook to your Azure environment:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2WhitelistURL%2Fazuredeploy.json)

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
   - The default Base URL is "zsapi.zscalertwo.net/api/v1"
   - To change, edit the playbook and update the "Define_Base_URL" action for your Zscaler cloud instance

4. **Configure Automation Rules**
   - Create automation rules in Microsoft Sentinel to trigger this playbook
   - Configure rules to run on incidents containing URL entities that should be whitelisted

## Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| PlaybookName | Name of the Logic App | Zscaler-Oauth2-WhitelistURL |

## Workflow

1. Triggered by Microsoft Sentinel incident creation
2. Initializes temporary variables and empty URL collection array
3. Extracts URL entities from the incident
4. For each URL entity, parses and appends to the collection array
5. Initializes the Zscaler API Base URL variable
6. Calls the Zscaler-Oauth2-Authentication playbook to obtain an access token
7. Retrieves the existing whitelist via GET request to `/security`
8. Parses existing whitelist URLs and appends to the collection (if not null)
9. Deduplicates the combined URL list using union operation
10. Joins all URLs into a comma-separated format
11. Constructs the JSON request body with the whitelistUrls array
12. Updates the security policy via PUT request to `/security` with the merged whitelist

## Learn More

- [Zscaler API Documentation](https://help.zscaler.com/zia/api)
- [Security Policy Settings API](https://help.zscaler.com/zia/security-policy-settings)
- [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
- [Microsoft Sentinel Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)
