# Azure Firewall - Add IP Address to Threat Intel Allow list

 ## Summary

2-3 Sentences about what this playbook does.

When a new Azure Sentinel incident is created, this Playbook is triggered and performs the following: (general main steps)
1. step 1
1. step 2 
1. step 3
1. ...

![Screenshot of the Logic Apps desginer](./designerScreenShot.PNG)<br><br>

any more screenshots relevant, for example:
**This is the adaptive card SOC will recieve when playbook is triggered:**<br><br>
![Adaptive Card example](./AdaptiveCard.jpg)

### Prerequisites 
1. The custom connector needs to be deployed prior to the deployment of this playbook under the same subscription. Relevant instructions can be found in the connector doc page.
1. ...


### Deployment instructions 
1. Deploy the playbook by clicking on "Depoly to Azure" button. This will take you to deplyoing an ARM Template wizard.


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F --- path ---azuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F --- path ---azuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>

2. Fill in the required paramteres:
    * Parameter 1 (example input: ...)
    * Parameter 2 (example input: ...)

### Post-Deployment instructions 

<br>**Authorize connections**

Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connection 


### Configurations in Azure Sentinel
1. Enable Azure Sentinel Analytics rules that create alerts and incidents which includes the relevant entities.
1. Configure automation rule(s) to trigger the playbooks.


## Playbook steps explained

Explain the steps of the playbook, so users who wants to reverse engineer it, make changes or use it as inspiration understand the logic.