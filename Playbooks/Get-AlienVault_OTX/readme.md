# Get-AlienVault_OTX
author: Andrew Blumhardt

This playbook will copy AlienVault OTX IOC data using the Security Graph API into Azure Sentinel. Requires an AlienVault API Key and registered Azure AD app. Update the AlienVault, tenant ID, client ID (app ID), and secret. Refer to MS Docs and Sentinel Threat Intelligence blogs for more information.

Activation:
Obtain an API Key (authentication to OTX data)
Create an App Registration in Azure AD (authentication to Microsoft Graph Security API)
Deploy Logic App
Update Get-AlienVault_OTX with your IDs and Keys
Activate the Threat Intelligence Platforms connector in Sentinel
Manually run Get-AlienVault_OTX to seed the table (wait 15 min)
Activate the related Analytic Rules in Sentinel
Verify that your TI data is flowing and formatted correctly:

ThreatIntelligenceIndicator
|where TimeGenerated >= ago(1h) | summarize count() by Description

Logic App template based on and inspired by Jason Wescott’s article on OTX-Sentinel integration: 

Documentation references:

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
