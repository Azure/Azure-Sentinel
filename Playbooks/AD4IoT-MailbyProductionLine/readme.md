# AD4IoT - Sent an email by production line
Author: Amit Sheps

The following playbook will send mail to notify specific stake holders.<br>
One example can be in the case of specific security team per product line or per physical location. The playbook requires a watchlist which maps between the sensors name and the mail addresses of the alerts stockholders, a sample is provide with the playbook.  

## Prerequisites
* The playbook is applicable for Azure Defender for IoT incidents. Configure an Automation Rule to run a playbook on the relevant IoT incident creation rule.
* Create a Azure Sentinel Watchlist named **MailsBySensor** (sample included) which includes the list of the following:
    * Sensor names parameter name
    * Mail address to be used to send mails
    Example can be found in this folder.


## Screenshots
![screenshot1](./images/MailToStakeholder.png)<br>
![screenshot2](./images/designerOverviewLight.png)<br>


## Deploy to Azure
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAD4IoT-MailbyProductionLine%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAD4IoT-MailbyProductionLine%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>