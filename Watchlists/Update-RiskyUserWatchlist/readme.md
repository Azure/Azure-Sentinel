#  Update-RiskyUserWatchlist

Author: Jhonny Paulino, Nathan Swift

This Logic App will run weekly and create/update a Risky User watchlist with users from Microsoft Defender for cloud app with additional data for threatscore, information, and a url.

**Prerequisites for the solution**:

1. You must create a Azure AD Service Principal, record the AppId, tenantID, and create a secrets and record the secret. This service principal will be used in the solution to query the Defender for Cloud App /entities rest api

2. Be sure to add the following 'Microsoft Cloud App Security' Application Permissions to the created service principal discovery.read, investigation.read . Also be sure to grant admin consent to those application permissions.

**Deploying the solution**:

1. Add/Update the missing parameters in the ARM template deployment 
   The Watchlist name will be also the alias name that you will use to query the data, for example 

      _GetWatchlist(**'cloudappriskyusers'**)
	  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FWatchlists%2FUpdate-RiskyUserWatchlist%2Fazuredeploy.json)


**Post Deployment**:

1. Manually check/update the Key Vault secret called 'cloudapplist' with the Azure AD Service Principal key

   The Logic App as a Managed Service Indetity - MSI needs to have the following RBAC Roles:

2. Key Vault Secrets User on the deployed Key Vault resource.
This is required for obtaining the AAD SPN secret key encrypted through Logic App.

3. Azure Sentinel Contributor Role on the Azure Sentinel Resource Group.
This is required for deleting and updating the watchlist in Microsoft Sentinel.