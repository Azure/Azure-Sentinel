# Zscaler OAuth2 Block IP Playbook

This playbook enables automated IP blocking in Zscaler Internet Access (ZIA) when triggered by Microsoft Sentinel incidents. It uses OAuth2 authentication to securely communicate with the Zscaler API and add malicious IP addresses to a designated block category.

## Overview

The Zscaler-Oauth2-BlockIP playbook is designed to:

- Automatically extract IP entities from Microsoft Sentinel incidents
- Authenticate with Zscaler ZIA using OAuth2 via the authentication playbook
- Add malicious IP addresses to a specified Zscaler URL category for blocking
- Process multiple IPs sequentially to ensure reliable API communication

## Prerequisites

Before deploying this playbook, ensure you have:

1. A Zscaler Internet Access (ZIA) subscription with API access enabled
2. The **Zscaler-Oauth2-Authentication** playbook deployed in the same resource group
3. OAuth2 client credentials (Client ID and Client Secret) configured in Azure Key Vault
4. A block category created in Zscaler (default: "OTHER_MISCELLANEOUS")
5. Appropriate permissions to deploy Azure Logic Apps

## Deployment

Click the button below to deploy the Zscaler-Oauth2-BlockIP playbook to your Azure environment:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2BlockIP%2Fazuredeploy.json)

## Post-Deployment Configuration

After deployment, complete the following steps:

1. **Authorize API Connections**
   - Navigate to the Logic App in the Azure portal
   - Go to API connections and authorize the Microsoft Sentinel connection
   - Ensure the managed identity has appropriate permissions

2. **Grant Required Permissions**
   - Assign the Logic App managed identity the "Microsoft Sentinel Responder" role on your workspace
   - Verify the Zscaler-Oauth2-Authentication playbook is deployed and accessible

3. **Configure Block Category** (Optional)
   - The default category is "OTHER_MISCELLANEOUS"
   - Update the parameter during deployment if you use a different category

4. **Configure Zscaler Admin URL** (Optional)
   - The default is "https://admin.zscaler.net"
   - Update the parameter for your Zscaler cloud instance

5. **Configure Automation Rules**
   - Create automation rules in Microsoft Sentinel to trigger this playbook
   - Configure rules to run on incidents containing IP entities

## Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| PlaybookName | Name of the Logic App | Zscaler-Oauth2-BlockIP |
| Zscaler OAuth2 Authentication Playbook | Name of the OAuth2 authentication playbook | Zscaler-Oauth2-Authentication |
| Zscaler Admin Url | Your Zscaler admin portal URL | https://admin.zscaler.net |
| Block Category | Zscaler URL category for blocking | OTHER_MISCELLANEOUS |

## Workflow

1. Triggered by Microsoft Sentinel incident creation
2. Extracts IP entities from the incident
3. Calls the Zscaler-Oauth2-Authentication playbook to obtain an access token
4. For each IP address, adds it to the configured Zscaler URL category using the API
5. IPs are processed sequentially (concurrency set to 1) for reliable execution

## Learn More

- [Zscaler API Documentation](https://help.zscaler.com/zia/api)
- [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
- [Microsoft Sentinel Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)
