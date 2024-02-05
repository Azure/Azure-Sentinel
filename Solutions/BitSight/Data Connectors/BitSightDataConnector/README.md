# BitSight Data Connector
* [Introduction](#Introduction)
* [Description](#Description)
* [Folders](#Folders)
* [Prerequisites](#Prerequisites)
* [Configuration](#Configuration)
* [Installing for the users](#Installing-for-the-users)
* [Installing for testing](#Installing-for-testing)

## Introduction<a name="Introduction"></a>

This folder contains the Azure function time trigger code for BitSight Data Connector. The connector will run periodically and ingest the BitSight data into the Microsoft Sentinel logs custom tables.

## Description<a name="Description"></a>

The [BitSight](https://www.BitSight.com/) Data Connector supports evidence-based cyber risk monitoring by bringing BitSight data in Microsoft Sentinel.

## Folders<a name="Folders"></a>

1. `BitSightDataConnector/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. `AlertsGraphStatisticsDetails/` - This contains the Azure function source code to ingest the data of below mentioned endpoints.
    * Alert Data
    * Graph Data
    * Diligence statistics
    * Industries statistics
    * Observations statistics
    * Diligence historical statistics
3. `BreachesDetails/` - This contains the Azure function source code to ingest the data of below mentioned endpoint.
    * Breaches details
4. `CompaniesDetails/` - This contains the Azure function source code to ingest the data of below mentioned endpoint.
    * Companies details
5. `FindingsDetails/` - This contains the Azure function source code to ingest the data of below mentioned endpoint.
    * Findings Data
6. `FindingsSummaryDetails/` - This contains the Azure function source code to ingest the data of below mentioned endpoint.
    * Findings summary
7. `PortFolioCompanies/` - This contains azure function source code to ingest the data of companies available in Portfolio which will be used by other functions to retrieve various details for each company.
8. `SharedCode/` - This contains the constants, logger, exceptions and common methods used in each azure function.

## Prerequisites<a name="Prerequisites"></a>
1. BitSight API Token is required.  See the documentation to [learn more](https://help.bitsighttech.com/hc/en-us/articles/115014888388-API-Token-Management) about API Token.

## Configuration<a name="Configuration"></a>

### STEP 1 - Steps to Create/Get Bitsight API Token

Follow these instructions to get a BitSight API Token

1. For SPM App: Refer to the [User Preference](https://service.bitsight.com/app/spm/account) tab of your Account page, \n\t\tGo to Settings > Account > User Preferences > API Token.
2. For TPRM App: Refer to the [User Preference](https://service.bitsight.com/app/tprm/account) tab of your Account page, \n\t\tGo to Settings > Account > User Preferences > API Token.
3. For Classic BitSight: Go to your [Account](https://service.bitsight.com/settings) page, \n\t\tGo to Settings > Account > API Token.

### STEP 2 - App Registration steps for the Application in Microsoft Entra ID

This integration requires an App registration in the Azure portal. Follow the steps in this section to create a new application in Microsoft Entra ID:

1. Sign in to the Azure portal.
2. Search for and select Microsoft Entra ID.
3. Under Manage, select App registrations > New registration.
4. Enter a display Name for your application.
5. Select Register to complete the initial app registration.
6. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the Application (client) ID and Tenant ID. The client ID and Tenant ID is required as configuration parameters for the execution of BitSight Data Connector.
- Reference link: https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app

### STEP 3 - Add a client secret for application in Microsoft Entra ID

Sometimes called an application password, a client secret is a string value required for the execution of BitSight Data Connector. Follow the steps in this section to create a new Client Secret:

1. In the Azure portal, in App registrations, select your application.
2. Select Certificates & secrets > Client secrets > New client secret.
3. Add a description for your client secret.
4. Select an expiration for the secret or specify a custom lifetime. Limit is 24 months.
5. Select Add.
6. Record the secret's value for use in your client application code. This secret value is never displayed again after you leave this page. The secret value is required as configuration parameter for the execution of BitSight Data Connector.
- Reference link: https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app#add-a-client-secret

### STEP 4 - Assign role of Contributor to application in Microsoft Entra ID

Follow the steps in this section to assign the role:

1. In the Azure portal, Go to Resource Group and select your resource group.
2. Go to Access control (IAM) from left panel.
3. Click on Add, and then select Add role assignment.
4. Select Contributor as role and click on next.
5. In Assign access to, select User, group, or service principal.
6. Click on add members and type your app name that you have created and select it.
Now click on Review + assign and then again click on Review + assign.
- Reference link: https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal

## Installing for the users<a name="Installing-for-the-users"></a>

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in Data connectors section of Sentinel.

i. Go to Microsoft Sentinel -> Data Connectors

ii. Click on the BitSight Data Connector, connector page will open.

iii. Click on the blue `Deploy to Azure` button.

It will lead to a custom deployment page where after user need to select **Subscription**, **Resource Group** and **Location**.
And need to enter below information to configure BitSight Data Connector.
User Inputs  | Default Value
------------- | -------------
Function Name  | BitSight
API_token  | None
Azure_Client_Id | None
Azure_Client_Secret | None
Azure_Tenant_Id | None
Companies  | ALL
Workspace ID  | None
Workspace Key  | None
Portfolio_Companies_Table_Name | Portfolio_Companies
Alerts_Table_Name  | Alerts_data
Breaches_Table_Name | Breaches_data
Company_Table_Name  | Company_details
Company_Rating_Details_Table_Name  | Company_rating_details
Diligence_Historical_Statistics_Table_Name  | Diligence_historical_statistics
Diligence_Statistics_Table_Name  | Diligence_statistics
Findings_Summary_Table_Name  | Findings_summary
Findings_Table_Name  | Findings_data
Graph_Table_Name  | Graph_data
Industrial_Statistics_Table_Name  | Industrial_statistics
Observation_Statistics_Table_Name  | Observation_statistics
Log Level  | INFO
Schedule  | 0 0 * * * *
Schedule_Portfolio | 0 */30 *  * * *

The connector should start ingesting the data into the logs at every time interval specified in Schedule during configuration.


## Installing for testing<a name="Installing-for-testing"></a>


i. Log in to Azure portal using the URL - [Azure Portal-Home](https://ms.portal.azure.com/?feature.BringYourOwnConnector=true&feature.experimentationflights=ConnectorsKO#home).

ii. Go to Microsoft Sentinel -> Data Connectors

iii. Click the “import” button at the top and select the json file `BitSight_API_FunctionApp.json` downloaded on your local machine from Github.

iv. This will load the connector page and rest of the process will be same as the Installing for users guideline above.


Each invocation and its logs of the function can be seen in Function App service of Azure, available in the Azure Portal outside the Microsoft Sentinel.

i. Go to Function App and click on the function which you have deployed, identified with the given name at the deployment stage.

ii. Go to Functions -> Any of our function -> Monitor

iii. By clicking on invocation time, you can see all the logs for that run.

**Note: Furthermore we can check logs in Application Insights of the given function in detail if needed. We can search the logs by operation ID in Transaction search section.**