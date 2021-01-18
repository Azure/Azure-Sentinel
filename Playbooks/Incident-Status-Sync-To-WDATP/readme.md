
This playbook will disable the user in Azure Active Directoy and add a comment to the incident

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUser%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUser%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>





Description

A question that always get flagged when working on Azure sentinel specially in organizations where implementation of E5 is adopted at full scale that is:

When closing an incident in Azure sentinel will incident status get closed in let's say MDATP portal as well ?

The short answer is NO it simply won't! and this answer is applicable only to the very moment this article was written as Microsoft is bringing a lot of new features every second!

Likely there is an easy way to do this and it's also meeting best practices by utilizing the playbooks in Azure sentinel itself.

an Azure Sentenil incidents we can use the attribute VendorOriginID  to correlate the incident with
its corresponding alert or incident in other products like wdatp.
So apparently this is the matching attribute that we can use to build up the playbook.
looking at the steps:

Step#1: When a response to an Azure Sentinel alert is triggered:

This step simply implies when the playbook will be triggered

Step#2: Alert - Get incident

In this step we will need to fill it up with dynamic attributes
Step#3: Update incident

In this step we set the incident status to "Closed" in Sentinel
Step#4: Condition:

Now it's time to set the condition and actions required to finish the task.

the condition i used here is to set dynamic content attribute to: "Incident Alert product names"

if condition is met then next step would be to set the corresponding alert status in MDATP to "Resolved"

Here we will come to use the actual matching attribute called "provider alert ID" which is exactly same as VendorOriginID mentioned above
Note also here that we retrieved attribute "provider Alert ID" and used the MDATP connector to pass it to. So it's exactly like sending a query to MDATP 

