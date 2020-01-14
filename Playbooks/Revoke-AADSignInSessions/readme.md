# Revoke-AADSignInSessions
author: Nicholas DiCola

This playbook will revoke all signin sessions for the user using Graph API using a Beta API.  It will send and email to the user's manager. NOTE:  You must create an app registration for graph api with appropriate permissions.  
NOTE:  You will need to add the managed identity that is created by the logic app to the Password Administrator role in Azure AD.

<a href="https://azuredeploy.net/?repository=https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Revoke-AADSignInSessions" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRevoke-AADSignInSessions%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
