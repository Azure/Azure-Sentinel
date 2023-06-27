# Function app manual deployment instructions 

1.Deploy a Function App

NOTE: You will need to [prepare VS code](https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-python#prerequisites) for Azure function development.

Download the [Azure Function App](https://aka.ms/sentinel-SlackAuditAPI-functionapp) file. Extract archive to your local development computer.
Start VS Code. Choose File in the main menu and select Open Folder.
Select the top level folder from extracted files.
Choose the Azure icon in the Activity bar, if you aren't already signed in, choose the Azure icon in the Activity bar, then in the Azure: Functions area, choose Sign in to Azure
If you're already signed in, go to the next step.
Provide the following information at the prompts:

a. **Select folder**: Choose a folder from your workspace or browse to one that contains your function app.

b. **Select Subscription**: Choose the subscription to use under resources.

c. Right click on the functions and select **Create new Function App in Azure** (Don't choose the Advanced option)

d. **Enter a globally unique name for the function app**: Type a name that is valid in a URL path. The name you type is validated to make sure that it's unique in Azure Functions. (e.g. UmbrellaXYZ).

e. **Select a runtime**: Choose Python 3.8.

f. Select a location for new resources. For better performance and lower costs choose the same [region](https://azure.microsoft.com/regions/) where Microsoft Sentinel is located.

Deployment will begin. A notification is displayed after your function app is created.

Deploy the function in Function app: Once the function app is created click on deploy button under workspace section. Select the Subcription and the function app in which function needs to be deployed.

Go to Azure Portal for the Function App configuration.