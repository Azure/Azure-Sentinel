# Ingestion Cost Alert Playbook

Managing cost for cloud services is an essential part of ensuring that you get maximum value for your investment in solutions running on this computing platform. Azure Sentinel is no different. To help you exercise greater control over your budget for Azure Sentinel  this playbook will send you an alert should you exceed a budget that you define for your Azure Sentinel Workspace within a given time-frame.

## Deployment steps

1. Log into the Azure Portal
2. In the Azure search box type Log Analytics Workspaces


![01-laazureportal](../Send-IngestionCostAlert/images/01-LAAzurePortal.png)


3. Select the Azure Sentinel workspace

![02-laworkspaces](../Send-IngestionCostAlert/images/02-laworkspaces.png)

4. Copy the Subscription ID, Resource group and the Workspace name

### The Logic App is activated by a Recurrence trigger whose frequency of execution can be adjusted to your requirements

![03-Rgselection](../Send-IngestionCostAlert/images/03-rgselection.png)

5. Scroll to the bottom of this document and select Deploy to Azure

![04-Azuredeploy](../Send-IngestionCostAlert/images/04-azuredeploy.png)


6. Log into the Azure portal

7. Enter the following information

-	Subscription: Select the Subscription
-	Resource Group: Select the RG
-	Playbook Name: Enter playbook name
-	Sentinel WS Name: Enter workspace name
-	Sentinel Sub ID: Enter Subscription ID
-	Sentinel ES Resource Group: Enter Resource Group Name
-	Mail List: Enter email address of user(s) that need to get the notification
-	User Name: Enter account with permissions to create a logic app

![05-deploymentscope](../Send-IngestionCostAlert/images/05-deploymentscope.png)

8. Select Review + create + Create
9. Click Go to resource group
10. Click o365-IngestionCostAlert

![06-o365api](../Send-IngestionCostAlert/images/06-o365api.png)


11. Click Test connection failed.

![07-testconnection](../Send-IngestionCostAlert/images/07-testconnection.png)


12. Click Authorize

![08-authorizeAPI1](../Send-IngestionCostAlert/images/08-authorizeAPI1.png)


13. Login into portal again

![09-portalauth](../Send-IngestionCostAlert/images/09-portalauth.png)



14. Click Save

![10-authapisuccess](../Send-IngestionCostAlert/images/10-authapisuccess.png)




15. Click the resource group again

![11-clickrg2](../Send-IngestionCostAlert/images/11-clickrg2.png)




16. Click teams-IngestionCostAlert

![12-teamsapi](../Send-IngestionCostAlert/images/12-teamsapi.png)





17. Click Test connection failed.

![13-teamstestapi](../Send-IngestionCostAlert/images/13-teamstestapi.png)






18. Click Authorize

![14-teamsauthorize](../Send-IngestionCostAlert/images/14-teamsauthorize.png)


19. Login into portal again

![15-teamslogin](../Send-IngestionCostAlert/images/15-teamslogin.png)





20. Click Save

![16-teamsapisave](../Send-IngestionCostAlert/images/16-teamsapisave.png)


21. In the Azure search box type Logic App 

![17-logicappsearch](../Send-IngestionCostAlert/images/17-logicappsearch.png)



22. Select the newly created logic app

![18-logicappfind](../Send-IngestionCostAlert/images/18-logicappfind.png)


23. Click Logic app designer

![19-LAdesigner](../Send-IngestionCostAlert/images/19-LAdesigner.png)

24. Select Price Per GB
25. Change the Type to Float
26. For the value, enter the total cost of Sentinel. This value will consist of the cost of:

-	[Azure Sentinel  Pricing](https://azure.microsoft.com/pricing/details/azure-sentinel/#:~:text=%20Azure%20Sentinel%20pricing%20%201%20Capacity%20Reservations.,an%20Azure%20Monitor%20Log%20Analytics%20workspace...%20More%20)

-	[Azure Monitor- ingestion and retention](https://azure.microsoft.com/pricing/details/monitor/)

These 3 costs should be added together

![20-recurrence](../Send-IngestionCostAlert/images/20-recurrence.png)

27. Select Days in a month and change the days to 31

![21-daysvar](../Send-IngestionCostAlert/images/21-daysvar.png)

28. Select Monthly budget and enter the total monthly budget

![22-totfund](../Send-IngestionCostAlert/images/22-totfund.png)

29. Select Threshold per day and enter the daily limit. To get this value simply divide the total budget from step 29 above by the number of days per month (31) in step 28

![23-daythresh](../Send-IngestionCostAlert/images/23-dailythresh.png)

30. Select Connection

31. Select the account to log in with or add a new connection

![24-connection1](../Send-IngestionCostAlert/images/24-connection1.png)

32. Click Sign-in and log into the account

![25-AMconnection](../Send-IngestionCostAlert/images/25-AMconnection.png)

33. Click For Each -> Condition

35. Enter the email address of the user(s) that will receive the notification. (secops@yourdomain.onmicrosoft.com)
![25-foreach](../Send-IngestionCostAlert/images/25-foreach.png)

35. Click Add an Action

37. Search for “Office365 Outlook”

39. Select “Send an e-mail”

![27-sendmail](../Send-IngestionCostAlert/images/27-sendmail.png)

38. Select “Add an action”
39. In the search box type Teams -> Microsoft Teams

![28-searchteams](../Send-IngestionCostAlert/images/28-searchteams.png)

40. In the search box type Post a message -> Post a message (V3) (preview)

![29-teamspost](../Send-IngestionCostAlert/images/29-teamspost.png)

41. Select the Teams group that will receive the message

42. Select the Team Channel within that teams group

![30-teamsaddress](../Send-IngestionCostAlert/images/30-teamsaddress.png)

43. In the message box type You have exceeded your daily budget 

44. Click the Dynamic content -> Max_per_day

![31-teamsdynamic](../Send-IngestionCostAlert/images/31-teamsdynamic.png)

When complete this section should look as follows:

![32-teamsthresh](../Send-IngestionCostAlert/images/32-teamsthresh.png)

45. Click Save 

![33-saveapp](../Send-IngestionCostAlert/images/33-saveapp.png)


<em>Below is the query being executed in the step above in text format which you can use for validation directly in the Log Analytics query window. Ensure to replace the variables below with actual numbers if running the query within the Log Analytics query window.</em>

```
  let price_per_GB = price_per_GB;
  let how_many_days = days_in_month;
  let total_funding = monthly_budget;
  let max_per_day = toreal(monthly_budget) / toreal(days_in_month);
  Usage
  | where TimeGenerated > startofday(ago(1d))
  | where IsBillable == true
  | summarize AggregatedValue= sum(Quantity) * price_per_GB / 1024
  | where AggregatedValue > max_per_day
```

In this step, the aggregated value obtained from the previous step is compared against the budget value you set and should it exceed the amount then the logic branches to the left and sends out an e-mail or posts a Microsoft Teams message. If you are still within budget, then the logic branches to the right and no message is sent.


   ![34-computation](../Send-IngestionCostAlert/images/34-computation.png)

In the final step below sends out an e-mail to the specified recipient list and a message is posted in a Microsoft Teams channel that you selected earlier


  ![35-sendmessage](../Send-IngestionCostAlert/images/35-sendmessage.png)

  <em>Additional information on cost management can be found in [this document](https://docs.microsoft.com/azure/azure-monitor/platform/manage-cost-storage)</em>
  
  <em>Special thanks to Damon Neal for his documentation template</em>
 



<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-IngestionCostAlert%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2Send-IngestionCostAlert%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
