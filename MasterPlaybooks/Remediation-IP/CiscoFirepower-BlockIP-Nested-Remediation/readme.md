# Cisco Firepower - Add IP Addresses to a Network Group object

## Summary

This playbook allows blocking of IPs in Cisco Firepower, using a **Network Group object**. This allows making changes to a Network Group selected members, instead of making Access List Entries. The Network Group object itself should be part of an Access List Entry.

When this playbook gets triggered performs below actions:
1. For the IPs we check if they are already selected for the Network Group object
2. For the IPs not already selected for the Network Group object, add it so it gets blocked
3. Creates a comment for response.<br>


** IP is added to Cisco Firepower Network Group object:**
<br>
![Cisco Firepower Network Group object](./Images/BlockIP-NetworkGroup-CiscoFirepowerAdd.png)

**Plabook overview:**

![Playbook overview](./Images/designerOverviewLight1.png)
![Playbook overview](./Images/designerOverviewLight2.png)
![Playbook overview](./Images/designerOverviewLight3.png)


## Prerequisites
1. Cisco Firepower custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector [doc pages](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/CiscoFirepower/CustomConnector).
2. In Cisco Firepower there needs to be a Network Group object. [Creating Network Objects](https://www.cisco.com/c/en/us/td/docs/security/firepower/630/configuration/guide/fpmc-config-guide-v63/reusable_objects.html#ariaid-title15)

<a name="deployment-instructions"></a>
### Deployment instructions 
1. Deploy the playbook by clicking on "Depoly to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FRemediation-IP%2FCiscoFirepower-BlockIP-Nested-Remediation%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FRemediation-IP%2FCiscoFirepower-BlockIP-Nested-Remediation%2Fazuredeploy.json)

2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (ex:CiscoFirepower-BlockIP-NetworkGroup)
    * Cisco Firepower Connector name: Enter the name of the Cisco Firepower custom connector (default value:CiscoFirepowerConnector)
    * Network Group object name: The name of the Network Group object.

## Post-Deployment instructions 
### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Cisco Firepower (For authorizing the Cisco Firepower API connection, the username and password needs to be provided)
