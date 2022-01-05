# Ingest Office 365 Management Activity API Data
Author: Pete Bryan

This playbook ingests Audit.General events from the Office 365 Management Activity API (https://docs.microsoft.com/office/office-365-management-api/office-365-management-activity-api-reference) and writes them to a custom log table called O365API_CL. 

There are a number of pre-configuration steps required before deploying the Logic App.

## Enable Office 365 Audit Logging
In order to collected Audit events from an Office 365 subscription you first need to enable audit logging. There are several ways to do this: https://docs.microsoft.com/microsoft-365/compliance/turn-audit-log-search-on-or-off?view=o365-worldwide

## Register an Azure AD App
1. Go to Azure Active Directory / App Registrations
2. Create +New Registration
3. Give it a name.  Click Register.
4. Click API Permissions Blade.
5. Click Add a Permission.  
6. Click Office 365 Management APIs.
7. Click Appplication Permissions
8. Check all permissions for each category.  Click Add permissions.
9. Click grant admin consent for domain.com
10. Click Certificates and Secrets
11. Click New Client Secret
12. Enter a description, select never.  Click Add.
13. IMPORTANT.  Click copy next to the new secret and paste it somewhere temporaily.  You can not come back to get the secret once you leave the blade.
14. Copy the client Id from the application properties and paste it somewhere.
15. Also copy the tenant Id from the AAD directory properties blade.

## Register the Audit.General API Subscription
1. Open Powershell
2. Populate the following commands with the required elements (in <>) and run.

```powerhshell
$ClientID = "<AAD App clientID>"
$ClientSecret = "<AAD App clientSecret>"
$loginURL = "https://login.microsoftonline.com/"
$tenantdomain = "<domain>.onmicrosoft.com"
$TenantGUID = "<AAD tenantguid>"
$resource = "https://manage.office.com"
$body = @{grant_type="client_credentials";resource=$resource;client_id=$ClientID;client_secret=$ClientSecret}
$oauth = Invoke-RestMethod -Method Post -Uri $loginURL/$tenantdomain/oauth2/token?api-version=1.0 -Body $body
$headerParams = @{'Authorization'="$($oauth.token_type) $($oauth.access_token)"} 
$publisher = New-Guid
Invoke-WebRequest -Method Post -Headers $headerParams -Uri "https://manage.office.com/api/v1.0/$tenantGuid/activity/feed/subscriptions/start?contentType=Audit.General&PublisherIdentifier=$Publisher" 
```

## Deploy the Logic App template
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-O365Data%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-O365Data%2Fazuredeploy.json)