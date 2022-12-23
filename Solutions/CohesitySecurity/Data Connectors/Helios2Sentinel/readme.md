# Azure Functions
This solution requires deploying two Azure functions - one for receiving alerts and another one for creating Sentinel incidents.
Before deployment, please make sure that all prerequisites and pre-deployment steps are done correctly.

## Prerequisites
* _(Recommendation)_ Get access to [Visual Studio](https://visualstudio.microsoft.com/vs/community/) or [Visual Studio Code](https://code.visualstudio.com/).
* Install [dotnet core](https://dotnet.microsoft.com/download/dotnet-core).
* Install [azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest).
* Install [azure-functions-core-tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local).

## Deployment
* Deploy configurations [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FData%2520Connectors%2FHelios2Sentinel%2Fazuredeploy.json)
* Deploy [IncidentProducer](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentProducer#readme) function.
* Deploy [IncidentConsumer](https://github.com/cohesity/Azure-Sentinel/tree/CohesitySecurity.internal/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/IncidentConsumer#readme) function.
