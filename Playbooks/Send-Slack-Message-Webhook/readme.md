# Send Slack Message Via Webhook
author: Zachi Neuman

This playbook will be sending slack with basic incidents details (Incident title, severity, tactics, link,…) when incident is created in Azure Sentinel.
The playbook includes functionality to:
1. Close Incident As False Positive
2. Close Incident As Benign Positve
3. Change Incident Status To Active
4. White List Entities
<br/><br/>
## Pre-requisites:
Slack application with: 
1. Webhook installed
1.1 How to install webhook - https://api.slack.com/messaging/webhooks
2. Interactivity Enbaled
<br/><br/>
## Deployment:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/Send-Slack-Message-Webhook/incident-trigger/azuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]()

## Post-deployment

### Configure connections
Edit the Logic App or go to Logic app designer.<br/>

### Attach the playbook
After deployment, attach this playbook to an automation rule so it runs when the incident is created.
[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)<br/>
<br/><br/>
## Screenshot
### Playbook screenshoot
### Email screenshot
