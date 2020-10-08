# Identity Protection - Email Response
author: Lior Tamir

This playbook uses Azure Identity Protection features in order to responde to risky users.
Attach this playbook to alert creation rules which expects to have entities of type Account attached to. 
When a new Azure Sentinel alert is created, the playbook iterates over the identities involved in the alert.
For each identity, playbook will send to the SOC email address (which is configured when deploying) an informative mail including the Risk history of this user, given by Azure AD Identity Protection.
Than it offers an option to confirm this user as compromised, dismiss it from being a risky user or ignore, by one button click.

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/IdentityProtection-EmailResponse/images/designerView.png"/>

Note: Azure AD Identity Protection is a premium feature. You need an Azure AD Premium P1 or P2 license to access the riskDetection API (note: P1 licenses receive limited risk information). The riskyUsers API is only available to Azure AD Premium P2 licenses only.

Documentation references:

<li>Azure AD Identity Protection:
<ul>
<li><a href="https://docs.microsoft.com/azure/active-directory/identity-protection/overview-identity-protection" target="_blank" rel="noopener">Learn more about Identity Protection</a></li>
</ul>
</li>


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIdentityProtection-EmailResponse%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIdentityProtection-EmailResponse%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
