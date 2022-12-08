# IncidentConsumer Azure Function
This function picks alerts from the queue and creates the corresponding records in the Sentinel Incident table.

## Publishing Prerequisites
1. Create your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel).
* __Attention__: It should be the same workspace as created for [IncidentProducer](https://raw.githubusercontent.com/cohesity/Azure-Sentinel/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/readme.md).
2. [Register](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) a client application in Azure Active Directory with the Contributor privileges ([steps](https://learn.microsoft.com/en-us/azure/healthcare-apis/register-application)).
* Save _Application (client) ID_, _Directory (tenant) ID_ and _Secret Value_.
3. Create a new queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps](https://learn.microsoft.com/en-us/azure/storage/queues/storage-quickstart-queues-portal)).
* __Attention__: It should be the same queue as created for [IncidentProducer](https://raw.githubusercontent.com/cohesity/Azure-Sentinel/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/readme.md).
* Save the connection string
4. Choose your [resource group](https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups) that you are going to use for the function app.
5. Choose your [subscription](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade) that you are going to use for the function app.

## Publish the Azure Function
* You can publish an Azure Function with Visual Studio ([steps](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-vs?tabs=in-process#publish-to-azure)) or Visual Studio Code ([steps](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#publish-to-azure)).
* Alternatively, you can do it from the command line. An important note on using the following commands, the Azure Function version must match what is defined in your codebase. Visual Studio will prompt to upgrade the function if this is different, the command below may not.
Run the following commands
``az login``
followed by
``func azure functionapp publish IncidentConsumer --csharp --force``

## Post Publishing Steps
1. In the [Function App](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp) window choose IncidentConsumer.
2. Click on _Configuration_ to see the _IncidentConsumer | Configuration_ window.
3. Set the following parameters in the _Application Settings_ tab to the corresponding values you created in the __Publishing Prerequisites__ above. If you don't see one of these settings, then press the _+New Application Setting_ button and create it ([details](https://learn.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal)). 
* _AzureWebJobsStorage_: The queue connection string.
* _workspace_: Your workspace name.
* _ClientId_: Your client id from your registered app.
* _ClientKey_:  Your client key (secret) from your registered app.
* _TenantId_:  Your tenant id (secret) from your registered app.
* _resourceGroup_: Your [resource group](https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups). 
* _subscription_: Your [subscription](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade).
4. Restart the Azure Function.
* Go to the _Overview_ blade of the _IncidentConsumer_ function.
* Press _Restart_.
* Confirm the restart.

## Testing
Check that the function successfully runs at  _IncidentConsumer | Functions | Monitor_.
