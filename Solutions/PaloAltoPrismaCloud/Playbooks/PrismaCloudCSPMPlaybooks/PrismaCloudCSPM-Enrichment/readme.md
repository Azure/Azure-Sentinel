# PrismaCloudCSPM-Enrichment Info Playbook
 ## Summary
 When a new Microsoft Sentinel incident is created, this playbook gets triggered and performs below actions
 1. Fetches the list of assets from incident entities.
 2. Make the API call to get the latest Compliance security posture/details from cloud console and update the same incidents comments with result.
 3. Note : Asset column for which the security posture to be enriched should be mapped with hostname entity while creating analytics rule. 


### Prerequisites 
 1. PrismaCloudCSPM Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
 2. API Key and User ID . To get this, login into your Prisma cloud instance dashboard and navigate to Settings --> Access Control --> Access Keys --> Add
 3. [Important step]Store the API secret key in Key vault then provide the keyvault name and key name of the stored secret during deployment

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPaloAltoPrismaCloud%2FPlaybooks%2FPrismaCloudCSPMPlaybooks%2FPrismaCloudCSPM-Enrichment%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPaloAltoPrismaCloud%2FPlaybooks%2F%2FPrismaCloudCSPMPlaybooks%2FPrismaCloudCSPM-Enrichment%2Fazuredeploy.json)

2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here (Ex: PrismaCloudCSPM-Enrichment).
    * Custom Connector Name: Enter the Prisma cloud custom connector name here (Ex: PrismaCloudCSPMCustomConnector).
    * Keyvault name: Enter the key vault name where secret key is stored.
    * Prisma Secret Name : Your Key name for the stored API secret.
	* Prisma User ID : Enter the prisma user id.

### Post-Deployment instructions 
#### a. Authorize connections (Perform this action if needed)
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for playbooks other API Connection.

#### b. Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with risky asset. 
2. Configure the automation rules to trigger this playbook , mapping of hostname entity is necessary

#### c. Assign Playbook Microsoft Sentinel Responder Role
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

#### D. Assign access policy on key vault for Playbook to fetch the secret key
1. Select the Keyvault resource where you have stored the secret
2. Click on Access policies Blade
3. Click on Create
4. Under Secret permissions column , Select Get , List from "Secret Management Operations"
5. Click next to go to Principal tab and choose your deployed playbook name
6. Click Next leave application tab as it is .
7. Click Review and create
8. Click Create

#  References
 - [Prisma cloud support documentation](https://prisma.pan.dev/api/cloud/cspm/)
