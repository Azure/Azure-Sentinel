# Azure Functions
This solution requires deploying two Azure functions - one for receiving alerts and another one for creating Sentinel incidents.
Before deployment, please make sure that all prerequisites and pre-deployment steps are done correctly.

## Prerequisites
* _(Recommendation)_ Get access to [Visual Studio](https://visualstudio.microsoft.com/vs/community/) or [Visual Studio Code](https://code.visualstudio.com/).
* Install [dotnet core](https://dotnet.microsoft.com/download/dotnet-core).
* Install [azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest).
* Install [azure-functions-core-tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local).

## Deployment
* Run this [script](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/azuredeploy.json.sh) to create/deploy everything for function apps.
