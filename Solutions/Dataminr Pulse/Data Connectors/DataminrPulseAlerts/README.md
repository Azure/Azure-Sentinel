# Dataminr Pulse Data Connector
* [Introduction](#Introduction)
* [Description](#Description)
* [Folders](#Folders)
* [Prerequisites](#Prerequisites)
* [Configuration](#Configuration)
* [Installing for the users](#Installing-for-the-users)
* [Installing for testing](#Installing-for-testing)

## Introduction<a name="Introduction"></a>

This folder contains the Azure function Http Trigger code for DataminrPulseAlerts Data Connector. The connector will run automatically when Alerts data will be pushed via RTAP and will ingest the data into Microsoft Sentinel logs custom table `DataminrPulse_Alerts_CL`. To receive data from Dataminr RTAP, user must need to run this Data Connector manually once to add integration settings for deployed function app in Dataminr.

## Description<a name="Description"></a>

Dataminr Pulse Alerts Data Connector brings our AI-powered real-time intelligence into Microsoft Sentinel for faster threat detection and response.

## Folders<a name="Folders"></a>

1. `DataminrPulseAlerts/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies.
2. `DataminrPulseAlertsHttpStarter/` - This contains the azure function source code to receive data via webhook request and invoke Orchestrator function.
3. `DataminrPulseAlertsSentinelOrchestrator/` - This contains the azure function source code to invoke Activity function as per requirement and pass the data, received as input to Orchestrator context to an activity function.
4. `DataminrPulseAlertsManualActivity/` - This contains the azure function source code to add integration settings in dataminr for provided functionapp url.
5. `DataminrPulseAlertsSentinelActivity/` - This contains the azure function source code to process alerts data received as input to activity function and post it into Microsoft Sentinel.
6. `shared_code/` - This contains the constants, logger and exceptions used in each azure function.

## Prerequisites<a name="Prerequisites"></a>
1. Users must have a valid Dataminr Pulse API **client ID** and **secret** to use this data connector.
2. One or more Dataminr Pulse Watchlists must be configured in the Dataminr Pulse website.

## Configuration<a name="Configuration"></a>

### STEP 1 - Credentials for the Dataminr Pulse Client ID and Client Secret
1. Obtain Dataminr Pulse user ID/password and API client ID/secret from your Dataminr Customer Success Manager (CSM).

### STEP 2 - Configure Watchlists in Dataminr Pulse portal.
1. Login to the Dataminr Pulse [website](https://app.dataminr.com).
2. Click on the settings gear icon, and select “Manage Lists.”
3. Select the type of Watchlist you want to create (Cyber, Topic, Company, etc.) and click the “New List” button.
4. Provide a name for your new Watchlist, and select a highlight color for it, or keep the default color.
5. Configure the companies, topics, geolocations, alert priority, and delivery settings for this Watchlist.
6. When you’re done configuring the Watchlist, click Save to save it.



## Installing for the users<a name="Installing-for-the-users"></a>

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in Data connectors section of Microsoft Sentinel.

i. Go to Microsoft Sentinel -> Data Connectors

ii. Click on the DataminrPulseAlerts, connector page will open.

iii. Click on Deploy to Azure 
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-DataminrPulseAlerts-azuredeploy)


It will lead to a custom deployment page where user need to select **Subscription**, **Resource Group** and **Location**.
And need to enter below information to configure DataminrPulse data connector for Microsoft Sentinel.
```Function Name
   BaseURL
   ClientId
   ClientSecret
   AlertsTableName
   LogLevel
   Workspace ID
   Workspace Key
```
### **Post Deployment Steps**<a name="Post Deployment Steps"></a>

**Get the Function app endpoint**
    
    1. Go to Azure function Overview page and Click on "Functions" in the left blade.
    2. Click on the function called "DataminrPulseAlertsHttpStarter".
    3. Go to "GetFunctionurl" and copy the function url.
    4. Replace "{functionname}"  with "DataminrPulseAlertsSentinelOrchestrator" in copied function url.

**Steps to add integration settings in Dataminr by running function app manually.**

    1. Within Microsoft Sentinel, go to Azure function apps then `<your_function_app>` Overview page and Click on "Functions" in the left blade.
    2. Click on the function called "DataminrPulseAlertsHttpStarter".
    3. Go to "Code + Test" and click "Test/Run".
    4. Provide the necessary details as mentioned below:
        - HTTP Method : "POST"
        - Key : default(Function key)
        - Query : Name=functionName ,Value=DataminrPulseAlertsSentinelOrchestrator
        - Reuqest Body (case-sensitive): 
            {
                "integration-settings": "ADD",
                "url": "<URL part from copied Function-url>",
                "token": "<value of code parameter from copied Function-url>"
            }
    5. After providing all required details, click "Run".
    6. You will receive an integration setting ID in the HTTP response with a status code of 200.
    7. Save "Integration ID" for future reference.

## Installing for testing<a name="Installing-for-testing"></a>


i. Log in to Azure portal using the URL - [https://portal.azure.com/?feature.BringYourOwnConnector=true&feature.UseKoBladeForE2E=true#home](https://portal.azure.com/?feature.BringYourOwnConnector=true&feature.UseKoBladeForE2E=true#home).

ii. Go to Microsoft Sentinel -> Data Connectors

iii. Click the “import” button at the top and select the json file `DataminrPulseAlerts_FunctionApp.json` downloaded on your local machine from Github.

iv. This will load the connector page and rest of the process will be same as the Installing for users guideline above.


The connector should ingest the data into the logs when it receives data from Dataminr RTAP via Http request.

Each invocation and its logs of the function can be seen in Function App service of Azure, available in the Azure Portal outside of Microsoft Sentinel.

i. Go to Function App and click on the function which you have deployed, identified with the given name at the deployment stage.

ii. Go to Functions -> DataminrPulseSentinelConnector -> Monitor

iii. By clicking on invocation time, you can see all the logs for that run.

**Note: Furthermore we can check logs in Application Insights of the given function in detail if needed. We can search the logs by operation ID in Transaction search section.**
