# CybersixgillAlertStatusUpdate
author: Loginsoft

This playbook will update status of Actionable alerts in Cybersixgill Portal. When incident is updated in Microsoft Sentinel, playbook will run and update status Actionable alerts from Cybersixgill Portal 

# Prerequisites
We will need the following data to do one time setup

1. Cybersixgill Client ID (client_id)
2. Cybersixgill Client Secret (client_secret)

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersixgill-Actionable-Alerts%2FPlaybooks%2FCybersixgillAlertStatusUpdate%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https%3A%2F%2Fportal.azure.us%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCybersixgill-Actionable-Alerts%2FPlaybooks%2FCybersixgillAlertStatusUpdate%2Fazuredeploy.json)

# Post-deployment
1. Create new automation rule, ex: CybersixgillStatusUpdateAutomationRule
   * Trigger = When Incident is updated
   * Condition = Status Changed

*Automation rule example*
![](./images/AutomationRuleExampleDark.PNG)
![](./images/PlaybookParametersDark.PNG)


![](./images/AutomationRuleExampleLight.PNG)
![](./images/PlaybookParametersLight.PNG)