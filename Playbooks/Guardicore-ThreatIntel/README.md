# Integrating Guardicore Threat Intelligence into Azure Sentinel

Author: Accelerynt

For any technical questions, please contact info@accelerynt.com

This playbook will pull the domain names and IPs from the threat intelligence that Guardicore shares every Sunday. It will create Azure Sentinel Threat Intelligence Indicators with the information gathered and send it to the tiIndicators API. This playbook is configured to run every Monday morning at 6:00 AM EST.

The Guardicore Cyber Threat Intelligence Service [Feed](https://threatintelligence.guardicore.com/download-guardicore-cyber-threat-intelligence-data) is part of the their [Cyber Threat Intelligence Platform](https://threatintelligence.guardicore.com/).




<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGuardicore-ThreatIntel%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/Guardicore-ThreatIntel/azuredeploy.json" target="_blank"><img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/></a>

  
 # 
Click the “Deploy to Azure” button and this will bring you to the Custom Deployment Template.

In the **BASICS** section:  

* Select the “**Subscription**” and “**Resource Group**” from the dropdown boxes you would like the playbook deployed to.  

In the **SETTINGS** section:   

* **Playbook Name**: This can be left as “Guardicore-ThreatIntel” or you may change it.  

Towards the bottom ensure you check the box accepting the terms and conditions and then click on “Purchase”. 

![template](Images/template.png)

The playbook should take less than a minute to deploy. Return to your Azure Sentinel workspace and click on “Playbooks.” Next, click on your newly deployed playbook. Don’t be alarmed to see that the status of the playbook shows failed. We still need to edit the playbook to set up a valid connection on our Microsoft Graph Security connectors.  

![playbookclick](Images/playbookclick.png)

Click on the “Edit” button. This will bring us into the Logic Apps Designer.

![editbutton](Images/editbutton.png)

Click on the bottom left bar labeled “For Each - GC Data: Malicious Domains 1”. 

![logicapp1](Images/logicapp1.png)

Click on the bar labeled “Condition - Check Valid Data 1”. 

![logicapp2](Images/logicapp2.png)

Click on “Connections”.  

![logicapp3](Images/logicapp3.png)

Click on the circled exclamation point under the word "Invalid". 

![logicapp4](Images/logicapp4.png)

This will prompt you to sign in with your credentials.

![logicapp5](Images/logicapp5.png)

You should see the that the “Create tiIndicator 2” box has updated and displays “Connected to GCTI.” Click the X to close the Logic App Designer. There is no need to click a save button. 

![logicapp6](Images/logicapp6.png)

This process will not need to be repeated for the right hand branch. 

# Developer's Note:
The branching for the same outer loops is necessary because not all Guardicore domains and IP addresses are in a format Microsoft Graph will accept as valid. 
The branching allows a domain name and its associated IP addresses to be ingested separately.
This way, an invalid domain name will not negate its associated valid IP addresses, or vice versa.
