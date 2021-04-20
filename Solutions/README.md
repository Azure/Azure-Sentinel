# Azure Sentinel Solutions 
Azure Sentinel Solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product and/or domain and/or vertical scenarios in Azure Sentinel. This experience is powered by Azure Marketplace for Solutions’ discoverability, deployment and enablement and Microsoft Partner Center for Solutions’ authoring and publishing. 

# Why Azure Sentinel Solutions?
* Customers can easily discover packaged content and integrations that deliver product value or for a domain or for a vertical centrally in Azure Sentinel. 
* Customers can easily deploy and optionally enable content to get started immediately.
* Providers or partners can deliver combined product or domain or vertical value via Solutions in Azure Sentinel and be able to productize investments too.

# Solution Package
Clone the repository [Sentinel-AzMP-Solutions](https://msazure.visualstudio.com/One/_git/Sentinel-AzMP-Solutions) to C:\One.
## Create Input File
Create an input file and place it in the path C:\One\Sentinel-AzMP-Solutions\solutions\automation\input.

**Input File Format:**
```
/**
 * Solution Automation Input File Interface
 * -----------------------------------------------------
 * The purpose of this interface is to provide detail on
 *  the various fields the input file can have.
 */
interface SolutionAutomationInput {
  Name: string;                //Solution Name      - Ex. "Symantec Endpoint Protection"
  Author: string;              //Author of Solution - Ex. "Eli Forbes - v-eliforbes@microsoft.com"
  Logo: string;                //Link to the Logo used in the CreateUiDefinition.json
  Description: string;         //Solution Description used in the CreateUiDefinition.json
  WorkbookDescription: string; //Workbook description from ASI-Portal Workbooks Metadata

  //The following fields take arrays of paths relative to the solutions folder.
  //Ex. Workbooks: ["Workbooks/SymantecEndpointProtection.json"]
  Workbooks?: string[];
  "Analytic Rules"?: string[];
  Playbooks?: string[];
  Parsers?: string[];
  "Hunting Queries"?: string[];
  "Data Connectors"?: string[];
  BasePath?: string; //Optional base path to use. Either Internet URL or File Path. Default = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/""
}
```

**Example of Input File: Solution_McAfeePO.json**
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
    "Analytic%20Rules/McAfeeEPOAgentHandlerDown.yaml",
    "Analytic%20Rules/McAfeeEPOAlertError.yaml"
  ],
  "Parsers": [
    "Parsers/McAfeeEPOEvent.txt "
  ],
  "Hunting Queries": [
    "Hunting%20Queries/McAfeeEPOAgentErrors.yaml"
  ],
  "Data Connectors": [
    "Data%20Connectors/Connector_McAfee_ePO.json"
  ],
  "BasePath": "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions"
}  
```

## Generate Solution Package
Run generateSolution script in the automation folder which will create solution package with createUIDefinition.json, mainTemplate.json and zip file(version (1.0.0) as name) in the solutions folder with respect to the given input file. For every new modification to the files createUIDefinition.json and mainTemplate.json, a new zip file containing modified files should be created with latest version name (1.0.1, 1.0.2…..) and should be placed in the solution folder along with previous zip file.

## Validate Package
Validate the Solution offer files createUiDefinition.json and mainTemplate.json using the Azure Toolkit / TTK CLI tool. This tool helps with static analysis. User can validate package through two methods.

**Through generated xml files:**
1.	Go to path C:\One\Sentinel-AzMP-Solutions\tmp\results\arm-ttk
2.	Check the xml files of respective solution to check the validations.
3.	If errors are displayed make necessary modifications to the files so it passes all validations.

**Through commands:**

**Setup & Run arm-ttk tool:**
1.	Clone the repository https://github.com/Azure/arm-ttk to C:\One 
    *	If C:\One does not exist, create the folder. 
    * You may also choose a different folder but reference it properly while importing module.
1.	Open powershell, go to the solution path and run the following command to import arm-ttk module.
    * Import-Module C:\One\arm-ttk\arm-ttk\arm-ttk.psd1
1.	Move to the directory where your solution files reside.
1.	Run the following command:
    *	Test-AzTemplate
1.	Check whether all the validations are passed or not.
1.	If any errors are displayed make necessary modifications to the files so it passes all validations.

After all the checks in arm-ttk tool are passed. Validate the package files by following below steps:

**1.	Validate createUiDefinition.json:**
  * Open [CreateUISandbox](https://portal.azure.com/?feature.customPortal=false#blade/Microsoft_Azure_CreateUIDef/SandboxBlade).
  * Copy json content from createUiDefinition.json (in the recent version).
  * Clear that content in the editor and replace with copied content in step #2.
  * Click on preview
  * You should see the user Interface preview of data connector, workbook etc. and descriptions you provided in input file.
  * Check the description and User interface of solution preview.

**1.	Validate maintemplate.json:**

Validate mainTemplate by deploying the template in portal. 
Follow these steps to deploy in portal:
  * Open up https://aka.ms/AzureSentinelPrP which launches the Azure portal with the needed private preview flags.
  * Go to “Deploy a Custom Template” on the portal
  * Select “Build your own template in Editor”.
  * Copy json content from mainTemplate.json (in the recent version).
  * Clear that content in the editor and replace with copied content in step #3.
  * Click Save and then progress to selecting subscription, sentinel enabled resource group and corresponding workspace etc. to complete the deployment ->Final Step would be Review + Create to trigger deployment.
  * Check if deployment successfully completes.
  * You should see the data connector workbook etc. deployed in the respective galleries and validate – let us know your feedback.







