# Create Microsoft Sentinel Incident on Missing Data Source Solution
Author: John Joyner

This solution will create a Microsoft Sentinel incident when one or more data sources are discovered to have sent no data in the previous 24 hours.

Consumption plan Logic App has one (1) trigger and fourteen (14) steps.

### Click to Deploy to Azure

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-Incident-on-missing-Data-Source%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-Incident-on-missing-Data-Source%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

### IMPORTANT POST DEPLOYMENT STEPS

1. The Logic App will initially include API connections authorized by the authenticated user performing the deployment. Each of the two (2) API connections must be individually  authorized (details provided below in this README). <em>The Logic App will fail until this step is performed.</em>

2. The "<b>Initialize variable - Sentinel Data Sources</b>" step of the Logic App must be customized with the data sources expected in the environment (details provided below in this README). <em>Sentinel incidents created by the Logic App will be inaccurate until this step is completed.</em>

### Overview of the steps the Logic App works through 

The Logic App loops through each data source (specified in the first 'Initialize variable' task in the Logic App) and checks for that data type in the Log Analytics workspace, appending missing data source name(s) to an array. If any data source is found to have no recent data in the workspace, a low severity Microsoft Sentinel incident is created that includes an HTML table of the array listing the missing data source name(s).

![0-appoverview](../Create-Incident-on-missing-Data-Source/images/0-appoverview.png)

### The Logic App is activated by a Recurrence trigger whose frequency of execution can be adjusted to your requirements:

![1-Recurrence](../Create-Incident-on-missing-Data-Source/images/1-Recurrence.png)

### Since the Logic App is being deployed from an ARM template you will need to make connections to Log Analytics and Microsoft Sentinel before the Logic App can work in your environment. 

1. Before using the Logic App for the first time, navigate to the Logic App -> Development Tools -> API connections menu.
2. Select each of the two (2) API connections, and for both connections press the Authorize button, authenticate with your user account, and push the Save button. 

 ![2-Authorize-API-Connections](../Create-Incident-on-missing-Data-Source/images/2-Authorize-API-Connections.png)

Tip: After verifying the Logic App in your environment, you can swap out the user-based API connections with a service principal or a system-assigned or user-assigned managed identity. Assign RBAC '<b>Log Analytics Reader</b>' and '<b>Microsoft Sentinel Contributor</b>' roles to the service principal or Logic App managed system identity at the Management Group, Subscription, or Resource Group level.

### The "Initialize variable - Sentinel Data Sources" task in the Logic App must be customized for your environment.

The variable is pre-populated with a number of data sources to get you started. Delete the data sources you don't have in your environment and add those not already in the list. You should include all the data sources in your Microsoft Sentinel -> Configuration -> Data Connectors list as well as Azure Monitor -> Settings -> Data Collection Rules.

Each data source is specified as an array with two "attribute : value" pairs like this:

```
   {
      "kql": "AWSCloudTrail",
      "name": "Amazon Web Services"
   },
```
To add additional data sources, the "kql" value is what you would use in the Log Analytics log viewer to query for that data source, also known as the Table name, possibly augmented with one or more "| where" filters. The "name" value is any text string that is meaningful to you to describe that data source.

If any KQL or Name value contains quote marks ("), these must be escaped with a backslash {\\}, so that you actually have backslash-quote (\\") specified in the Logic App. See this example where the KQL contains a "| where" filter with quote marks:

```
   {
      "kql": "CommonSecurityLog | where DeviceVendor == \"Fortinet\" | where DeviceProduct startswith \"Fortigate\"",
      "name": "Fortinet"
   },
```

Remember that each array needs a comma after the closing curly bracket, except for the last array in the list which does not have a comma.

  ![3-InitializeVariable](../Create-Incident-on-missing-Data-Source/images/3-InitializeVariable.png)

### Below is an example Microsoft Sentinel incident created by the Logic App:

   ![4-SampleIncident](../Create-Incident-on-missing-Data-Source/images/4-SampleIncident.png)
