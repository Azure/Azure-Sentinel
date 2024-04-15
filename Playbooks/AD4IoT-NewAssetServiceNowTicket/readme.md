# AD4IoT - Create ServiceNow record for a new asset
Author: Amit Sheps

Normally, the authorized entity to program a PLC is the Engineering Workstation, to program a PLC attackers might create a new Engineering Workstation to create malicious programing. The following playbook will open a ticket in ServiceNow each time a new Engineering Workstation is detected.  
This playbook parses explicitly the IOT device entity fields. 

## prerequisites
• The playbook is applicable for Azure Defender for IoT incidents  
• Automation rule for the specific incidents which reference alerts with the text "new"


## screenshots
![screenshot1](./images/ticketSnow.png)<br>
![screenshot2](./images/designerOverviewLight.png)<br>

## Deploy to Azure
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAD4IoT-NewAssetServiceNowTicket%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAD4IoT-NewAssetServiceNowTicket%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>