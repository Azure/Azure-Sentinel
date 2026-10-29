# Censys Supplier Risk Data Connector
* [Introduction](#Introduction)
* [Description](#Description)
* [Folders](#Folders)
* [Prerequisites](#Prerequisites)
* [Configuration](#Configuration)
* [Installing for the users](#Installing-for-the-users)
* [Installing for testing](#Installing-for-testing)

## Introduction<a name="Introduction"></a>

This folder contains the Azure function time trigger code for Censys Supplier Risk Data Connector. The connector will run periodically and ingest the Censys risk events into the Microsoft Sentinel logs custom table `CensysRiskEvents_CL`.

## Description<a name="Description"></a>

The [Censys](https://censys.com/) Supplier Risk Data Connector brings the risk events of the Censys Supplier Risk change feed (`/v1/supplychains/default/risk-events`) into Microsoft Sentinel. Each event is one state change (opened, resolved or reopened) of a risk on an asset of one of your suppliers.

* The events are sent to the table `CensysRiskEvents_CL` with the [Logs Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview), through a data collection endpoint and a data collection rule that the deployment template creates.
* The connector saves the position of the last ingested event after every page, so each run continues where the previous one stopped.
* Suppliers and risks can be selected by name. A second function keeps the supplier names and risk names, with their ids, in storage tables of the Function App (nothing from it is sent to Microsoft Sentinel).
* The solution parsers `CensysRiskEvents` (one row per event) and `CensysRisks` (the current state of each risk) read the table.

## Folders<a name="Folders"></a>

1. `CensysRiskEventsFunctionConnector/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. `CensysSRRiskEvents/` - This contains the Azure function source code to ingest the data of below mentioned endpoint.
    * Risk events (`/v1/supplychains/default/risk-events`)
3. `CensysSRSuppliersAndRisks/` - This contains the Azure function source code that keeps the names and ids of the suppliers and risks in storage tables, to be used by the `SupplierNames` and `RiskNames` inputs. It reads the below mentioned endpoints.
    * Suppliers (`/v1/supplychains/default/suppliers`)
    * Risks (`/v1/supplychains/default/risks`)
4. `SharedCode/` - This contains the constants, logger, exceptions, Censys API client, checkpoint, input validation, supplier and risk lookup and Logs Ingestion code used in each azure function.

## Prerequisites<a name="Prerequisites"></a>
1. A Censys personal access token and the Censys Organization ID are required. Users on Starter, Search, and Core plans need the **API Access** role. See the documentation to [create a token](https://accounts.censys.io/settings/personal-access-tokens).
2. A Microsoft Entra application (app registration) with a client secret is required. The deployment template gives it the **Monitoring Metrics Publisher** role on the data collection rule.
3. Read and write permissions on the Log Analytics workspace of Microsoft Sentinel, and permission to create a Function App and role assignments in its resource group.

The Function App runs on the Flex Consumption plan (Linux, Python 3.14). Azure Government is not supported.

## Configuration<a name="Configuration"></a>

### STEP 1 - Steps to Create/Get a Censys Personal Access Token and Organization ID

Follow these instructions to get the values needed by this connector:

1. Sign in to Censys and open [Personal access tokens](https://accounts.censys.io/settings/personal-access-tokens).
2. Create a personal access token. Users on Starter, Search, and Core plans need the **API Access** role.
3. Copy the token. It is shown only once.
4. Copy the **Organization ID** (UUID) of the Censys organization you want to collect risk events for.

Supplier names and risk names, used by the optional filters, can be picked from the Censys Supplier Risk UI.

### STEP 2 - Get the name of the Log Analytics workspace

The deployment template creates the table, the data collection endpoint and the data collection rule in the workspace of Microsoft Sentinel, so deploy it in the resource group of that workspace. You need the **name** of the workspace (workspace Overview page).

### STEP 3 - App Registration steps for the Application in Microsoft Entra ID

This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:

1. Sign in to the Azure portal.
2. Search for and select Microsoft Entra ID.
3. Under Manage, select App registrations > New registration.
4. Enter a display Name for your application.
5. Select Register to complete the initial app registration.
6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the Application (client) ID and Tenant ID. The client ID and Tenant ID are required as configuration parameters for the execution of Censys Supplier Risk Data Connector.
- Reference link: https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app

### STEP 4 - Add a client secret for application in Microsoft Entra ID

Sometimes called an application password, a client secret is a string value required for the execution of Censys Supplier Risk Data Connector. Follow the steps in this section to create a new Client Secret:

1. In the Azure portal, in App registrations, select your application.
2. Select Certificates & secrets > Client secrets > New client secret.
3. Add a description for your client secret.
4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
5. Select Add.
6. Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page. The secret value is required as configuration parameter for the execution of Censys Supplier Risk Data Connector.
- Reference link: https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret

### STEP 5 - Get Object ID of your application in Microsoft Entra ID

After creating your app registration, follow the steps in this section to get the Object ID:

1. Go to Microsoft Entra ID.
2. Select Enterprise applications from the left menu.
3. Find your newly created application in the list (you can search by the name you provided).
4. Click on the application.
5. On the overview page, copy the Object ID. This is the **Azure_Entra_Object_Id** needed for the ARM template role assignment. The template gives this application the **Monitoring Metrics Publisher** role on the data collection rule, so no other role needs to be assigned.

## Installing for the users<a name="Installing-for-the-users"></a>

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in Data connectors section of Microsoft Sentinel.

i. Go to Microsoft Sentinel -> Data Connectors

ii. Click on the Censys Supplier Risk (using Azure Functions), connector page will open.

iii. Click on Deploy to Azure

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-CensysSRRiskEventsFunction-azuredeploy)

It will lead to a custom deployment page where user need to select **Subscription** and **Resource Group** (use the resource group of the Log Analytics workspace of Microsoft Sentinel).
And need to enter below information to configure Censys Supplier Risk Data Connector.

User Inputs  | Default Value
------------- | -------------
Censys SR Function Name  | CensysSR (name prefix, up to 10 characters)
Censys Api Key  | None
Censys Organization Id  | None
Censys Start Date Time  | Empty (all events Censys still retains)
Censys Supplier Names  | Empty (all suppliers)
Censys Risk Names  | Empty (all risks)
Censys Change Types  | Empty (opened, resolved and reopened)
Censys Severity  | Empty (all severities)
Censys Rapid Response  | Empty (both)
Azure_Client_Id  | None
Azure_Client_Secret  | None
Azure_Tenant_Id  | None
Azure_Entra_Object_Id  | None
WorkspaceName  | None
Location  | Location of the resource group
Censys Risk Events Table Name  | CensysRiskEvents_CL
Censys Risk Events Collection Schedule  | 0 */10 * * * *
Censys Supplier and Risk List Refresh Schedule  | 0 */30 * * * *
AppInsightsWorkspaceResourceID  | None
Censys SR Function Log Level  | INFO

* **Censys Start Date Time:** UTC time to start collecting from, for example `2026-10-01T00:00:00Z`. It must not be in the future.
* **Censys Supplier Names / Censys Risk Names:** names separated by an asterisk (*), for example `OpenAI*Harvey*Acme, Inc.` or `Log4Shell*Exposed Redis`. Pick the names from the Censys Supplier Risk UI. Names are not case-sensitive and the maximum is 500 characters. A name that is not found is skipped with a warning in the log. If none of the names of a setting is found, nothing is collected in that run and the next run tries again.
* **Censys Change Types:** comma-separated `opened`, `resolved`, `reopened`. **Censys Severity:** comma-separated `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`. **Censys Rapid Response:** `true` for rapid response findings only, `false` to exclude them.
* A wrong value in an input stops the run with an error that names the input, and nothing is sent. A change of a filter applies from the next run and continues from the current position, so avoid changing the filters often.
* **Warning:** keep the frequency of both schedules at least 10 minutes for a better experience. The schedules are NCRONTAB expressions with six fields (second, minute, hour, day, month, day of week).

The template creates the table `CensysRiskEvents_CL`, a data collection endpoint, a data collection rule, the Application Insights component, the storage account and the Function App.

The connector should start ingesting the data into the logs at every time interval specified in Censys Risk Events Collection Schedule during configuration. The function that refreshes the supplier and risk lists runs once when the app starts and then at every time interval specified in Censys Supplier and Risk List Refresh Schedule.

## Installing for testing<a name="Installing-for-testing"></a>


i. Log in to Azure portal using the URL - [Azure Portal-Home](https://ms.portal.azure.com/?feature.BringYourOwnConnector=true&feature.experimentationflights=ConnectorsKO#home).

ii. Go to Microsoft Sentinel -> Data Connectors

iii. Click the “import” button at the top and select the json file `CensysSR_RiskEvents_FunctionApp.json` downloaded on your local machine from Github.

iv. This will load the connector page and rest of the process will be same as the Installing for users guideline above.


Each invocation and its logs of the function can be seen in Function App service of Azure, available in the Azure Portal outside the Microsoft Sentinel.

i. Go to Function App and click on the function which you have deployed, identified with the given name at the deployment stage.

ii. Go to Functions -> `CensysSRRiskEvents` or `CensysSRSuppliersAndRisks` -> Monitor

iii. By clicking on invocation time, you can see all the logs for that run. The log lines start with `CensysSR`. Set the Censys SR Function Log Level to `DEBUG` for more detail.

**Note: Furthermore we can check logs in Application Insights of the given function in detail if needed. We can search the logs by operation ID in Transaction search section.**
