# Network Session Essentials Solution Summarization capability

This logic app helps to summarize Network session data into custom tables. This would incur additional cost.

 ## Summary
 To ensure good performance of Network Session Essentials solution, summarization capability can be used. This would create various custom tables containing analytics based on different parameters of ASIM Network Session Schema.

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploySummarizationPublic)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/deploySummarizationGov)

2. Fill in the required parameter:
    * Playbook Name: Enter the playbook name here (Ex: SummarizeData)

### Post-Deployment instructions 
#### a. Authorize connections (Perform this action if needed)
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Monitor Logs
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.  Click the Azure Log Analytics Data Collector
7.	Click edit API connection
8.	Add value for workspace id and key which is associated with the Sentinel instance
9.	Click Save
