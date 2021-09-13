# PaloAlto-PAN-OS Block IP Nested Remediation Playbook

 ## Summary

This playbook allows blocking/unblocking IP addresses in PaloAlto, using **IP Groups**. This allows to make changes on predefined address group, which is attached to predefined security policy rule.

When this playbook gets triggered and it performs below actions:

1. Gets a list of malicious IP address.
2. For each IP address in the list, checks if IP address in blocked in security policy rule or not.
3. If IP address is blocked in security policy rule, then it unblocks that IP address.
4. If IP address is not blocked in security policy rule, then it blocks that IP address.

![PAN-OS](./Images/PlaybookdesignerLight.png)<br>
![PAN-OS](./Images/PlaybookdesignerDark.png)<br>

### Prerequisites 
1. PaloAlto connector needs to be deployed prior to the deployment of this playbook under the same subscription and same resource group. Capture the name of Connector during deployment. Relevant instructions can be found in the connector doc page.
2. Generate an API key.[Refer this link on how to generate the API Key](https://paloaltolactest.trafficmanager.net/restapi-doc/#tag/key-generation)
3. Address group should be created for PAN-OS and this should be used while creating playbooks. 
4. Security policy rule should be created in PAN-OS.

### Deploy Custom Connector

To deploy Palo Alto PAN-OS Custom connector click on the below button.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-PAN-OS%2FPaloAltoCustomConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-PAN-OS%2FPaloAltoCustomConnector%2Fazuredeploy.json) 


### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-IP%2FPaloAlto-PAN-OS-BlockIP-Nested-Remediation%2Fazuredeploy.json)  [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-IP%2FPaloAlto-PAN-OS-BlockIP-Nested-Remediation%2Fazuredeploy.json)


2. Fill in the required parameters:

|Parameter|Description|
|------------|---------------|
|**Playbook Name**|Enter the playbook name here (e.g. PaloAlto-PAN-OS-Remediation)|
|**PAN-OS Connector name**|Enter the name of PAN-OS Connector captured during deployment.|
|**Address group name**|Enter the predefined address group name here to Block IP / Unblock IP.|
    

### Post-Deployment instructions 
#### Authorize connections
Once deployment is complete, you will need to authorize PAN-OS API connection.
1.	Click the PAN-OS connection resource
2.	Click edit API connection
3.	Provide API key
4.	Click Save



## Playbook steps explained

### When the playbook is triggered

The playbook receives list of malicious IP addresses as the input.

### Initialize variables 

   a. Action Name (type-String) - To store action name as block IP or unblock IP
   
   b. Address group Members(type-Array) - To store list of address group members

   c. Address action (type-object) - To store address action in case of success or failure
   
   d. IP Address Action(type-Array) - To store action taken against each IP

### Lists all address objects 
Lists all the address objects present in the firewall

### Lists all security rules
Lists all the security policy rules present in the firewall

### For each-malicious IP
Iterates on the IPs found in this incident (probably one) and performs the following:

#### Filter array of IP address from list of address objects
This filters the list of address objects in which IP is a member

#### Lists all address object groups
Lists all the address object groups present in the firewall

#### Sets variable address group members
This assign list of address group members

#### Compose configured address group
This composes predefined address group

###Filter array IP from list of security rules
Filter array list of security rules in which IP is a member

###Condition to check if the IP present in list of address objects
 
a) If IP is present in list of address objects

   * Condition to check if IP present in predefined address group

        i) If IP present in predefined address group then unreference that IP from the address group. Set action name as UnblockIP.

        ii) If IP not present in predefined address group then append that IP into address group members. Set action name as BlockIP.

b) If IP address is not present in list of address objects then append that IP address to address group member and set action name as BlockIP.  

###Condition to check if IP needs to be blocked

a) If IP needs to be blocked then create new address object for that malicious IP and update the address object group.

b) If IP need not be blocked, then simply update the address object group.

###Update the address action variable according to success or failure.

###Response from playbook is sent to master playbook to generate incident comments.

 
