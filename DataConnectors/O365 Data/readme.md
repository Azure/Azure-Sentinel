# Deploy Function App for getting Office 365 Management API data into Azure Sentinel
This function app will poll O365 Activity Managment API every 5 mins for logs.  It does support multi-tenant and is designed to get Audit.General and DLP.All events.

For multi-tenant, you will need to add 4 properties to the app config.  You can do this locally in local.settings.json before deploying the app or after in the Azure Portal.
To add a tenant:
1. Update numberOfTenants to the number of tenants you want to poll.
2. Add each of the following items replacing tenant1_ with tenant2_ and 3 and so on.
* "tenant1_clientID": "<GUID>",
* "tenant1_clientSecret": "@Microsoft.KeyVault(SecretUri=https://<name>.vault.azure.net/secrets/<secret>/<version>)",
* "tenant1_domain": "<domain>",
* "tenant1_tenantGuid": "<GUID>",

## Deployment and Configuration
### Add AAD App Permissions
1. Go to Azure Active Directory / App Registrations
2. Create +New Registration
3. Call it "O365APItoAzureSentinel".  Click Register.
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

### Create O365 API Subscription
1. Open Powershell
2. Run the following commands

```powerhshell
$ClientID = "<GUID> from AAD App Registration"
$ClientSecret = "<clientSecret> from AAD App Registrtion"
$loginURL = "https://login.microsoftonline.com/"
$tenantdomain = "<domain>.onmicrosoft.com"
$TenantGUID = "<tenantguid> from AAD"
$resource = "https://manage.office.com"
$body = @{grant_type="client_credentials";resource=$resource;client_id=$ClientID;client_secret=$ClientSecret}
$oauth = Invoke-RestMethod -Method Post -Uri $loginURL/$tenantdomain/oauth2/token?api-version=1.0 -Body $body
$headerParams = @{'Authorization'="$($oauth.token_type) $($oauth.access_token)"} 
$publisher = "<randomGuid>" Get a guid from https://guidgenerator.com/
```

* Run this command to enable Audit.General Subscription. 
```powershell
Invoke-WebRequest -Method Post -Headers $headerParams -Uri "https://manage.office.com/api/v1.0/$tenantGuid/activity/feed/subscriptions/start?contentType=Audit.General&PublisherIdentifier=$Publisher"
```
* Run this command to enable DLP.ALL subscription
```powershell
Invoke-WebRequest -Method Post -Headers $headerParams -Uri "https://manage.office.com/api/v1.0/$tenantGuid/activity/feed/subscriptions/start?contentType=DLP.ALL&PublisherIdentifier=$Publisher"
```

### Deploy the Function App
Note: You will need to prepare VS code for Azure function development.  See https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-powershell#prerequisites
1. Download the [Zip](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/O365%20Data/O365APItoAS-Template.zip?raw=true)  file of the Azure Funciton app from Github.
2. Extract to location on your machine.
3. Open VS Code
4. Click File -> Open Folder
5. Select the Top folder from extracted files.
6. Type Crtl+Shift+P.
7. Click Azure Functions: Deploy to function app.  You maybe asked to sign in to azure.
8. Click Create New function app in Azure (advanced)
9. Provide a unique name like "O365APItoAS".  Press Enter
10. Click Windows
11. Click Consumption
12. Click PowerShell
13. Click Create new Resource Group
14. Press enter to accept the name
15. Click Create a new storage Account
16. Press enter to accept the name
17. Click Create new Application Insights resource
18. Press enter to accept the name
19. Pick a location
20. Deployment will begin.
21. Wait for the deployment to complete, then click upload settings in the bottom right
22. Click yes to all to upload.
23. Go to the Azure Portal.
24. Go to the resource group that was created.  Click the Function.
25. Click Stop.
26. Click Platform Features Tab.
27. Click Identity
28. Click On under system assigned.  Click Save.  Click Yes.

### Create a Key Vault
1. Go to the Azure Portal.
2. Go to the resource group that was created.  Click Add.
3. Type Key Vault.
4. Create a Key vault.
5. Go to the resource created.
6. Click Access Policies.
7. Click Add Access Policy
8. Select Secret Management from Configure from template
9. Click Select Principal
10. Search for the name of the function app.  Click Select.
11. Click Add.
12. Click Save
13. Click Secrets
14. Click Generate
15. Enter O365Tenant1_clientsecret.  Paste the AAD app secret.  Click Create.
16. Click Generate
17. Enter O365workspaceKey.  Paste the Azure Sentinel Workspace Key.  Click Create.
18. Click O365clientsecret and copy the current version string to a temp location.
19. Click O365workspaceKey and copy the current version stringto a temp location.
20. Go to the Overiew blade.  Copy the DNS Name to a temp location.
Note: you will need to create additional keys if you have multiple tenants.

### Confiugure Settings for the Function
1. Go to the Azure Portal.
2. Go to the resource group that was created.  Click the Function.
3. Click Platform Features Tab.
4. Click Configuration under General.
5. click edit next to clientSecret.
6. Update the value using your copied properties.
* @Microsoft.KeyVault(SecretUri=https://<dnsname>/secrets/O365Tenant1_clientSecret/<versionstring>)
7. Click Ok.
8. click edit next to workspaceKey.
9. Update the value using your copied properties
* @Microsoft.KeyVault(SecretUri=https://<dnsname>/secrets/O365workspacekey/<versionstring>)
10. Click Ok.
11.  Update each setting
* clientID = AAD app registration id
* contentTypes = Audit.General or Audit.General,DLP.All or DLP.All
* domain = <domain> from <domain>.onmicrosoft.com
* publisher is a random guid for throttling that we used in steps to create subscription.
* recordTypes This can be 0 or a list of record types comma seperated like 28,40,41 (see https://docs.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema#auditlogrecordtype)
* tenantGuid is your AAD tenant guid.
* workspaceId is your Azure Sentinel workspace id
12. Click Save
13. Go back to the function and click start under the overview blade.
