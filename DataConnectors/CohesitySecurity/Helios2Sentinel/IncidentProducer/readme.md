# IncidentProducer Azure Function
This function retrieves ransomware alerts from Cohesity DataHawk and lands them in the queue for further processing and storing in the Sentinel Incident table.

## Publishing Prerequisites
1. Get your DataHawk API key.
* Go to the Cohesity Helios [login page](https://helios.cohesity.com/login).
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_. The API Key Token is displayed.
2. Create your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel)
3. [Register](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) a client application in Azure Active Directory with the Contributor privileges ([steps](https://learn.microsoft.com/en-us/azure/healthcare-apis/register-application)).
* Save _Application (client) ID_, _Directory (tenant) ID_ and _Secret Value_.
4. Create a new queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps](https://learn.microsoft.com/en-us/azure/storage/queues/storage-quickstart-queues-portal)).
* Save the connection string
5. Create an instance of [Azure Cache for Redis](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Cache%2FRedis) ([steps](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/cache-configure))

## Publish the Azure Function
* You can publish an Azure Function with Visual Studio ([steps](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-vs?tabs=in-process#publish-to-azure)) or Visual Studio Code ([steps](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#publish-to-azure)).
* Alternatively, you can do it from the command line. An important note on using the following commands, the Azure Function version must match what is defined in your codebase. Visual Studio will prompt to upgrade the function if this is different, the command below may not.
Run the following commands
``az login``
followed by
``func azure functionapp publish IncidentProducer --csharp --force``

## Post Publishing Steps
1. In the [Function App](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp) window choose IncidentProducer.
2. Click on _Configuration_ to see the _IncidentProducer | Configuration_ window.
3. Set the following parameters in the _Application Settings_ tab to the corresponding values you created in the __Publishing Prerequisites__ above. If you don't see one of these settings, then press the _+New Application Setting_ button and create it (learn more about changing Application Settings [here](https://learn.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal)).
* _AzureWebJobsStorage_: The queue connection string.
* _apiKey_: The DataHawk API key.
* _startDaysAgo_: If it's the first run, how many days of historical events would you like to get? By default, it's set to _-30_ meaning that you'll get all alerts that happened between 30 days ago and now. If you set it to 0, then you'll get only new alerts.
* _connectStr_: The Redis cache connection string.
* _workspace_: Your workspace name.
4. Restart the Azure Function.
* Go to the Overview blade of the IncidentProducer function.
* Press _Restart_.
* Confirm the restart.

## Testing
Check that the function successfully runs at  _IncidentProducer | Functions | Monitor_.
