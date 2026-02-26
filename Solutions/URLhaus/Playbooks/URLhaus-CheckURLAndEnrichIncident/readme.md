# URLhaus-CheckURLAndEnrichIncident
 ## Summary
 Once a new sentinal incident is created, this playbook gets triggered and performs the following actions:
 1. [Gets Information](https://urlhaus-api.abuse.ch/#urlinfo) from URLhaus by URL`s, provided in the alert custom entities. 
 2. Enriches the incident with the obtained info.

<img src="./playbook_screenshot.png" width="80%"/><br>
### Prerequisites 
1. URLhausAPI Custom Connector has to be deployed prior to the deployment of this playbook under the same subscription.

### Deployment instructions 
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Faverbn%2FAzure-Sentinel%2FURLhaus-Connector-and-Playbooks%2FSolutions%2FURLhaus%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Faverbn%2FAzure-Sentinel%2FURLhaus-Connector-and-Playbooks%2FSolutions%2FURLhaus%2FPlaybooks%2Fazuredeploy.json)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Faverbn%2FAzure-Sentinel%2FURLhaus-Connector-and-Playbooks%2FSolutions%2FURLhaus%2FPlaybooks%2FURLhaus-CheckURLAndEnrichIncident%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FURLhaus%2FPlaybooks%2FURLhaus-CheckURLAndEnrichIncident%2Fazuredeploy.json)


### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, authorize each connection.

1. Open playbook which has been deployed
2. Click API connection on left side blade
3. Click the Azure Sentinel connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for URLhausAPI connector API Connection
#### b. Configurations in Sentinel
1. In Azure sentinel, analytical rules should be configured to trigger an incident. 
2. Configure the automation rules to trigger the playbook.
