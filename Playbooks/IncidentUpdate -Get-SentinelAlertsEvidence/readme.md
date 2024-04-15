# IncidentUpdate -Get-SentinelAlertsEvidence

This playbook will run on a time schedule base (every hour) and it will check for any incident that was updated (in the last hour) in your Sentinel workspace by Sentinel Alerts. <br>
It will then automatically attach the new alert evidence from the updated Azure Sentinel incident (from the last hour) and send the evidence to an Event Hub that can be consumed by a 3rd party SIEM solution.


Author: Naomi Christis and Yaniv Shasha

Deploy the solution
1.	Create an Event Hub using the article "Create an event hub using Azure portal" <br>
https://docs.microsoft.com/azure/event-hubs/event-hubs-create  or use an existing Event Hub.

2.	Deploy the playbook to your environment

3.	Once the playbook is deployed; modify the required connection to Azure Monitor Logs <br>(This means configuring the connection to your workspace so we can query for the updated Azure Sentinel incidents).<br>

4.	Next, configure the connection to your event hub (in the "send event" actions; use your Event Hub from step 1.) <br>


