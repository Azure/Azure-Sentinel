# PaloAlto-PAN-OS-GetURLCategoryInfo Playbook OnPrem version
 ## Summary
 When a new sentinal incident is created, this playbook gets triggered and performs below actions:
 1. Fetches the address group details and URL filtering category information from PAN-OS
 2. Updates all the collected information in incident


![PaloAlto-PAN-OS-GetURLCategoryInfo](./designerscreenshot.PNG)<br>
### Prerequisites 
1. PAN-OS Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Generate an API key. [Refer this link on how to generate the API Key](https://paloaltolactest.trafficmanager.net/restapi-doc/#tag/key-generation)

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (e.g. PAN-OS Playbook)
    * KeyVaultName: Name of Azure Key Vault that will store X-PAN-KEY
    * secretValue: value of X-PAN-KEY
    * OnPremiseGatewayName: On-premises data gateway that will be used with PaloAlto connector.
    
### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connection such as Teams connection.

#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger this playbook


#### c. Configuration of Azure Key Vault
1. Navigate to new automatically created Azure Key Vault. Name of Key Vault is defined in playbook parameters.
   ![Key Vault configuration](./images/KeyVault.png)
2. Create new Access Police with secret Get permission
   ![Secret permission creation](./images/CreatePolice.png)
3. Find principal by playbook name and select it
4. Click Create

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2Fsocprime%2FAzure-Sentinel%2Fraw%2FPAN-OS-OnPremCustomConnector%2FPlaybooks%2FPaloAlto-PAN-OS%2FPlaybooksOnPrem%2FPaloAlto-PAN-OS-GetURLCategoryInfo%2Fazuredeploy.json)  
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2Fsocprime%2FAzure-Sentinel%2Fraw%2FPAN-OS-OnPremCustomConnector%2FPlaybooks%2FPaloAlto-PAN-OS%2FPlaybooksOnPrem%2FPaloAlto-PAN-OS-GetURLCategoryInfo%2Fazuredeploy.json)

## Playbook steps explained

### When Azure Sentinel incident creation rule is triggered

Azure Sentinel incident is created. The playbook receives the incident as the input.

### Get Secret
Gets X-PAN-KEY from created Azure Key Vault

### Entities - Get URLs

Get the list of risky/malicious URLs as entities from the Incident

### List-address objects

Playbook uses "List address objects" action to get address object details from PAN-OS

### List URL filtering category information

Playbook uses "List URL filtering category information" action to get URL filtering category details from PAN-OS
### For each-risky URL received from the incident
Iterates on the URLs found in this incident (probably one) and performs the following:

1. For the risky URL, Filter URL from list of address objects action to get specific address object details from PAN-OS

   a. Compose body of address object where URL is a member for updating incident with address object details

 2. Create HTML table for URL category information such as name, location and description

 3. Add a comment to the incident with the information below:

     a. User information collected by "List address obects" action from PAN-OS such as

    *  name, location, description and URL
    
     
     b. URL filtering category information collected by "List URL filtering category information" action from PAN-OS such as

    * name, location and description

