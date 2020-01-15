# Reset-AADPassword
author: Nicholas DiCola

This playbook will reset the user password using Graph API.  It will send the password (which is a random guid) to the user's manager.  The user will have to reset the password upon login.  
NOTE:  You must create an app registration for Graph API with appropriate permissions.  
NOTE:  You will need to add the managed identity that is created by the logic app to the Password Administrator role in Azure AD.

<a href="https://azuredeploy.net/?repository=https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Reset-AADPassword" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FReset-AADPassword%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
