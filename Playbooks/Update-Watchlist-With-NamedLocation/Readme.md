# Update-Watchlist-With-NamedLocation


author: Maria de Sousa-Valadas
version: 1.0


This Logic App runs on a scheduled basis (every 7 days by default) and checks if new IP ranges have been added to your Named Location. If there are new IP ranges, they will be added to your preexisting Azure Sentinel Watchlist, which you can then use in queries, analytics, hunting queries, etc. for correlation.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-Watchlist-With-NamedLocation%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-Watchlist-With-NamedLocation%2Fazuredeploy.json)

 
## Pre-requisites
1.	Create a [Named Location](https://docs.microsoft.com/azure/active-directory/conditional-access/location-condition) to store the IP ranges you want to add to your Watchlist. You will need the ID of the Named Location in the Logic App. To check the ID, you can use the [Get-AzureADMSNamedLocationPolicy](https://docs.microsoft.com/powershell/module/azuread/get-azureadmsnamedlocationpolicy?view=azureadps-2.0) PowerShell command or use the Graph API ([List namedLocations API call](https://docs.microsoft.com/powershell/module/azuread/get-azureadmsnamedlocationpolicy?view=azureadps-2.0))
2.	Create a Watchlist with one column called "ip_range". If you use a different name, you can edit the step *Watchlists  Add a new watchlist* item to specify the right name.
3.	Set up a service principal to call the Named Locations API and create a secret for it:
    a.	On Azure AD, create an app registration on Azure Active Directory. Under API Permissions > Add a permission > Microsoft Graph > Application permission and select **Policy.Read.All**. Select Grant admin consent for your tenant (must be done by a Global Admin). This permission is required to get named locations from the Graph API (see [here](https://docs.microsoft.com/graph/api/namedlocation-get?view=graph-rest-1.0&tabs=http)).
    b.	Select the app registration you have just created, select Overview and copy the Application (client) ID, you will have to enter it as a parameter when you deploy the Logic App.  
    c.	Go to Certificates & Secrets > New client secret. Copy this secret, you will store it in your Key Vault in the next step.
4.	Create a [Key Vault](https://docs.microsoft.com/azure/key-vault/general/overview) to store your secret to the app registration you have just created (best practice)
    a.	On Key Vaults, you can either use an existing Key Vault or create a new one to store your secret.
    b.	Under Access policies, select Permission model: Azure role-based access control. Now, you can assign permissions to your Logic App to access the secret.
 
 
## Post-Deployment Configuration
1.	Grant permissions to your Logic App
    a.	Once deployed, go to the Logic App's blade and click on Identity under Settings. The System assigned managed identity should be On
    b.	Click on + Add role assignment.
    c.	To grant access to Azure Sentinel: select Resource group under Scope and select the Subscription and Resource group where the Azure Sentinel Workspace is located. Select **Azure Sentinel Contributor** (as it has to edit the Watchlist) under Role and click Save.
    d.	To grant access to Key Vault: select Resource group under Scope and select the Subscription and Resource group where the Key vault located. Select **Keyvaults Secret Users** under Role and click Save.
2.	The logic app is set to run every 7 days. You can modify the frequency on the first step.
 
 
##Configure connections:
1.	On the step "Get secret" you will need to update your connection. Select Change Connection, then Add new, and finally Connect with managed identity (preview). Fill in the information. As you have previously granted permission to the keyvault, you should be able to select the Secret.
2.	In the last step, you may need to update your connection to Azure Sentinel as well.
