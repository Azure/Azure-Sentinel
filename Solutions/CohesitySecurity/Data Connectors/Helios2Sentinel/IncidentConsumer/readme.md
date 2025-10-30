# IncidentConsumer Azure Function
This function picks alerts from the queue and creates the corresponding records in the Microsoft Sentinel Incident table.

## Publish the Azure Function
Run [this](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/azuredeploy.json.sh) script to create configuration and deploy the function applications to Azure.

**Note:** You can ignore the **Publish the Azure Function** section if you've already run the script for deploying another Cohesity function app.

## Testing
Check that the function successfully runs at  _``Your function name that starts from cohesitycon`` | Functions | Monitor_. Each successfull run should have the same  log-message. If not, then see the Troubleshooting section for tips.

## Troubleshooting
1. If the function fails due to expiry of API key on your Cohesity Data Cloud API, then you must create another API key. Follow the steps below.
* Go to the Cohesity Data Cloud [login page](https://helios.cohesity.com/login).
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_. The API Key Token is displayed.
2. If you're not seeing new incidents in your workspace, then ensure that you created your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel) and specified it correctly in the _Workspace_ environment variable.
* __Attention__: It should be the same workspace as created for [IncidentProducer](https://github.com/Azure/Azure-Sentinel/edit/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer/readme.md).
3. If this function receives incidents but they are not listed in the Microsoft Sentinel Incidents table, then ensure that you have a valid queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps to create a queue](https://learn.microsoft.com/azure/storage/queues/storage-quickstart-queues-portal)) and the path is correctly specified in the _AzureWebJobsStorage_ environment variable.
* __Attention__: It should be the same queue as created for [IncidentProducer](https://github.com/Azure/Azure-Sentinel/edit/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer/readme.md).
4. Ensure that all environment variables are set correctly. To validate, you can compare their names with the ones in [local.settings.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer/local.settings.json).
5. If you changed any of the environment variables, Cohesity highly recommends you to restart the function. Follow the steps below.
* Go to the _Overview_ blade of the IncidentProducer function.
* Select _Restart_.
* Confirm the restart.
6. If your function application fails to authenticate for creating records in the Microsoft Sentinel Incidents table, then [re-register](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) the client application in Microsoft Azure Active Directory with AzureStorage.user_impersonation permission. For more information, see these [steps](https://learn.microsoft.com/azure/healthcare-apis/register-application). Also, make sure that the client application is assigned the _Microsoft Sentinel Contributor_ role in the appropriate subscription.
* Save _Application (client) ID_, _Directory (tenant) ID_, and _Secret Value_ in your [KeyVault](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.KeyVault%2Fvaults) with the secret names _ClientId_, _ClientKey_, and _TenantId_.
