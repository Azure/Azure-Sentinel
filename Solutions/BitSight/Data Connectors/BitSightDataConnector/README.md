# BitSight Data Connector
* [Introduction](#Introduction)
* [Folders](#Folders)
* [Installing for the users](#Installing-for-the-users)
* [Installing for testing](#Installing-for-testing)

## Introduction<a name="Introduction"></a>

This folder contains the Azure function time trigger code for BitSight Data Connector. The connector will run periodically and ingest the BitSight data into the Microsoft Sentinel logs custom tables.
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
Workspace ID  | None
Workspace Key  | None
API_token  | None
Companies  | ALL
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
Log Level  | DEBUG
Bitsight Schedule  | 0 0 0 * * *

The connector should start ingesting the data into the logs at every time interval specified in Bitsight Schedule during configuration.


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