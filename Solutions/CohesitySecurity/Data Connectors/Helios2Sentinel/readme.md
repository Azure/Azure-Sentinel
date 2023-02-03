# Azure Functions
This solution uses Microsoft Azure functions requires to receive alerts and create Microsoft Sentinel incidents. You have to deploy the Azure functions.
Before deployment, please make sure that all prerequisites are done correctly.

## Prerequisites
* _(Recommendation)_ Get access to [Visual Studio](https://visualstudio.microsoft.com/vs/community/) or [Visual Studio Code](https://code.visualstudio.com/) in case later you decide to change the code for your environment.
* Install [dotnet core](https://dotnet.microsoft.com/download/dotnet-core).
* Install [azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest).
* Install [azure-functions-core-tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local).

## Deployment
Click on the "Deploy to Azure" button to deploy the Azure functions. This step directs you to deploy an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FData%2520Connectors%2FHelios2Sentinel%2Fazuredeploy.json)
