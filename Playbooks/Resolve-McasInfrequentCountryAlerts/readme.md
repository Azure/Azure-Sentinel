# Resolve-McasInfrequentCountryAlerts
author: Sebastien Molendijk - Microsoft

This playbook allows you to automatically resolve Microsoft Cloud App Security [Infrequent Country alerts](http://aka.ms/mcasinvestigationguide#activity-from-infrequent-country) based on several criterias like:

* The user out-of-office status
* The user group membership
* The user risk level status in Azure AD

<br>

## Requirements

This playbook uses an API token to close the alert in MCAS, and an AAD service principal with the required permissions below to query the relevant Microsoft Graph endpoints.

|Logic App action|API|Endpoint|AAD Required Permission|
|----------------|---|--------|-----------------------|
|Get_user_details|Microsoft Graph|/users/{user UPN}|User.Read.All|
|Get_user_manager|Microsoft Graph|/users/{user UPN}/manager|User.Read.All|
|Get_user_OOF|Microsoft Graph|/users/{user UPN}/getMailTips|Mail.Read|
|Check_group_membership|Microsoft Graph|/users/{user UPN}/checkMemberGroups|Directory.Read.All|
|Get_user_AAD_risk_status|Microsoft Graph|/riskyUsers/{user AAD object Id}|IdentityRiskyUser.Read.All|
|Resolve_Cloud_App_Security_alert|MCAS API|/cas/api/v1/alerts/resolve/||

<br>

### Additional resources

* Complete explanation and demonstration of this playbook in [this video](https://youtu.be/ql8x4rC6m9A).
* [Registering a service principal in Azure AD](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal)
* [Microsoft Graph permissions reference](https://docs.microsoft.com/graph/permissions-reference)
* [Create an MCAS API token](https://docs.microsoft.com/cloud-app-security/api-tokens)

<br>

## Deployment

You can use the **Deploy.ps1** script, after updating the required parameters in the provided **parameters.json** file, or use the buttons below.

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FResolve-McasInfrequentCountryAlerts%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FResolve-McasInfrequentCountryAlerts%2Fazuredeploy.json)
