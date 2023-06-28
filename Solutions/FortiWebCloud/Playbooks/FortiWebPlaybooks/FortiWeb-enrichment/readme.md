# FortiWeb-enrichment Info Playbook
 ## Summary
 When a new Microosft Sentinel incident is created, this playbook gets triggered and performs below actions
 1. Fetches the list of Ip's from incident entites .
 2. Make the APi call to get the latest threat information/details from cloud console and update the same incidents comments with result.
 ![image](https://user-images.githubusercontent.com/97503740/184323073-d3d7e6eb-f40e-42e1-8d2b-ef7f9550e646.png)
![image](https://user-images.githubusercontent.com/97503740/184323351-310a1d97-a541-4204-aa65-06069e5decbe.png)

### Prerequisites 
1. FortiWeb Cloud Custom Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. API key. To get API Key, login into your FortiWeb cloud instance dashboard and navigate to Global --> system settings --> API Key.

### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFortiWebCloud%2FPlaybooks%2FFortiWebPlaybooks%2FFortiWeb-encrichment%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFortiWebCloud%2FPlaybooks%2F%2FFortiWebPlaybooks%2FFortiWeb-encrichment%2Fazuredeploy.json)

2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here (Ex: FortiWeb-BlockIP-URL)
    * Custom Connector Name: Enter the FortiWeb custom connector name here (Ex: FortiWebCloud)

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microosft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for Fortiweb Api  Connection (For authorizing the Fortiweb API connection, API Key needs to be provided)
#### b. Configurations in Sentinel
1. In Microosft Sentinel analytical rules should be configured to trigger an incident with risky URL or IP Address. 
2. Configure the automation rules to trigger this playbook , mapping of IP and URL entities is necessary
