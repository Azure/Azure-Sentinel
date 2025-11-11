# Create an Azure Function app and an ARM Template to deploy a Function App for ingesting data into Azure Sentinel
This guide provides instructions to leverage templates to create an Azure Function app and create a single-click deployment of a Azure Function App using an ARM Template. 

### Prerequisites 
- Function App files - Leverage the [Azure Function App code templates](https://aka.ms/sentinelazurefunctioncode) in either PowerShell or Python to develop the Azure Function App. Follow guidance within the template. The Azure Function app does the following and the Azure Function code template provides blocks for the following with comments/guidelines:
  - Pull logs from your <PROVIDER NAME APPLIANCE NAME> API
  - Transform the data logs into a Azure Sentinel acceptable format (JSON) - The Azure Sentinel Log Analytics Data Collector API accepts the request in [JSON format](https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api#request-body). Refer to the [Record type and properties formatting details and examples](https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api#record-type-and-properties) and format the data received into JSON before progressing to the next step of posting the logs to the Azure Sentinel workspace.
  - POST the logs to the Azure Sentinel workspace using the [Azure Log Analytics Data Collector API](https://docs.microsoft.com/azure/azure-monitor/platform/data-collector-api).
- [**azuredeploy_DataConnector_API_AzureFunctionApp_template.json** template file](https://aka.ms/sentinelazurefunctiondeploymentfiletemplate)
- **GitHub repository** to store the Function App files - The Azure Function files can be in [Azure Sentinel GitHub](https://aka.ms/threathunters) repository
- **PowerShell** to create an encoded URL

#### 1. Upload Function App Files
1. Create a **.zip** file containing all the Function App Files. This should include the run.ps1, function.json, and any dependent modules
2. Rename the azuredeploy_DataConnector_API_FunctionApp_template.json template as azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json by entering the right PROVIDER_NAME_APPLIANCE_NAME for the data connector
3. Upload the **.zip** file and the **azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json** template into the Azure Sentinel GitHub Repository

#### 2. Configure the azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json template
The azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json file is the link between the ARM Template and the Function App Code
1. Open the **azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json** template and navigate to the **parameters** section at the top. This section provides a mechanism for the end user to configure the environmental variables required by the Function App. Add all the necessary parameters and their default values, as neeeded. <br> * Required parameters often include the Workspace ID, Workspace Key, API Key(s)/Token, and API URI.
2. Configure the **resources** section to include all the application settings (environmental variables) required by the Function App as a properties value. The resource section creates the link between the parameters defined in the previous step and the environmental variables configured in the Function App code. This field is case-sensitive and must match the case within the Function App code. 
3. For the **WEBSITE_RUN_FROM_PACKAGE** property, add the link to the **.zip** file contain the Function App files as the value. This will link the ARM template to the Function App.

#### 3. Create an encoded URL
To create a single-click deployment button, an encoded URL to the **azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json** file is required. 

Prior to generating an encoded URL, ensure the Azure Function and relevant template are available in the [Azure Sentinel GitHub repository](https://aka.ms/threathunters). 
* The Azure Function and the relevant ARM template needs to land under a subfolder named PROVIDER_NAME_APPLIANCE_NAME in the [Azure Sentinel 'Data connector' folder](https://aka.ms/sentinelgithubdataconnectors).
* Refer to [contribution guidelines](https://aka.ms/sentinelgithubcontributionguidelines) to submit this as a GitHub Pull Request, for approval and merging. 

To create a encoded URL, using PowerShell: 

1. Select the **azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json** ARM template in the [Azure Sentinel GitHub repository](https://aka.ms/threathunters)
2. On the top right corner, select the **Raw** button to view the **azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json** in raw format. 
3. Copy the URL that appears in the browser as follows,`raw.githubusercontent.com/<filepath>/azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json`
4. On a local device, open PowerShell and enter the following commands:

>`$url = "raw.githubusercontent.com/<filepath>/azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json"`
>`[uri]::EscapeDataString($url)`

5. The output will be an encoded URL.

#### 4. Creating the Deploy to ARM Template Link
With the encoded URL created in the previous step, the link can now be distributed to deploy the Function App using the ARM Template. 

To create **Deploy to Azure** button, use the Microsoft Azure graphic located `https://aka.ms/deploytoazurebutton`

![Deploy To Azure](https://aka.ms/deploytoazurebutton)

Examples of how to integrate within your documentation:
**JSON:** `[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](<encodedURL>)`
**Markdown:** `<a href="<encodedURL>" target="_blank"> <img src="https://aka.ms/deploytoazurebutton"> </a>`

#### 5. Updating the Function App Code
Any updates to the Function App code should be updated through the GitHub repository replacing the files within the **.zip** file. If addition environment variables are needed, the **azuredeploy_Connector_PROVIDER_NAME_APPLIANCE_NAME_AzureFunction.json** must be updated.
