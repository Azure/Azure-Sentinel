# Deploy Function App for getting Office 365 Management API data into Azure Sentinel
This function app will poll O365 Activity Managment API every 10 mins for logs.  It is designed to get Teams events under Audit.General.

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

### Deploy the Function App pre-req
1. Create a ResourceGroup to host the artefacts of the solution. 
2. Create a storage account under resource group. 
3. Create a Function App to host the solution, and download the publish profile. 
4. Create a Azure Key vault to store sensitive keys. 

#### 1: Deploy via Visual Studio
1. Download the solution artefacts of Azure Funciton app from Github.
2. Open Solution using Visual Studio (Express and above)
3. Build the solution.
4. Publish the function app, using publish profile downloaded in previous section step. 
5. Deploy. 
6. Press enter to accept the name
7. Pick a location
8. Deployment will begin.
9. Wait for the deployment to complete
10. Click yes to all to upload.
11. Go to the resource group that was created.  Click the Function.
12. Click Stop.
13. Click Platform Features Tab.
14. Click Identity
15. Click On under system assigned.  Click Save.  Click Yes.

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
15. Enter ClientId.  Paste the AAD app Client ID.  Click Create.
16. Click Generate
17. Enter ClientSecret.  Paste the app Client secret.  Click Create.
18. Click Generate
19. Enter StorageContainerConnectionString.  Paste the storage connection string.  Click Create.
20. Click Generate
21. Enter SentinelCustomerId.  Paste the Sentinel workspace Id.  Click Create.
22. Click Generate
23. Enter SentinelSharedkey.  Paste the Sentinel shared key.  Click Create.


### Confiugure Settings for the Function
1. Go to the Azure Portal.
2. Go to the resource group that was created.  Click the Function.
3. Click Platform Features Tab.
4. Click Configuration under General.
5. Add keys by clicking new Application Settings
   * KeyVaultEnabled = true/false ( if key vault is enabled)
   * KeyVaultBaseUrl = "https://<Add Your KeyVault Base Url here>.vault.azure.net",
   * ClientId = "<Add Your Client Id here>"
   * ClientSecret =  "<Add Your Client Secret here>"
   * TenantId = "<Add Your Tenant Id here>"
   * AADInstance = "https://login.microsoftonline.com/{0}"
   * ResourceId = "https://manage.office.com"
   * PublisherGUID = <domain> from <domain>.onmicrosoft.com
   * publisher is a random guid for throttling that we used in steps to create subscription.

   * AuditLogExtractionStartDate = "4/15/2020 12:00:01 AM"
   * "Start time and end time must be specified (or both omitted) and must be less than or equal to 24 hours apart, with the start time prior to  end time and start time no more than 7 days in the past."
   *If not provided then Current UTC Time is taken as default.

   * ConnectionIntervalinMinutes = <domain> from <domain>.onmicrosoft.com
   * Indicating the time range of content to return , read more on https://docs.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference

   * StorageContainerConnectionString = "Stroage container string"
   * If key vault is enabled then leave it blank. 

   * LogContainerName = "log"
   * Container name where function specific log info will be stored. 
   * LogFileName = "logs.txt""
   * log file name.

   * EnableArchiving = true/false , 
   * DataContainerName = "data"
   * Container name where blobs will be stored, depending on EnableArchiving flag 

   * EnableDirectInjestionToWorkSpace = true/false,
   * Indicates if the audit logs to be directly injested to analytics workspace


   * SentinelCustomerId = "Sentinel workspace Id"
   * If keyvault is enabled then leave blank
   * SentinelSharedkey = "Shared key"
   * If keyvalut is enabled then leave blank
12. Click Save
13. Go back to the function and click start under the overview blade.
