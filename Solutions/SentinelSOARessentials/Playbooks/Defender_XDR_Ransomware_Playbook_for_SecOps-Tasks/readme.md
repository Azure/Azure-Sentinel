# Defender_XDR_Ransomware_Playbook_for_SecOps-Tasks
author: Benji Kovacevic

This playbook add Incident Tasks based on Microsoft Defender XDR Ransomware Playbook for SecOps. This playbook will walk the analyst through four stages of responding to a ransomware incident: containment, investigation, eradication and recovery, and prevention. The step-by-step instructions will help you take the required remedial action to protect information and minimize further risks.

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FDefender_XDR_Ransomware_Playbook_for_SecOps-Tasks%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSentinelSOARessentials%2FPlaybooks%2FDefender_XDR_Ransomware_Playbook_for_SecOps-Tasks%2Fazuredeploy.json)
<br><br>

# Post-deployment
1. Assign Microsoft Sentinel Responder role to the managed identity. To do so, choose Identity blade under Settings of the Logic App.
2. Assign playbook to the automation rule. - https://learn.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook?tabs=LAC<br>
Conditions<br>
    Incident provider > Equals > Microsoft Defender XDR<br>
    ![SentinelIncident](./images/automationRuleDark.jpg)<br><br>
    
## Playbook will run if the alert has any of these keywords:<br>
    1. Ransomware
    2. ransomware

# Screenshots

**Playbook** <br>
![playbook screenshot](./images/playbookDark.jpg)<br>

**Microsoft Sentinel Incident Tasks**<br>
![SentinelIncident](./images/tasksDark.jpg)
