
Author: Mahmoud Elsayed

## This playbook could be used to sync incident status in Azure sentinel to the corresponding incident in MDATP


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUser%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-AADUser%2Fazuredeploy.json)





**Description**

This playbook is applicable in following scenario:
- MDATP connector is enabled in Azure sentinel
- An analytic rule is configred to log incidenets in sentinel based on received information from MDATP

In this scenario when an incident status changes for example when an incident gets closed or re-opened, the incident status doesn't get propagated and reflected in MDATP.

This playbook represents an example of how to keep incident status in sync between sentinel and MDATP.


The goal is to find a common matching criteria between the two entities. 

If we look at shown example of one incident in sentinel

 ![Picture1](./Graphics/1.gif)

Clicking on the incident and then from the right pane clicking on "Alerts" it opens the following page with the query result as shown in following screens:

![Picture2](./Graphics/2.gif)

![Picture3](./Graphics/3.gif)

The VendorOriginID is the attribute that represents the Alert ID as it is stored in MDATP originally at the source.

So this is the matching attribute will be used to create the playbook with.

This picture shows how the playbook looks like after being created.

![Picture4](./Graphics/4.gif)


Following is the main steps:

**Step#1**: When a response to an Azure Sentinel alert is triggered:

This step is default trigger that has to be used when the playbook will be triggered

**Step#2:** Alert - Get incident

In this step the fields can be filled up with dynamic attributes as shown in the picture

![Picture5](./Graphics/5.gif)



**Step#3:** Update incident

In this step we set the incident status to "Closed" in Sentinel

![Picture6](./Graphics/6.gif)


**Step#4:** Condition:

Now it's time to set the condition and actions required..

The condition used here is to set dynamic content attribute to: "Incident Alert product names"

![Picture7](./Graphics/7.gif)

If condition is met then next step would be to set the corresponding alert status in MDATP to "Resolved"

The actual matching attribute "provider alert ID" that is exactly same as VendorOriginID mentioned above will be used:

![Picture8](./Graphics/8.gif)


Note: attribute "provider Alert ID" was retreived and the MDATP connector was used in background to pass it to. Same result could be obtained when sending a query to MDATP with the specific alert id ed637431102114129586_160070831 in order to set it to "resovled".

**Step#5:** testing the playbook in action:

![Picture9](./Graphics/9.gif)

![Picture10](./Graphics/10.gif)

As shown above it was able to pull the alert ID ed637431102114129586_160070831 that is equal to the VendorOriginID in order to query for it in MDATP and close the alert.

