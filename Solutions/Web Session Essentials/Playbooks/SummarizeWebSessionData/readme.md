# Web Session Essentials Summarization capability

This logic app helps to ingest summarized web session data into custom tables. Please note - enabling this playbook would incur additional cost.

 ## Summary
 To ensure good performance of Web Session solution, summarization capability can be used. This would create four custom tables containing analytics based on different parameters of ASIM Web Session Schema. This playbook will create the following four tables in your Log Analytics Workspace:
 * WebSession_Summarized_SrcInfo_CL
 * WebSession_Summarized_SrcIP_CL
 * WebSession_Summarized_DstIP_CL
 * WebSession_Summarized_ThreatInfo_CL

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/deploywebsessionDataSummarizationPlaybookPublic)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/deploywebsessionDataSummarizationPlaybookGov)

2. Fill in the required parameter:
    * Playbook Name: Enter the playbook name here (Ex: SummarizeWebSessionData)

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