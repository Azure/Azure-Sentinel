# Deploy a Function App for collecting Zoom data into Azure Sentinel
This function app will listen for Zoom API events and will write them to Log Analyitcs on arrival.

### Deploy the Function App
The easiest way is via the provided ARM templates:

#### 1: Deploy via Azure ARM Template
1.  Deploy the template.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FZoom%2Fazuredeploy.json)

2. Deploy permissions for the function to the Key Vault.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FZoom%2Fazuredeploy_kv.json)

Alternatively you can deploy the elements manually.
#### 2: Deploy via VS Code
Note: You will need to prepare VS code for Azure function development.  See https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-powershell#prerequisites
1. Download the [Zip](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Zoom/zoom_logs_template.zip?raw=true) file of the Azure Funciton app from Github.
2. Extract to a location on your local host.
3. Open VS Code.
4. Click File -> Open Folder.
5. Select the top level folder from extracted files.
6. Type Crtl+Shift+P.
7. Click Azure Functions: Deploy to function app.  You maybe asked to sign in to Azure.
8. Click Create New function app in Azure (advanced).
9. Provide a unique name like "ZoomLogs". Press Enter.
10. Click Windows.
11. Click Consumption.
12. Click PowerShell.
13. Click Create new Resource Group.
14. Press enter to accept the name.
15. Click Create a new storage Account.
16. Press enter to accept the name.
17. Click Create new Application Insights resource.
18. Press enter to accept the name.
19. Pick a location to deploy in.
20. Deployment will begin.
21. Wait for the deployment to complete, then click upload settings in the bottom right.
22. Click yes to all to upload.
23. Go to the Azure Portal.
24. Go to the resource group that was created.  Click the Function.
25. Click Stop.
26. Click Platform Features Tab.
27. Click Identity.
28. Click On under system assigned.  Click Save.  Click Yes.

### Create a Key Vault
1. Go to the Azure Portal.
2. Go to the resource group that was created.  Click Add.
3. Type Key Vault.
4. Create a Key vault.
5. Go to the resource created.
6. Click Access Policies.
7. Click Add Access Policy.
8. Select Secret Management from Configure from template.
9. Click Select Principal.
10. Search for the name of the function app.  Click Select.
11. Click Add.
12. Click Save.
13. Click Secrets.
14. Click Generate.
15. Enter WorkspaceKey. Paste in your Azure Sentinel Workspace Key. Click Create.
16. Click Generate.
17. Click WorkspaceKey and copy the current version string to a temporary location.

### Configure Settings for the Function
1. Go to the Azure Portal.
2. Go to the resource group that was created. Click the Function.
3. Click Platform Features Tab.
4. Click Configuration under General.
5. Click edit next to workspaceKey.
6. Update the value using the string copied from KeyVault.
* @Microsoft.KeyVault(SecretUri=https://<dnsname>/secrets/workspaceKey/<versionstring>)
7. Click Ok.
8. Click edit next to workspaceId.
9. Update the value with your Sentinel Workspace Id.
10. Click Ok.
11. Click Save.

## Configure your Zoom API app.
You also need to configure your Zoom account to sent events to your Function App. To do this go to https://marketplace.zoom.us/ and log in with a user who has admin access to your Zoom account.
1. Select ‘Develop’ in the top right hand corner and click ‘Build App’. 
2. Select ‘Webhook Only’ as your app type. 
3. Give your app a name.
4. Fill out the required Basic Information and click continue. 
5. Under the Feature Tab enable the ‘Event Subscriptions’ toggle and click ‘Add new event subscription’. 
6. Set a subscription name and in the Event notification endpoint URL enter your Function App URL. This will be in the format of https://<FunctionAppName>.azurewebsites.net/api/<FunctionName>. You can find this you app URL in the Azure Portal.  
7. Click ‘Add Events’ and select the events you want to receive in Azure Sentinel. Then click done. 
8. Copy your feature Verification token for your event subscription and save it. 
9. Click ‘Save’ and ‘Continue’. 

Once you have done this you need to add your verification code to your previously deployed Function App. To do this go to the Function App in the Azure Portal.
1. Click Platform Features Tab.
2. Click Configuration under General.
3. Click Edit next to ZoomVerification.
4. Enter your Zoom app's verification token.
5. Restart your function app.

If sucessfully deployed you should start to see events appear in your Azure Sentinel workpsace as soon as they are generated.
If you run into issues there are a number of options for [monitoring](https://docs.microsoft.com/en-us/azure/azure-functions/functions-monitoring?tabs=cmd) and [deugging](https://docs.microsoft.com/en-us/azure/azure-functions/functions-debug-powershell-local) your Function App.