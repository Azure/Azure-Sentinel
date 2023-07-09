# Send-UnhealthyAzureArcResourceAlert
author: Laraib khan

This playbook will qyery Low analytics workspace about each Azure Arc-enabled resource/server that has had its health status change to "Unavailable" in the past day and has been in that state for more than 30 minute and Send that alert via Email.

##Edit *Run query and list results* action 
Select your own
- Subcription
- Resource Group
- Resource Type
- Resource Name

![screenshot](.images/subscription.png)


##Edit *Send an Email* Action
Replace <email-id@domain.com> to your own choice of email address.
![screenshot](.images/email.png)


# Deploy to Azure
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-UnhealthyAzureArcResourceAlert%2Fazuredeploy.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-UnhealthyAzureArcResourceAlert%2Fazuredeploy.json" target="_blank">
<img src="https://aka.ms/deploytoazuregovbutton"/>
</a>