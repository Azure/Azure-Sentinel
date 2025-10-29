# Microsoft Sentinel Solutions Packaging Tool Guidance

Microsoft Sentinel Solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product and/or domain and/or vertical scenarios in Microsoft Sentinel. This experience is powered by Azure Marketplace for Solutions' discoverability, deployment and enablement and Microsoft Partner Center for Solutions’ authoring and publishing. Refer to details in [Microsoft Sentinel solutions documentation](https://aka.ms/azuresentinelsolutionsdoc). Detailed partner guidance for authoring and publishing solutions is covered in [building Microsoft Sentinel solutions guidance](https://aka.ms/sentinelsolutionsbuildguide).

The packaging tool detailed below provides an easy way to generate your solution package of choice in an automated manner and enables validation of the package generated as well. You can package different types of Microsoft Sentinel content that includes a combination of data connectors, parsers or Kusto Functions, workbooks, analytic rules, hunting queries, Azure Logic apps custom connectors, playbooks and watchlists.

## Creating Solution Package

Clone the repository [Azure-Sentinel](https://github.com/Azure/Azure-Sentinel) to `C:\GitHub`.

### Create Input File

- Make sure to have a **.json** input data file inside of 'Data' folder for your solution. 
- Review the input file format guidance below to create/update the input file. Ensure that all the mandatory properties have the intended values. Review all optional properties wherever necessary.
> **NOTE:** The input file is used by the pipeline to auto-generate a solution package. Any inaccuracies in this file will propogate unintended changes in the auto-generated solution package.
- (Optional) Set the "createPackage" property in data input file. This property is optional and is default to true. 
> This should be set to **false**, only when the package creation requires to be skipped.
- The json array properties for content types ("Workbooks", "Analytic Rules", "Data Connectors", "Parsers", "Playbooks" & "Parsers") in input file are optional as it will be calculated at pipeline run automatically. Please note:
    - If any of the propereties are not added to the input file, all the content templates from the Solutions folder for each property that doesn't exist will be computed at runtime and then added to the solution package. 
    - If content names are specified, only the templates specified will be considered for packaging.
    - If you want any specific resources not to be added to the package, just specify empty array in data input file. E.g: If you have playbooks folder and files in a solution but dont want to add these playbooks to the generated package, then specify an empty array for the "Playbooks" property (such as "Playbooks": []). Doing this will ensure playbooks (even if they exist) are not considered during the packaging process.

    E.g: For solution "Alibaba Cloud", if you have parsers, dataconnectors  then no need to specify json array in data input file and when we make any change in the solution and push it via a pull request, it will trigger workflows that identify files automatically within the Alibaba Clould solution and generate package accordingly.

- When Pull Request is in open state, this package will be added automatically into the same PR.

#### **Input File Format:**

```json
/**
 * Solution Automation Input File Json
 * -----------------------------------------------------
 * The purpose of this json is to provide detail on the various fields the input file can have.
 * Name: Solution Name - Ex. "Symantec Endpoint Protection"
 * Author: Author Name+Email of Solution - Ex. "Clark Kent - Clark.Kent@contoso.com"
 * Logo: Link to the Logo used in createUiDefinition.json
 * - NOTE: This field is only recommended for Azure Global Cloud. It is not recommended for solutions in Azure Government Cloud as the image will not be shown properly.
 * Description: Solution description used in createUiDefinition.json. Can include markdown.
 * WorkbookDescription: Workbook description(s), generally from Workbooks' Metadata. This field can be a string if 1 description is used across all, and an array if multiple are used.
 * PlaybookDescription: Playbook description(s), generally from Playbooks' Metadata. This field can be a string if 1 description is used across all, and an array if multiple are used.
 * WatchlistDescription: Watchlist description(s), generally from Watchlists' Property data. This field can be a string if 1 description is used across all, and an array if multiple are used. This field is used if the description from the Watchlist resource is not desired in the Create-UI.
 * Workbooks, Analytic Rules, Playbooks, etc.: These fields take arrays of paths relative to the repo  root, or BasePath if provided.
 * SavedSearches: This input assumes a format of any of the following:
 * -- Direct export via API (see https://docs.microsoft.com/rest/api/loganalytics/saved-searches/list-by-workspace)
 * -- Array of SavedSearch resources
 * -- Raw ARM template
 *
 * - NOTE: Playbooks field can take standard Playbooks, Custom Connectors, and Function Apps. Sequence of Playbooks should be FunctionApps, Custom Connector and then rest of the Playbooks. If FunctionApps and Custom Connector are not present then just specify Playbooks.
 * BasePath: Optional base path to use. Either Internet URL or File Path. Default is repo root (https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/)
 * Version: Version to be used during package creation. Default version will be 3.0.0. This tool supports package creation for 2.x.x(Template Spec) and 3.x.x(contentPackages). Based on variable 'defaultPackageVersion' and given Version input. If the defaultPackageVersion is 3.0.0 and Data file input version is 2.0.1 then it package generated is of 3.0.0 i.e which ever is higher takes precedence. Here we are also verifying the catalogAPI to check version deployed in PartnerCenter. If 'defaultPackageVersion' is 2.0.0 and data input file version is 2.0.4 but in PartnerCenter catalogAPI version installed is 2.0.2 then package generated is of 2.0.3 i.e it will increment the package version based on catalogAPI.
 * Metadata: Name of metadata file for the Solution, path is to be considered from BasePath.
 * All properties are MANDATORY unless explicitly specified as optional in the comment with the property.
 */
{
  "Name": "{SolutionName}",
  "Author": "{AuthorName - Email}",
  "Logo": "<img src=\"{LogoLink}\" width=\"75px\" height=\"75px\">",
  "Description": "{Solution Description}",
  "WorkbookDescription": ["{Description of workbook(s)}"],
  "Workbooks": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "WorkbookBladeDescription": "{string}", //This is optional property. Custom description to be used in the CreateUiDefinition.json for Workbooks Blade
  "AnalyticalRuleBladeDescription": "{string}", //This is optional property. Custom description to be used in the CreateUiDefinition.json for Analytical Rule Blade
  "HuntingQueryBladeDescription": "{string}", //This is optional property. Custom description to be used in the CreateUiDefinition.json for Hunting Query Blade
  "PlaybooksBladeDescription": "{string}", //This is optional property. Custom description to be used in the CreateUiDefinition.json for Playbook Blade
  "Analytic Rules": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "Playbooks": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder. Ensure if there is any CustomConnector in the solution then it's entry should be added prior to any other playbook.
  "PlaybookDescription": ["{Description of playbook(s)}"],
  "Parsers": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "SavedSearches": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "Hunting Queries": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "Data Connectors": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "Watchlists": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "WatchlistDescription": [], //Optional. If not specified, this will be auto-populated with ALL Workbooks in the respective solution folder.
  "BasePath": "{Path to Solution Content}",
  "Version": "3.0.0", // Default version of 3.0.0. If you want create templateSpec package then change variable 'defaultPackageVersion' value in createSolutionV3.ps1 file 
  "Metadata": "{Name of Solution Metadata file}",
  "Is1PConnector": false,
  "createPackage": true  // This is optional property. Default value is true. When set to false, a package will not be generated using V3(local) or V4(pipeline).
}

```

#### **Example of Input File: Solution_McAfeePO.json**

```json
{
  "Name": "Cisco Umbrella",
  "Author": "Microsoft - support@microsoft.com",
  "Logo": "<img src=\"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/cisco-logo-72px.svg\" width=\"75px\" height=\"75px\">",
  "Description": "The [Cisco Umbrella](https://umbrella.cisco.com/) solution for Microsoft Sentinel enables you to ingest [Cisco Umbrella events](https://docs.umbrella.com/deployment-umbrella/docs/log-formats-and-versioning) stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API.

  **Underlying Microsoft Technologies used:**\n\nThis solution takes a dependency on the following technologies, and some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs:
  a. [Azure Monitor HTTP Data Collector API](https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api)
  b. [Azure Functions](https://azure.microsoft.com/services/functions/#overview)  ",
  "WorkbookBladeDescription": "This Microsoft Sentinel Solution installs workbooks. Workbooks provide a flexible canvas for data monitoring, analysis, and the creation of rich visual reports within the Azure portal. They allow you to tap into one or many data sources from Microsoft Sentinel and combine them into unified interactive experiences.",
  "AnalyticalRuleBladeDescription": "This solution installs the following analytic rule templates. After installing the solution, create and enable analytic rules in Manage solution view. ",
  "HuntingQueryBladeDescription": "This solution installs the following hunting queries. After installing the solution, run these hunting queries to hunt for threats in Manage solution view",
  "PlaybooksBladeDescription": "This solution installs the following Playbook templates. After installing the solution, playbooks can be managed in the Manage solution view. ",
  "Data Connectors": [
    "DataConnectors/CiscoUmbrella/CiscoUmbrella_API_FunctionApp.json"
  ],
  "Parsers": [
    "Solutions/CiscoUmbrella/Parsers/Cisco_Umbrella"
  ],
  "Hunting Queries": [
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaAnomalousFQDNsforDomain.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaBlockedUserAgents.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaDNSErrors.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaDNSRequestsUunreliableCategory.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaHighCountsOfTheSameBytesInSize.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaHighValuesOfUploadedData.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaPossibleConnectionC2.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaPossibleDataExfiltration.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaProxyAllowedUnreliableCategory.yaml",
    "Solutions/CiscoUmbrella/Hunting Queries/CiscoUmbrellaRequestsUncategorizedURI.yaml"
  ],
  "Analytic Rules": [
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaConnectionNon-CorporatePrivateNetwork.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaConnectionToUnpopularWebsiteDetected.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaCryptoMinerUserAgentDetected.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaEmptyUserAgentDetected.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaHackToolUserAgentDetected.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaPowershellUserAgentDetected.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaRareUserAgentDetected.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaRequestAllowedHarmfulMaliciousURICategory.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaRequestBlocklistedFileType.yaml",
    "Solutions/CiscoUmbrella/Analytic Rules/CiscoUmbrellaURIContainsIPAddress.yaml"
  ],
  "Workbooks": [
    "Solutions/CiscoUmbrella/Workbooks/CiscoUmbrella.json"
  ],
  "Playbooks": [
    "Playbooks/CiscoUmbrellaEnforcementAPIConnector/azuredeploy.json",
    "Playbooks/CiscoUmbrellaInvestigateAPIConnector/azuredeploy.json",
    "Playbooks/CiscoUmbrellaManagementAPIConnector/azuredeploy.json",
    "Playbooks/CiscoUmbrellaNetworkDeviceManagementAPIConnector/azuredeploy.json",
	"Playbooks/Playbooks/CiscoUmbrella-AddIpToDestinationList/azuredeploy.json",
    "Playbooks/Playbooks/CiscoUmbrella-AssignPolicyToIdentity/azuredeploy.json",
    "Playbooks/Playbooks/CiscoUmbrella-BlockDomain/azuredeploy.json",
    "Playbooks/Playbooks/CiscoUmbrella-GetDomainInfo/azuredeploy.json"
  ],
  "BasePath": "C:\\GitHub\\Azure-Sentinel",
  "Version": "3.0.0", // Default version of 3.0.0. If you want create templateSpec package then change variable 'defaultPackageVersion' value in createSolutionV3.ps1 file 
  "Metadata": "SolutionMetadata.json",
  "Is1PConnector": false
}
```

### Create Solution Metadata File

Create a  file and place it in the base path of solution `https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/McAfeeePO/`.
* Refer to the [Microsoft Sentinel content and solutions categories documentation](https://aka.ms/sentinelcontentcategories) for a complete list of valid Microsoft Sentinel categories.
* Refer to [Microsoft Sentinel content and support documentation](https://aka.ms/sentinelcontentsupportmodel) for information on valid support models.


#### **Metadata File Format:**

```json
/**
 * Solution Automation Metadata File Json
 * -----------------------------------------------------
 * The purpose of this json is to provide detail on the various fields the metadata of a solution can have. Refer to the metadata schema and example provided after the definitions for further context.
 * publisherId: An identifier that's used by Partner Center to uniquely identify the publisher associated with a commercial marketplace account.- Ex. "azuresentinel", "CheckPoint", "semperis"
 * offerId: Id of the Offer of Solution - Ex. "azure-sentinel-solution-ciscoaci", "azure-sentinel-solution-semperis-dsp"
 * firstPublishDate: Solution first published date
 * lastPublishDate: Latest published date of Solution
 * providers: Provider of the solution. Specify one or many providers as a comma separated list as applicable for the solution - Ex. Cisco, Checkpoint, Microsoft
 * categories: Domain and Vertical applicability of the solution. There can be multiple domain and/or vertical categories applicable to the same solution which can be represented as an array. For e.g. Domains - "Security - Network", "Application", etc. and Vertical - "Healthcare", "Finance". Refer to the [Microsoft Sentinel content and solutions categories documentation](https://aka.ms/sentinelcontentcategories) for a complete list of valid Microsoft Sentinel categories.
 * support: Name, Email, Tier and Link for the solution support details.
 * - NOTE: Additional metadata properties like Version, Author, etc. are used by the packaging tool based on the values provided in the input file. Format specified in the example below. Refer to [Microsoft
 content and support documentation](https://aka.ms/sentinelcontentsupportmodel) for further information.
 */
{
    "publisherId": "{Id of Publisher}",
    "offerId": "{Solution Offer Id}",
    "firstPublishDate": "{Solution First Published Date in the YYYY-MM-DD format}",
    "lastPublishDate": "{Solution recent Published Date in the YYYY-MM-DD format}",
    "providers": "{Solution provider list}",
    "categories": {
      "domains" : "{Solution category domain list}",
      "verticals": "{Solution category vertical list}",
     },
    "support": {
      "name": "{Name of the entity supporting the solution}",
      "email": "{Email for Solution support}",
      "tier": "{Support Tier}", //Enter one of the following: Microsoft, Partner or Community
      "link": "{Link of Support contacts for Solution}",
    }
}

```

#### **Example of Input File: SolutionMetadata.json**

```json
{
	"publisherId": "azuresentinel",
	"offerId": "azure-sentinel-solution-mcafeeepo",
	"firstPublishDate": "2021-03-26",
	"lastPublishDate": "2021-08-09",
	"providers": ["Cisco"],
	"categories": {
		"domains" : ["Security - Network"],
		"verticals": []
	},
	"support": {
	  "name": "Microsoft Corporation",
	  "email": "support@microsoft.com",
	  "tier": "Microsoft",
	  "link": "https://support.microsoft.com"
	}
} 
```

### Generate Solution Package

- `Package will now be created in an automated way through an automated pipeline and without the need to run any commands locally to generate the solution package. 'createSolutionV4.ps1' file is specifically for pipeline way of generating package for any of the solutions`. 'createSolutionV4.ps1' file is located at `./Tools/Create-Azure-Sentinel-Solution/pipeline` folder path. This file cannot be run locally and is meant for packaging from pipeline using Github workflows.
 > **IMPORTANT:** To generate package locally make use of `createSolutionV3.ps1` which is in './Tools/Create-Azure-Sentinel-Solution/V3' folder.
- Core business logic for 'createSolutionV3.ps1' and 'createSolutionV4.ps1' files are inside of './Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1' file. 
- For any of the WorkbookMetadata change make use of './Tools/Create-Azure-Sentinel-Solution/V2/WorkbookMetadata/WorkbooksMetadata.json' file.
- Make sure you have data input file inside of **Data** folder and added a SolutionMetadata.json file inside in the respetcive solutions folder.
- (Optional) Set the "createPackage" property in data input file. This property is optional and is set default to true. 
> This should be set to **false**, only when the package creation requires to be skipped.
- The json array properties for content types ("Workbooks", "Analytic Rules", "Data Connectors", "Parsers", "Playbooks" & "Parsers") in input file are optional as it will be calculated at pipeline run automatically. Please note:
    - If any of the propereties are not added to the input file, all the content templates from the Solutions folder for each property that doesn't exist will be computed at runtime and then added to the solution package. 
    - If content names are specified, only the templates specified will be considered for packaging.
    - If you want any specific resources not to be added to the package, just specify empty array in data input file. E.g: If you have playbooks folder and files in a solution but dont want to add these playbooks to the generated package, then specify an empty array for the "Playbooks" property (such as "Playbooks": []). Doing this will ensure playbooks (even if they exist) are not considered during the packaging process.
    E.g: For solution "Alibaba Cloud", if you have parsers, dataconnectors  then no need to specify json array in data input file and when we make any change in the solution and push it via a pull request, it will trigger workflows that identify files automatically within the Alibaba Clould solution and generate package accordingly.

The package, once generated consists of the following files:

* `createUIDefinition.json`: Template containing the definition for the Deployment Creation UI

* `mainTemplate.json`: Template containing Deployable Resources

These files will be created in the solution's `Package` folder with respect to the resources provided in the given input file. For every new modification to the files after the initial version of package, a new zip file should be created with an updated version name (3.0.0, 3.0.1 etc.) containing modified `createUIDefinition.json` and `mainTemplate.json` files.

Upon package creation, the automation will automatically import and run automated validation on the generated files using the Azure Toolkit / TTK CLI tool.

### Azure Toolkit Validation

The Azure Toolkit Validation is run automatically after package generation. However, if you make any manual edits to the template after the package is generated, you'll need to manually run the Azure Toolkit technical validation on your solution to check the end result.

If you've already run the package creation tool in your current PowerShell instance, you should have the validation command imported and available, otherwise follow the steps below to install.

#### Azure Toolkit Validation Setup

- When package is generated using pipeline this step is automatically executed. For manual validation follow below steps.
- Clone the [arm-ttk repository](https://github.com/Azure/arm-ttk) to `C:\One`
  - If `C:\One` does not exist, create the folder.
  - You may also choose a different folder, but properly reference it in the Profile script.
- Open your Powershell Profile script
  - To find your Powershell Profile Script:
    - Open Powershell.
    - Type `$profile`, and hit enter.
    - Your Powershell Profile script path will be output to the screen.
    - Open the Profile script.
- Add the following line of code to your Profile script.
  - `Import-Module C:\One\arm-ttk\arm-ttk\arm-ttk.psd1`
- Save and close your Profile script.
- Refresh your profile.
  - Run the following command in Powershell: `& $profile`
  - Alternatively, you can close and re-open your PowerShell window.

#### Azure Toolkit Validation Usage

- Navigate to the directory of your solution.
- Run: `Test-AzTemplate`

### Manual Validation

Once the package is created and Azure Toolkit technical validation is passing, one should manually validate that the package is created as desired.

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

### Known Failures

#### VMSizes Must Match Template

This will generally show as a warning but the test will be skipped. This will not be perceived as an error by the build.

### Common Issues

#### Template Should Not Contain Blanks

This issue most commonly comes from the serialized workbook and playbooks, due to certain properties in the json having values of null, [], or {}. To fix this, remove these properties.

#### IDs Should Be Derived from ResourceIDs

Some IDs used, most commonly in resources of type `Microsoft.Web/connections`, tend to throw this error despite seeming to fit the expected format. To fix this define two variables, one which uses the problematic ID value, and another which references the first variable, then use this second variable as necessary in place of the ID value. See below for example of such a variable pair:

```json
"variables": {
    "playbook-1-connection-1": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', parameters('workspace-location'), '/managedApis/microsoftgraphsecurity')]",
    "_playbook-1-connection-1": "[variables('playbook-1-connection-1')]"
  }
```

#### ApiVersions Should Be Recent

Some resources, particularly playbook-related resources, come in with outdated `apiVersion` properties, and depending on the version it may not be picked up as outdated by the validation.

Please ensure that resources of the following types use the corresponding versions:

```json
{
    "type": "Microsoft.Web/connections",
    "apiVersion": "2018-07-01-preview",
}
```

```json
{
    "type": "Microsoft.Logic/workflows",
    "apiVersion": "2019-05-01",
}
```

#### Parameters Must Be Referenced

It's possible some default parameters may go unused, especially if the solution consists mainly of playbooks. On failure this check will output the unused parameter(s) that exist within the `mainTemplate.json` file.

To fix this, remove the unused parameter from the `parameters` section of `mainTemplate.json`, and check the following common issue "Outputs Must Be Present In Template Parameters".

#### Outputs Must Be Present In Template Parameters

In most cases, this error is a result of removing an unused parameter reference from `mainTemplate.json`. To fix the error in such a case, remove the problematic output variable from the `outputs` section of `createUiDefinition.json`.

Otherwise, the parameter will need be added in the `parameters` section of `mainTemplate.json` and referenced as necessary.

#### Main Template Encoding Issues

If you generate your solution package using a version of PowerShell under 7.1, you'll likely face encoding errors which cause issues within the `mainTemplate.json` file.

The main encoding issue here will be that single-quote characters `'` are encoded into `\u0027`, and due to function references relying on single-quotes, this will break the template.

To resolve this issue, it's recommended that you install PowerShell 7.1+ and re-generate the package.

See [Setup](#setup) to install PowerShell 7.1+.


#### YAML Conversion Issues

If the YAML Toolkit for PowerShell is not installed, you may experience errors related to converting `.yaml` files, for analytic rules or otherwise.

To resolve this issue, it's recommended that you install the YAML Toolkit for Powershell.

See [Setup](#setup) to install the YAML Toolkit for PowerShell.

#### ARM-TTK failue for ContentProductId, Id Issues

If you see arm-ttk error for 'contentProductId' and 'id' for 'Ids should be derived from ResourceIds' then you can ignore this error validations. 

#### FILE EXTENSIONS

Make sure to specify file extension in lower case and and not caps(eg: office365.JSON).

#### MERGE MASTER INTO PULL REQUEST

It is always recommended to take latest pull of master branch and create a pull request. If a pull request is raised and we do master pull to get latest into our branch then make sure before pushing it to server we make a minor change in our solutions file be it a space or tag change in solutions that will identify your solution changes.
If we push changes after taking the latest from master then the package will not be generated for your changes in pr but for master changes. So once master latest is pulled make a minor change of space of tag in your existing solution file and then push the changes to server. This way package will be generated for your solution only. The reason is pipeline will always checks for the latest commit and run package processing step on it.

#### AUTOMATIC PACKAGE FOR FORK PULL REQUEST IS NOT SUPPORTED

When a pull request from a fork is raised with changes and pushed then pipeline packaging process will not kick start automatically. Due to security reasons we are not supporting packaging for form pull requests. We are working on a way for fork pull request to be able to create package automatically from pipeline. 