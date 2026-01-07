# Zscaler OAuth2 Blacklist URL Playbook

This playbook enables automated URL blocking in Zscaler Internet Access (ZIA) when triggered by Microsoft Sentinel incidents. It uses OAuth2 authentication to securely communicate with the Zscaler API and add malicious URLs to a designated block category.

## Overview

The Zscaler-Oauth2-BlacklistURL playbook is designed to:

- Automatically extract URL entities from Microsoft Sentinel incidents
- Authenticate with Zscaler ZIA using OAuth2 via the authentication playbook
- Add malicious URLs to a specified Zscaler block category
- Add comments to incidents documenting the remediation actions taken

## Prerequisites

Before deploying this playbook, ensure you have:

1. A Zscaler Internet Access (ZIA) subscription with API access enabled
2. The **Zscaler-Oauth2-Authentication** playbook deployed in the same resource group
3. OAuth2 client credentials (Client ID and Client Secret) configured in Azure Key Vault
4. A block category created in Zscaler (e.g., "OTHER_MISCELLANEOUS" or a custom category)
5. Appropriate permissions to deploy Azure Logic Apps

## Deployment

Click the button below to deploy the Zscaler-Oauth2-BlacklistURL playbook to your Azure environment:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2BlacklistURL%2Fazuredeploy.json)

## Post-Deployment Configuration

After deployment, complete the following steps:

1. **Authorize API Connections**
   - Navigate to the Logic App in the Azure portal
   - Go to API connections and authorize the Microsoft Sentinel connection
   - Ensure the managed identity has appropriate permissions

2. **Grant Required Permissions**
   - Assign the Logic App managed identity the "Microsoft Sentinel Responder" role
   - Verify the authentication playbook is accessible from this playbook

3. **Configure Zscaler Block Category**
   - Verify the block category specified during deployment exists in Zscaler
   - To change the category, edit the playbook and update the category variable

4. **Configure Automation Rules**
   - Create automation rules in Microsoft Sentinel to trigger this playbook
   - Configure rules to run on incidents containing URL entities

## Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| PlaybookName | Name of the Logic App | Zscaler-Oauth2-BlacklistURL |
| Zscaler Authentication Playbook | Name of the OAuth2 authentication playbook | Zscaler-Oauth2-Authentication |
| Zscaler Admin URL | Your Zscaler admin portal URL | https://admin.zscaler.net |
| Block Category | Zscaler URL category for blocking | OTHER_MISCELLANEOUS |

## Learn More

- [Zscaler API Documentation](https://help.zscaler.com/zia/api)
- [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
- [Microsoft Sentinel Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)
