# Cisco ASA - Create or remove access rules on an interface for IP Addresses

## Summary

This playbook allows blocking/unblocking of IPs in Cisco ASA, using **Access Control Entries** which will be created in an access control list.

When a new Sentinel incident is created, this playbook gets triggered and performs below actions
1. For the IPs we check if they are already directly blocked by an access control entry in the access control list
2. An adaptive card is sent to a Teams channel with information about the incident and giving the option to ignore an IP, or depdening on it's current status block it by adding an access control entry or unblock it by removing an access control entry
    ![Adaptive card](./images/CreateACEInACL-AdaptiveCard.png)
3. Comment is added to Microsoft Sentinel incident.
![playbook overview](./images/CreateACEInACL-AzureSentinel-Comments.png)

**ACE is added to an ACL in Cisco ASA:**
![playbook overview](./images/CreateACEInACL-CiscoASA.png)

**Playbook overview:**

![playbook overview](./images/CreateACEInACL-LogicApp.png)


### Prerequisites
1. **This playbook template is based on Microsoft Sentinel Incident Trigger which is currently in Private Preview (Automation Rules).** You can change the trigger to the Sentinel Alert trigger in cases you are not part of the Private Preview.
2. Cisco ASA custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found in the connector doc page.
3. Cisco ASA needs to have an extended Access Control List configured. Create a new ACL or retrieve the name of an existing ACL. To use Cisco ASDM to configure Extended ACLs, see [Configure Extended ACLs](https://www.cisco.com/c/en/us/td/docs/security/asa/asa914/asdm714/firewall/asdm-714-firewall-config/access-acls.html#ID-2069-0000016d)

### Deployment instructions 
1. Deploy the playbook by clicking on "Depoly to Azure" button. This will take you to deplyoing an ARM Template wizard.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoASA%2FCiscoASA-CreateACEInACL%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoASA%2FCiscoASA-CreateACEInACL%2Fazuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>

2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (ex:CiscoASA-CreateACEInACL)
    * Cisco ASA Connector name : Enter the name of the Cisco ASA custom connector (default value:CiscoASAConnector)
    * Interface ID : The name of the interface you want to create the access rules on.

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams and Cisco ASA (For authorizing the Cisco ASA API connection, the username and password needs to be provided)

#### b. Select Teams channel
The Teams channel to which the adaptive card will be posted will need to be configured.
1. Click the Azure Logic app resource
2. Edit the Logic App
3. Find the 'PostToTeams' action
4. Select a Team and Channel
5. Save the Logic App

#### c. Configurations in Sentinel
1. In Microsoft Sentinel analytical rules should be configured to trigger an incident with IP Entity.
2. Configure the automation rules to trigger this playbook
