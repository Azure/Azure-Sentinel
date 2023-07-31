# Function app manual deployment instructions 

- Start VS Code. Choose File in the main menu and select Open Folder.

- Select the top level folder from extracted files.

- Choose the Azure icon in the Activity bar, if you aren't already signed in, choose the Azure icon in the Activity bar, then in the Azure: Functions area, choose Sign in to Azure

- If you're already signed in, go to the next step.

- Provide the following information at the prompts:

	a. **Select folder**: Choose a folder from your workspace or browse to one that contains your function app.

	b. **Select Subscription**: Choose the subscription to use under resources.
	
	(https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/subscription.png)

	c. Right click on the functions and select **Create new Function App in Azure** (Don't choose the Advanced option)

	(https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/CreatenewFunctionApp.png)

	d. **Enter a globally unique name for the function app**: Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. UmbrellaXYZ).
	
	(https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/globallyuniquename.png)

	e. **Select a runtime**: Choose Python 3.8.

	(https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/Selectaruntime.png)

	f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

	(https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/Selectalocation.png)

- Deployment will begin. A notification is displayed after your function app is created.

- Deploy the function in Function app: Once the function app is created click on deploy button under workspace section. Select the Subcription and the function app in which function needs to be deployed.
(https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/Deploythefunction.png)

- Go to Azure Portal for the Function App configuration. 