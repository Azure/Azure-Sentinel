# IncidentProducer Azure Function
This function retrieves ransomware alerts from Cohesity DataHawk and lands them in the queue for further processing and storing in the Sentinel Incident table.

## Publish Azure Function
Run [this](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/azuredeploy.json.sh) script to create configuration and deploy the function apps to Azure.

**Note:** You don't need to do it if you've already run the script for deploying another Cohesity function app. 

## Testing
Check that the function successfully runs at  _``Your function name that starts from cohesitypro`` | Functions | Monitor_. Each successfull run should have the corresponding log-message. If not, please see the Troubleshooting section for tips.

## Troubleshooting
1. If the function fails because your DataHawk (Helios) API key expired, get your new key by following these steps
* Go to the Cohesity DataHawk (Helios) [login page](https://helios.cohesity.com/login).
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_. The API Key Token is displayed.
2. If you're not receiving new incidents, make sure that you created your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel) and also specified it correctly in the _Workspace_ environment variable.
* __Attention__: It should be the same workspace as created for [IncidentConsumer](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer#readme).
3. If this function receives incidents but they don't get into the Sentinel Incidents table, make sure that you have a valid queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps to create a queue](https://learn.microsoft.com/azure/storage/queues/storage-quickstart-queues-portal)) and the path is correctly specified in the _AzureWebJobsStorage_ environment variable.
* __Attention__: It should be the same queue as created for [IncidentConsumer](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer#readme).
4. If it's the first run, how many days of historical events would you like to get? If you're ok to see a blank table until you get a new alert, then skip this recommendation. If not, then we recommend to set the _startDaysAgo_ variable to _-30_ meaning that you'll get all alerts that happened between 30 days ago and now. If you set it to 0, then you'll get only new alerts.
5. Check that all environment variables are set correctly by comparing their names with the ones in [local.settings.json](https://github.com/cohesity/Azure-Sentinel/blob/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer/local.settings.json).
6. If you changed any of the environment variables, we highly recommend restarting the function after that.
* Go to the _Overview_ blade of the IncidentProducer function.
* Press _Restart_.
* Confirm the restart.
