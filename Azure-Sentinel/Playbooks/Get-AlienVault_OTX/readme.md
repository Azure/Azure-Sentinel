# Get-AlienVault_OTX_V2
author: Andrew Blumhardt

This is a Logic App to import threat indicators from AlienVault into Azure Sentinel using the Graph Security API.

Refer to the following link for a more detailed description: https://azurecloudai.blog/2020/11/19/how-to-connect-alienvault-otx-to-azure-sentinel/ 

The connector "Threat Intelligence Platforms (Preview)" is needed to activate the integration with Microsoft Graph Security API.

**Summary:**

Designed to exceed the 1000 workflow limit for large datasets by breaking the results into pages. Set the Lookback to gather historic IOC data. Prevents failed collections when results exceed 1000 records. Tested using 200k records (5 years).

**Instructions:**
1.	Get an API key from AlienVault: https://otx.alienvault.com/
2.	Create an App  Registration in Azure AD: http://thewindowsupdate.com/2020/02/11/bring-your-threat-intelligence-to-azure-sentinel/
3.	Import the Logic App (disabled by default)
4.	Set the run variables (Tennant ID, Client ID, App Secret, and OTX API Key).
5.	Enable and run.
6.  Enable the "Threat Intelligence Platforms (Preview)" connector in the Sentinel workspace.

**Historic Data Lookback (RUN ONCE):**
1.	Set the lookback days to a desired value (example 365)
2.	Enable and run the Logic App (estimate 10 minutes processing time for every 10k records)
3.	Set the Lookback days to the default 1 day

**Notes:**
1.	API sets a record lookup URL for the profile page on AlienVault in “additionalInformation”
2.	API uses the “FileCreatedDateTime” column to log the time ingested

**App Registration Troubleshooting:**
1. Make sure to Grant Admin Consent on the API Permission page
2. Your App Registration can be assigned to roles at the workspace or RG. You may need to assign additional credentials.

During testing the provider returned some incorrectly formatted records. This was only observed in large collections. The app does not have error checking. Incorrectly formatted records will fail if encountered but the overall app will complete. This will cause the log to show the parent app as failed.

**Documentation references:**

<li>Azure Management groups as containers of subscriptions to monitor
<ul>
<li><a href="https://techcommunity.microsoft.com/t5/azure-sentinel/bring-your-threat-intelligence-to-azure-sentinel/ba-p/1167546" target="_blank" rel="noopener">Bring your threat intelligence to Azure Sentinel</a></li>
</ul>
</li>
<li>Azure Active Directory registered application, assigned with RBAC roles
<ul>
<li><a href="https://docs.microsoft.com/graph/api/resources/security-api-overview" target="_blank" rel="noopener">Use the Microsoft Graph Security API</a></li>
</ul>
</li>
</li>
<li>Logic App alternative that Combines Sentinel and Defender TI collection
<ul>
<li><a href="https://github.com/richlilly2004/Azure-Sentinel/tree/master/Playbooks/Get-TIfromOTX" target="_blank" rel="noopener">Get-TIfromOTX by Rich Lilly</a></li>
</ul>
</li>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-AlienVault_OTX%2Fazuredeploy.json) 
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-AlienVault_OTX%2Fazuredeploy.json)
