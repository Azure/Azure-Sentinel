author: Andrew Blumhardt

This playbook will copy AlienVault OTX IOC data using the Security Graph API. Requires an AlienVault API Key and registered Azure AD app. Update the AlienVault, tenant ID, client ID (app ID), and secret. Refer to MS Docs and Sentinel Threat Intelligence blogs for more information.

Activation:
1. Obtain an API Key (authentication to OTX data)
2. Create an App Registration in Azure AD (authentication to Microsoft Graph Security API)
3. Deploy Logic App
4. Update Get-AlienVault_OTX with your IDs and Keys
5. Activate the Threat Intelligence Platforms connector in Sentinel
6. Manually run Get-AlienVault_OTX to seed the table (wait 15 min)
5. Activate the related Analytic Rules in Sentinel
6. Verify that your TI data is flowing and formatted correctly:

ThreatIntelligenceIndicator
|where TimeGenerated >= ago(1h)
| summarize count() by Description

Logic App template based on and inspired by Jason Wescott’s article on OTX-Sentinel integration: https://techcommunity.microsoft.com/t5/azure-sentinel/bring-your-threat-intelligence-to-azure-sentinel/ba-p/1167546

