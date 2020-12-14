# Connector Health Push Notification Solution
This enhanced solution builds on the existing “Connector Health Workbook” described in this video: [https://www.youtube.com/watch?v=T6Vyo7gZYds] .The Logic App leverages  underlying queries to provide you with an option to configure “Push notifications” to e-mail or a Microsoft Teams channel based on user defined anomaly scores as well as time since the last “Heartbeat” from Virtual Machines connected to the workspace. The solution consists of a logic app triggered by a scheudled rule. Below is a detailed description of how the rule and the logic app are put together. 

### Create an analytic rule that will trigger in case of an anomaly

![0-analyticrule](../Send-ConnectorHealthStatus/images/0-analyticrule.png)


### The logic app is triggered by the scheduled Analytic with the below properties:

![1-rulelogic](../Send-ConnectorHealthStatus/images/1-Rulelogic.png)

### In the “Set rule logic” section paste the query below and adjust the “UpperThreshold” & “LowerThreshold” variables as needed:

```
let UpperThreshold = 3.0; // Upper Anomaly threshold score
let LowerThreshold = -3.0; // Lower anomaly threshold score
let TableIgnoreList = dynamic(['SecurityAlert', 'BehaviorAnalytics', 'SecurityBaseline', 'ProtectionStatus']); // select tables you want to EXCLUDE from the results
union withsource=TableName1 *
| make-series count() on TimeGenerated from ago(14d) to now() step 1d by TableName1
| extend (anomalies, score, baseline) = series_decompose_anomalies(count_, 1.5, 7, 'linefit', 1, 'ctukey', 0.01)
| where anomalies[-1] == 1 or anomalies[-1] == -1
| extend Score = score[-1]
| where Score >= UpperThreshold or Score <= LowerThreshold
| where TableName1 !in (TableIgnoreList)
| project TableName=TableName1, ExpectedCount=round(todouble(baseline[-1]),1), ActualCount=round(todouble(count_[-1]),1), AnomalyScore = round(todouble(score[-1]),1)
```

### The Logic App is then attached to the scheduled rule to be triggered by an alert

 ![2-Attachtopb](../Send-ConnectorHealthStatus/images/2-Attachtopb.png)

### Details of the steps within the Logic App itself:

  ![3-LAHLview](../Send-ConnectorHealthStatus/images/3-LAHLview.png)

### When a response to an Azure Sentinel alert is triggered

  ![4-AlertTrigger](../Send-ConnectorHealthStatus/images/4-AlertTrigger.png)

### Parse JSON to extract extended alert properties

   ![5-ParseJSON](../Send-ConnectorHealthStatus/images/5-ParseJSON.png)

### Obtain incident details
   ![6-Alert-getincident](../Send-ConnectorHealthStatus/images/6-Alert-Getincident.png) 

### Execute query against workspace to detect potential anomalies

   ![7-IngestionAnomalyQuery](../Send-ConnectorHealthStatus/images/7-IngestionAnomalyQuery.png)

### Execute query against worksapce to detect potential VM connectivity issues
   ![8-HeartbeatQuery](../Send-ConnectorHealthStatus/images/8-HeartbeatQuery.png)

### To adjust the lookback period for the last heartbeat received from VMs in the workspace, change the “| where LastHeartbest < ago(5h)” line in the query above

### Send out the results of the query to the security engineering team as a summarized HTML table

   ![9-Sendemail](../Send-ConnectorHealthStatus/images/9-SendEmail.png)

### Below is a sample output of the push notification to security engineers
   ![10-SampleEmail](../Send-ConnectorHealthStatus/images/10-SampleEmail.png)


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-ConnectorHealthStatus%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2Send-ConnectorHealthStatus%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

<em>This solution was built in close collaboration with Jeremy Tan, Benjamin Kovacevic & Javier Soriano</em>
