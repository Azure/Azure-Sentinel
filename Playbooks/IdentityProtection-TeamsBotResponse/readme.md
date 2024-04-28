# Identity Protection - response from Teams
author: Lior Tamir

Run this playbook on incidents which contains suspicious AAD identities. When a new incident is created, this playbook iterates over the Accounts. It then posts an adaptive card in the SOC Microsoft Teams channel, including the potential risky user information given by Azure AD Identity Protection. The card offers to confirm the user as compromised or dismiss the compromised user in AADIP. It also allows to configure the Azure Sentinel incident. A summary comment will be posted to document the action taken and user information. [Learn more about Azure AD Identity Protection](https://docs.microsoft.com/azure/active-directory/identity-protection/overview-identity-protection)

## Prerequisites
1. Using the riskyUsers API requires an Azure AD Premium P2 license. 
2. Have a user which has permissions on Identity Protection API. [Learn more](https://docs.microsoft.com/graph/api/riskyuser-confirmcompromised?view=graph-rest-1.0#permissions)
 3. (optional) Create policies in Azure AD Identity protection to run when users are confirmed as compromised. [Learn more](https://docs.microsoft.com/azure/active-directory/identity-protection/concept-identity-protection-policies)

Overall:<br>
![](./images/ImageLight1.png)

Card to be sent by Microsoft Teams bot: <br>
![](./images/TeamsCard.png)

Response Part:<br>
![](./images/commmentLight.png)

Documentation references:
<li>Azure AD Identity Protection:
<ul>
<li><a href="https://docs.microsoft.com/azure/active-directory/identity-protection/overview-identity-protection" target="_blank" rel="noopener">Learn more about Identity Protection</a></li>
</ul>
</li>


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIdentityProtection-TeamsBotResponse%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FIdentityProtection-TeamsBotResponse%2Fazuredeploy.json)