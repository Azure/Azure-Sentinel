# Update-AzureDefenderDataConnector
authors: Sean Stark, Nathan Swift

This Logic App will act as a 15min synchronizer between new Azure subscriptions created and your Azure Sentinel Azure Defender Data Connector being enabled for the new Azure subscriptions to generate Azure Defender alerts into Azure Sentinel.

**Deploy to Azure**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-AzureDefenderDataConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FUpdate-AzureDefenderDataConnector%2Fazuredeploy.json)<br>
<br>

**Additional Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to authenticate and authorize against management.azure.com to find Azure Subscriptions, Find Azure Subscriptions enabled on Azure Sentinel - Azure Defender Data Connector and updates the Azure Sentinel - Azure Defender Data Connector to enable any new subscriptions found not enabled.

Assign RBAC 'Security Reader' and 'Azure Sentinel Contributor' role to the Logic App at the Root Management Group or targeted Management Group level.

New Azure subscriptions most likely will not have microsoft.security resource provider enabled. To enable programatically you can use the custom Azure Policies found in [Azure Security Center GitHub Here:](https://github.com/Azure/Azure-Security-Center/tree/main/Pricing%20%26%20Settings/Azure%20Policy%20definitions/Azure%20Defender%20Plans) or leverage the Built In Azure Policy 'Enable Azure Security Center on your subscription' [link to Azure Portal Policy redirect here](https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2Fac076320-ddcf-4066-b451-6154267e8ad2). Be sure to assign the Azure policy at the Root Management Group or targeted Management Group level. If resource provider microsoft.security is not enabled Logic App will fail on last action 'PUT DataConnector' with a 401 Unauthorized - Access Denied.