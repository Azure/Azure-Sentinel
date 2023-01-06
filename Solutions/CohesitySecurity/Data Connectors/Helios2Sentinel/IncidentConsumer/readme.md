# IncidentConsumer Azure Function
This function picks alerts from the queue and creates the corresponding records in the Sentinel Incident table.

## Publish the Azure Function
Run [this](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/azuredeploy.json.sh) script to create configuration and deploy the function apps to Azure.

**Note:** You don't need to do it if you've already run the script for deploying another Cohesity function app.

## Testing
Check that the function successfully runs at  _``Your function name that starts from cohesitycon`` | Functions | Monitor_. Each successfull run should have the corresponding log-message. If not, please see the Troubleshooting section for tips.

## Troubleshooting
1. If the function fails because your DataHawk (Helios) API key expired, get your new key by following these steps
* Go to the Cohesity DataHawk (Helios) [login page](https://helios.cohesity.com/login).
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_. The API Key Token is displayed.
2. If you're not seeing new incidents in your workspace, make sure that you created your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel) and also specified it correctly in the _Workspace_ environment variable.
* __Attention__: It should be the same workspace as created for [IncidentProducer](https://github.com/cohesity/Azure-Sentinel/edit/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer/readme.md).
3. If this function receives incidents but they don't get into the Sentinel Incidents table, make sure that you have a valid queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps to create a queue](https://learn.microsoft.com/azure/storage/queues/storage-quickstart-queues-portal)) and the path is correctly specified in the _AzureWebJobsStorage_ environment variable.
* __Attention__: It should be the same queue as created for [IncidentProducer](https://github.com/cohesity/Azure-Sentinel/edit/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer/readme.md).
4. Check that all environment variables are set correctly by comparing their names with the ones in [local.settings.json](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer/local.settings.json).
5. If you changed any of the environment variables, we highly recommend restarting the function after that.
* Go to the _Overview_ blade of the IncidentProducer function.
* Press _Restart_.
* Confirm the restart.
6. If your function app fails to authenticate to create records in the Sentinel Incidents table, then [re-register](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) a client application in Azure Active Directory with the Contributor privileges ([steps](https://learn.microsoft.com/azure/healthcare-apis/register-application)).
* Save _Application (client) ID_, _Directory (tenant) ID_ and _Secret Value_ in your [KeyVault](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults) with the secret names _ClientId_, _ClientKey_, _TenantId_.
