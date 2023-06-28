# Entrust-Enrichment of User Details Playbook - entity
 ## Summary
 When a Soc analyst, triggered this playbook over some name entity then Playbook performs below actions
 1. Fetches the user details, user group and roles details from Entrust
 2. Adds a rich comment to the incident associated with entity with all the collected information
    ![Comment example](./Images/Entrust-EnrichUser-EntityTrigger_incident_comment.png)

![Playbook Designer view](./Images/Entrust-EnrichUser-EntityTrigger.png)<br>

### Prerequisites 
1. User should be having an active subscription of product to open the product documentation.
2. For Json API keys, Kindly login to entrust Identity as a service portal.
3. Then click on left burger icon and Go to Applications under Resources.
4. click on "+" Button and search for Administration API.
5. Configure that and at the end save the Json object of API keys.
6. Make a note of application id and hostname.
7. Store the Shared Secret Key in key vault Secrets. 

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FEntrustIdentityAsaService%2FPlaybooks%2FEntrustPlaybooks%2FEntrust-EnrichIncidentWithUserDetails%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FEntrustIdentityAsaService%2FPlaybooks%2FEntrustPlaybooks%2FEntrust-EnrichIncidentWithUserDetails%2Fazuredeploy.json)

2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex:Entrust-EnrichIncidentWithUserDetails)
	* Entrust App ID: Enter the Entrust Application ID here
	* Key vault name: Enter the playbook name here
	* Entrust Secret Key Name: Enter the Entrust Secret Key name here
	* Host End Point: Enter the Host End Point here (Ex:<Organization>.us.trustedauth.com)
    
### Post-Deployment instructions 
#### a. Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with risky user account.
2. Configure the automation rules to trigger this playbook.
3. Proper Entity mapping is needed for making a successful run of playbook.

#### b. Assign Playbook Microsoft Sentinel Responder Role
1. Select the Playbook (Logic App) resource
2. Click on Identity Blade
3. Choose System assigned tab
4. Click on Azure role assignments
5. Click on Add role assignments
6. Select Scope - Resource group
7. Select Subscription - where Playbook has been created
8. Select Resource group - where Playbook has been created
9. Select Role - Microsoft Sentinel Responder
10. Click Save (It takes 3-5 minutes to show the added role.)

#### c. Assign access policy on key vault for Playbook to fetch the secret key
1. Select the Key vault resource where you have stored the secret
2. Click on Access policies Blade
3. Click on Create
4. Under Secret permissions column , Select Get , List from "Secret Management Operations"
5. Click next to go to Principal tab and choose your deployed playbook name
6. Click Next leave application tab as it is.
7. Click Review and create
8. Click Create

#  References
 - [Entrust Product Review](https://www.entrust.com/-/media/documentation/datasheets/entrust-identity-as-a-service-ss.pdf)
 - [Entrust documentation](https://www.entrust.com/documentation)
