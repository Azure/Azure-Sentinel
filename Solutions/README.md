# Azure Sentinel Solutions

Azure Sentinel Solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product and/or domain and/or vertical scenarios in Azure Sentinel. This experience is powered by Azure Marketplace for Solutions' discoverability, deployment and enablement and Microsoft Partner Center for Solutions’ authoring and publishing.

## Why Azure Sentinel Solutions?

* Customers can easily discover packaged content and integrations that deliver product value or for a domain or for a vertical centrally in Azure Sentinel.
* Customers can easily deploy and optionally enable content to get started immediately.
* Providers or partners can deliver combined product or domain or vertical value via Solutions in Azure Sentinel and be able to productize investments too.

## Creating Solution Package

**Note: Packaging tool is currently not available. It will be available in the near future.**

Clone the repository [Azure-Sentinel](https://github.com/Azure/Azure-Sentinel) to `C:\One`.

### Create Input File

Create an input file and place it in the path `C:\One\Azure-Sentinel\Tools\PowerShell\Create-Sentinel-Solution\input`.

#### **Input File Format:**

```json
/**
 * Solution Automation Input File Json
 * -----------------------------------------------------
 * The purpose of this json is to provide detail on
 *  the various fields the input file can have.
 */
{
  "Name": "{SolutionName}",                                             //Solution Name      - Ex. "Symantec Endpoint Protection
  "Author": "{AuthorName - id}",                                        //Author of Solution - Ex. "Amarnath Pamidi - v-ampami@microsoft.com"
  "Logo": "{<img src=\"{LogoLink}\" width=\"75px\" height=\"75px\">}",  //Link to the Logo used in the CreateUiDefinition.json
  "Description": "{Solution Description}",                              //Solution Description used in the CreateUiDefinition.json
  //Workbook description(s) from ASI-Portal Workbooks Metadata, this field can be a string if 1 description is used, and an array if multiple
  "WorkbookDescription": ["{Description of workbook}"],
  //The following fields take arrays of paths relative to the solutions folder.
  //Ex. Workbooks: ["Workbooks/SymantecEndpointProtection.json"]
  "Workbooks": [],
  "Analytic Rules": [],
  "Playbooks": [],
  "Parsers": [],
  "Hunting Queries": [],
  "Data Connectors": [],
  "BasePath": "{Path to solution}" //Optional base path to use. Either Internet URL or File Path. Default = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/""
}

```

#### **Example of Input File: Solution_McAfeePO.json**

```json
{
  "Name": "McAfeePO",
  "Author": "Amarnath Pamidi – v-ampami@microsoft.com",
  "Logo": "<img src=\"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/McAfeeePO/Workbooks/Images/Logo/mcafee_logo.svg\" width=\"75px\" height=\"75px\">",
  "Description": "The [McAfee ePO](https://www.mcafee.com/enterprise/en-in/products/epolicy-orchestrator.html) is a centralized policy management and enforcement for your endpoints and enterprise security products. McAfee ePO monitors and manages your network, detecting threats and protecting endpoints against these threats.",
  "WorkbookDescription": "Gain insights into McAfeePO logs.",
  "Workbooks": [
    "Workbooks/McAfeeePOOverview.json"
  ],
  "Analytic Rules": [
    "Analytic Rules/McAfeeEPOAgentHandlerDown.yaml",
    "Analytic Rules/McAfeeEPOAlertError.yaml"
  ],
  "Parsers": [
    "Parsers/McAfeeEPOEvent.txt "
  ],
  "Hunting Queries": [
    "Hunting Queries/McAfeeEPOAgentErrors.yaml"
  ],
  "Data Connectors": [
    "Data Connectors/Connector_McAfee_ePO.json"
  ],
  "BasePath": "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions"
}  
```

### Generate Solution Package

To generate the solution package from the given input file, run the `generateSolution.ps1` script in the automation folder, and it will create a compressed solution package of version 1.0.0, with `createUIDefinition.json`, and `mainTemplate.json` files in the solutions folder with respect to the given input file. For every new modification to the files after the initial version of package, a new zip file should be created with latest version name (1.0.1, 1.0.2…..) containing modified `createUIDefinition.json` and `mainTemplate.json` files and should be placed in the solution folder along with previous zip files.

### Validate Package

Validate the Solution offer files createUiDefinition.json and mainTemplate.json using the Azure Toolkit / TTK CLI tool. This tool helps with static analysis.

**Setup & Run arm-ttk tool:**

1. Clone the repository <https://github.com/Azure/arm-ttk> to `C:\One`
    * If `C:\One` does not exist, create the folder.
    * You may also choose a different folder but reference it properly while importing module.
2. Open powershell, run the following command to add arm-ttk module to profile.
    * `Add-Content -Path $Profile -Value "Import-Module C:\One\arm-ttk\arm-ttk\arm-ttk.psd1"`
3. Refresh Profile
    * Run the following command in Powershell: `& $profile`
4. Move to the directory where your solution files reside.
5. Run the following command:
    * `Test-AzTemplate`
6. Check whether all the validations are passed or not.
7. If any errors are displayed make necessary modifications to the files so it passes all validations.

After all the checks in arm-ttk tool are passed. Validate the package files by following below steps:

**1. Validate createUiDefinition.json:**

* Open [CreateUISandbox](https://portal.azure.com/#blade/Microsoft_Azure_CreateUIDef/SandboxBlade).
* Copy json content from createUiDefinition.json (in the recent version).
* Clear that content in the editor and replace with copied content in step #2.
* Click on preview
* You should see the User Interface preview of data connector, workbook, etc., and descriptions you provided in input file.
* Check the description and User Interface of solution preview.

**2. Validate maintemplate.json:**

Validate `mainTemplate.json` by deploying the template in portal.
Follow these steps to deploy in portal:

* Open up <https://aka.ms/AzureSentinelPrP> which launches the Azure portal with the needed private preview flags.
* Go to "Deploy a Custom Template" on the portal
* Select "Build your own template in Editor".
* Copy json content from `mainTemplate.json` (in the recent version).
* Clear that content in the editor and replace with copied content in step #3.
* Click Save and then progress to selecting subscription, Sentinel-enabled resource group, and corresponding workspace, etc., to complete the deployment.
* Click Review + Create to trigger deployment.
* Check if the deployment successfully completes.
* You should see the data connector, workbook, etc., deployed in the respective galleries and validate – let us know your feedback.
