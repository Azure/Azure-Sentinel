#  Close-SentinelIncident-From-Snow

Author: Yaniv Shasha
This Logic App  act as listener for a incident close event in ServiceNow and will close the incident in Sentinel.

 

## Closing the incident in Azure Sentinel when it is closed in ServiceNow requires two components:
1.	A Business Rule in ServiceNow that run custom JS code when the incident is closed.
2.	A Logic App in Azure Sentinel that waits to the Business Rule POST request.<br>


 ![Picture0](./Graphics/diag.GIF)




**The playbook, available here and presented below, works as follows:**
1.	Triger when an HTTP POST request hits the endpoint (1)
2.	Get relevant properties from the ServiceNow Incident. 
3.	Close the incident on Azure Sentinel (4)
4.	Add comment with the name of the user who closed the incident in ServiceNow into an Azure sentinel incident comment (5) 

 ### After Deploying the logicApp you will see the above workflow.

 ![Picture1](./Graphics/playbook2_numbers.GIF)
**Deploying the solution**:

This flow assume that customer use the above logic app [found here](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/Open-SNOW-Ticket) to export the incident into ServiceNow.

The incident properties that exported from Azure sentinel into ServiceNow incident page looks:

![Picture1](./Graphics/SNOW-Incident-View_visual.GIF)

1.	Copy the HTTP endpoint URL from the Logic App trigger part.

![Picture1](./Graphics/http_trigger.GIF)

2.	In “run query and list results” (2) authenticate with user that has log analytics read permission or Azure Sentinel Reader role as a minimum requirement.
3.	In “get incident – bring fresh ETAG” (3) authenticate to AAD APP with a user that has an Azure Sentinel Reader role, or with a Managed identity with the same permission.
4.	On the close incident step (4) we will need to use a user that has an Azure Sentinel Responder role as the identity for 
5.	On “add comment to incident” (5) use a user that has an Azure Sentinel Contributor account.


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FClose-SentinelIncident-fromSNOW%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
    
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FClose-SentinelIncident-fromSNOW%2Fazuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
    
</a>
