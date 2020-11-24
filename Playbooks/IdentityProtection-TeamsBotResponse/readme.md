# Identity Protection - Microsoft Teams Response
author: Lior Tamir

This playbook uses Azure Identity Protection features in order to responde to risky users.
Attach this playbook to alert creation rules which expects to have entities of type Account attached to. 
When a new Azure Sentinel alert is created, the playbook iterates over the identities involved in the alert.
The Microsoft Teams bot will post an adaptive card in the SOC channel, including the potential risky user information given by Azure AD Identity Protection. It will offer to configure the response on the Azure Sentinel incident and Identity Protection risky user with few clicks, directly from Teams.

Note: Azure AD Identity Protection is a premium feature. You need an Azure AD Premium P1 or P2 license to access the riskDetection API (note: P1 licenses receive limited risk information). The riskyUsers API is only available to Azure AD Premium P2 licenses only.

<br><br>
Overall:
<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/IdentityProtection-TeamsBotResponse/images/designerView.png"/>
<br><br>
Card to be sent by Microsoft Teams bot:
<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/IdentityProtection-TeamsBotResponse/images/msg.png"/><br><br>

Response Part:
<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/IdentityProtection-TeamsBotResponse/images/responsePart.png"/>
<br><br>
Documentation references:

<li>Azure AD Identity Protection:
<ul>
<li><a href="https://docs.microsoft.com/azure/active-directory/identity-protection/overview-identity-protection" target="_blank" rel="noopener">Learn more about Identity Protection</a></li>
</ul>
</li><br><br>


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIdentityProtection-TeamsBotResponse%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIdentityProtection-TeamsBotResponse%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
