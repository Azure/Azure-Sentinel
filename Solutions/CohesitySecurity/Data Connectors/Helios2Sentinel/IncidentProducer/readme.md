# IncidentProducer Azure Function
This function retrieves the ransomware alerts from Cohesity Data Cloud and adds them in the queue for further processing and storing in the Mcirosoft Sentinel Incident table.

## Publish Azure Function
Run [this](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/azuredeploy.json.sh) script to create configuration and deploy the function application to Microsoft Azure.

**Note:** You can ignore **Publish Azure Function** section if you've already run the script for deploying another Cohesity function application. 

## Testing
Check that the function successfully runs at  _``Your function name that starts from cohesitypro`` | Functions | Monitor_. Each successfull run should have the same  log-message. If not, you can refer to the Troubleshooting section for tips.

## Troubleshooting
1. If the function fails due to expiry of your Cohesity Data Cloud API key, then you must create a new API key. Follow the steps below.
* Go to the Cohesity Data Cloud [login page](https://helios.cohesity.com/login).
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_. The API Key Token is displayed.
2. If you're not receiving new incidents, then ensure that you created your Microsoft Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel) and specified it correctly in the _Workspace_ environment variable.
* __Attention__: It should be the same workspace as created for [IncidentConsumer](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer#readme).
3. If this function receives incidents but it's not listed in the Microsoft Sentinel Incidents table, then ensure that you have a valid queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps to create a queue](https://learn.microsoft.com/azure/storage/queues/storage-quickstart-queues-portal)) and the path is correctly specified in the _AzureWebJobsStorage_ environment variable.
* __Attention__: It should be the same queue as created for [IncidentConsumer](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer#readme).
4. If it's the first run, how many days of historical events would you like to get? If you're ok to see a blank table until you get a new alert, then skip this recommendation. If not, then Cohesity recommends to set the _startDaysAgo_ variable to _-30_. This means that you'll get all alerts that happened for last 30 days. If you set it to 0, then you'll get only new alerts.
5. Validate if all environment variables are set correctly. To validate, compare their names with the ones in [local.settings.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer/local.settings.json).
6. If you changed any of the environment variables, COhesity highly recommends restarting the function.
* Go to the _Overview_ blade of the IncidentProducer function.
* Select _Restart_.
* Confirm the restart.
