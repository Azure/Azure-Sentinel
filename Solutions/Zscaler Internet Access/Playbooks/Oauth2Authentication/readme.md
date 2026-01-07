# Zscaler OAuth2 Authentication Playbook

This playbook provides OAuth2 authentication capabilities for Zscaler Internet Access (ZIA) integration with Microsoft Sentinel. It handles the authentication flow required to obtain and manage access tokens for secure API communication with Zscaler services.

## Overview

The Zscaler-Oauth2-Authentication playbook is designed to:

- Authenticate with Zscaler ZIA using OAuth2 credentials
- Obtain and refresh access tokens automatically
- Provide secure credential management through Azure Key Vault
- Enable other Zscaler playbooks to leverage centralized authentication

## Prerequisites

Before deploying this playbook, ensure you have:

1. **Zscaler Configuration**
   - A Zscaler Internet Access (ZIA) subscription with API access enabled
   - An Azure AD application registration for OAuth2 authentication
   - OAuth2 client credentials from Azure AD:
     - Client ID (Application ID)
     - Client Secret
     - Tenant ID

2. **Azure Resources**
   - An existing Azure Key Vault
   - The client secret stored in Key Vault with the name `client-secret`
   - Appropriate permissions to deploy Azure Logic Apps and modify Key Vault access policies

3. **Required Information**
   - OAuth2 Scope (typically `api://[your-app-id]/.default`)
   - Azure AD Tenant ID
   - Key Vault name

## Deployment

### Option 1: Deploy via Microsoft Sentinel Content Hub (Recommended)

When deploying the full Zscaler solution from Content Hub, you will see an **Authentication Configuration** step where you need to provide:

1. **Key Vault Name**: The name of your Azure Key Vault containing the client secret
2. **OAuth2 Client ID**: Your Azure AD Application ID (GUID format)
3. **OAuth2 Scope**: The scope for token requests (e.g., `api://166a33fa-7009-42ad-bf3b-1f6fcffb6395/.default`)
4. **Azure AD Tenant ID**: Your Azure AD tenant ID (GUID format)

These parameters will automatically configure the OAuth2 Authentication Logic App during deployment.

### Option 2: Deploy Standalone Playbook

Click the button below to deploy only the Zscaler-Oauth2-Authentication playbook:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FZscaler%2520Internet%2520Access%2FPlaybooks%2FOauth2Authentication%2Fazuredeploy.json)

When deploying standalone, you'll need to provide the same parameters during deployment.

## Post-Deployment Configuration

After deployment, complete these steps:

### 1. Store Client Secret in Key Vault

Ensure your client secret is stored in the Key Vault you specified:

```bash
az keyvault secret set \
  --vault-name <YOUR_KEYVAULT_NAME> \
  --name client-secret \
  --value <YOUR_CLIENT_SECRET>
```

### 2. Grant Key Vault Access to Logic App

The Logic App uses a system-assigned managed identity. Grant it access to read secrets:

```bash
# Get the Logic App's managed identity object ID
LOGIC_APP_IDENTITY=$(az logic workflow show \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --name Zscaler-Oauth2-Authentication \
  --query identity.principalId -o tsv)

# Grant Key Vault Secrets User role
az role assignment create \
  --assignee $LOGIC_APP_IDENTITY \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.KeyVault/vaults/<KEYVAULT_NAME>
```

Alternatively, use the Azure Portal:
1. Navigate to your Key Vault
2. Go to **Access control (IAM)**
3. Click **Add role assignment**
4. Select **Key Vault Secrets User** role
5. Assign access to the **Zscaler-Oauth2-Authentication** Logic App

### 3. Verify Configuration

Test the authentication by manually running the Logic App:

1. Open the Logic App in the Azure Portal
2. Click **Run Trigger** → **Manual**
3. Check the run history to verify successful OAuth2 token retrieval
4. The response should contain an `access_token`

## Troubleshooting

### Common Issues

**"Parameter value missing" error in Key Vault connection**
- Ensure the Key Vault name was provided during deployment
- For existing deployments, update the connection:
  ```bash
  az resource update \
    --ids "/subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Web/connections/Keyvault-Zscaler-Oauth2-Authentication" \
    --set properties.alternativeParameterValues.vaultName="<KEYVAULT_NAME>"
  ```

**"Forbidden" error when accessing Key Vault**
- Verify the Logic App's managed identity has the "Key Vault Secrets User" role
- Check that the secret `client-secret` exists in the Key Vault

**OAuth2 token request fails**
- Verify the Client ID, Tenant ID, and Scope are correct
- Ensure the client secret in Key Vault is valid
- Check that the Azure AD application has the required API permissions

