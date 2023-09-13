# Commvault -- Sentinel Integration
This Sentinel integration enables Commvault users to ingest alerts and other data into their Sentinel instance. With Analytic Rules, Sentinel can automatically create Sentinel incidents from incoming Commvault syslogs. 

### Key Features
- Using Azure KeyVault, Commvault access tokens are automatically rotated, providing enhanced security. 
- Perform automated actions such as disabling IDP, specific users, or data aging on your Commvault/Metallic environment from inside Sentinel.

## Prerequisites
- Administrative access to your Commvault/Metallic environment.
- Administrative access to your Azure Resource Group and Subscription.
- An Azure Sentinel instance in the aforementioned Azure Resource Group.
- An Azure Log Analytic Workspace in the aformentioned Azure Resource Group.

## Inventory of Required Assets
The following Azure assets need to all be created in order for this integration to function properly. In addition to these assets, proper permissions need to be granted. When following the installation instructions, please use the same asset names to ensure compatibility.
### Automation Account
- **Commvault-Automation-Account:** This is where the runbooks are stored.
### Runbooks
All runbooks are stored in the Automation Account *Commvault-Automation-Account*.
- **Commvault_Cycle_Token:** Used in the *CommvaultTokenCycle* Logic App to execute the API calls that generate a new Commvault/Metallic access token.
- **Commvault_Disable_Data_Aging:** Used in the *Commvault-Logic-App* Logic App to execute the API calls that disable data aging for a specific client. 
- **Commvault_Disable_IDP:** Used in the *Commvault-Logic-App* Logic App to execute the API calls that disable the IDP in your environment.
- **Commvault_Disable_User:** Used in the *Commvault-Logic-App* Logic App to execute the API calls that disable a specific user given their email address.
### Logic Apps
- **Commvault-Logic-App:** This Logic App (also referred to as a *Playbook*) executes when called upon by an Automation Rule. Accessing the KeyVault to retrieve various credentials, it executes a specific runbook depending on the use case.
- **CommvaultTokenCycle:** This Logic App (also referred to as a *Playbook*) executes periodically to generate a new Commvault/Metallic access token and securely overwrites the old access token in your KeyVault.
### KeyVaults
- **Commvault-Integration-KV:** This KeyVault stores all required credentials as *secrets*.
### KeyVault Secrets
All of these secrets are stored in the *Commvault-IntegrationKV* KeyVault. For the first time setup, their values need to be manually retrieved.
- **access-token:** The access token for Commvault/Metallic.
- **environment-endpoint-url:** The URL of your Commvault/Metallic endpoint.
- **keyvault-url:** The URL of your Azure KeyVault. 
- **client-id:** The ID of the Azure App Registration client.
- **tenant-id:** The ID of your Azure Tenant.
- **secret-id:** The ID of your Azure App Registration client secret. 
- **keyvaultsecret:** The value of your Azure App Registration client secret. 
### App Registrations
- **Commvault_Token_Cycle_App:** An Azure Active Directory App Registration used for authorized KeyVault access. 
### Sentinel Analytic Rules
Each of these Analytic Rules run on a continuous basis and are querying for the manually triggered Sentinel incident. Once it discovers a specific incident, a new incident is created that triggers the corresponding Automation Rule. 
- **IDP Compromised:** The Sentinel Analytic Rule that continuously searches for a manually created Sentinel Incident pertaining to a compromised Commvault/Metallic IDP. 
- **User Compromised:** The Sentinel Analytic Rule that continuously searches for a manually created Sentinel Incident pertaining to a compromised Commvault/Metallic user. 
- **Data Aging:** The Sentinel Analytic Rule that continuously searches for a manually created Sentinel Incident pertaining to a request to disable data aging on a specific Commvault/Metallic client. 

## Installation
### Create the Runbooks
* Go to Automation Accounts -> Create 
  * Basics:
    * Select the correct subscription and resource group 
    * Name it “Commvault-Automation-Account" 
  * Click “Create” 
* Go to “Commvault-Automation-Account" ->  Runbooks (under “Process Automation”) -> Create a Runbook 
  * Name =  
    * Commvault_Disable_IDP
  * Runbook Type =  
    * Powershell 
  * Runtime Version =  
    * 5.1 
  * Click “Create” 
  * Edit Powershell Runbook =
    * Use the content in this file: **Runbooks/Commvault_Disable_IDP.ps1**
    * Click "Publish"
  * Click "Save"
* Go to “Commvault-Automation-Account" ->  Runbooks (under “Process Automation”) -> Create a Runbook 
  * Name = 
    * Commvault_Disable_User
  * Runbook Type = 
    * Powershell
  * Runtime Version = 
    * 5.1
  * Click "Create"
  * Edit Powershell Runbook = 
    * Use the content in this file: **Runbooks/Commvault_Disable_Users.ps1**
    * Click "Publish"
  * Click "Save"
* Go to “Commvault-Automation-Account" ->  Runbooks (under “Process Automation”) -> Create a Runbook 
  * Name = 
    * Commvault_Disable_Data_Aging
  * Runbook Type =
    * Powershell
  * Runtime Version = 
    * 5.1
  * Click "Create"
  * Edit Powershell Runbook = 
    * Use the content in this file: **Runbooks/Commvault_Disable_Data_Aging.ps1**
    * Click "Publish"
  * Click "Save"
    
### Create The KeyVault:
* Go to KeyVault -> Create
  * Basics:
    * Select the correct subscription and resource group
    * KeyVault name = 
      * Commvault-Integration-KV
  
### Create the KeyVault Secrets:
* Go to KeyVault -> "Commvault-Integration-KV" -> Secrets (Under "Objects") -> "Generate/Import"
  * Upload Options:
    * Manual
  * Name: 
    * access-token
  * Secret Value:
    * (Your Commvault/Metallic access token)
  * Enabled:
    * Yes
  * Click "Create"
* Go to KeyVault -> "Commvault-Integration-KV" -> Secrets (Under "Objects") -> "Generate/Import"
  * Upload Options: 
    * Manual
  * Name: 
    * environment-endpoint-url
  * Secret Value:
    * (Your Commvault/Metallic endpoint's URL)
  * Enabled:
    * Yes
  * Click "Create"
  
### Initialize the Logic App (*Playbook*):
* Go to "Custom Deployment" -> "Build your own template in the editor" -> "Load File" -> Use the json present under **Playbooks/CommvaultLogicApp/azuredeploy.json**.
	* Save 
	* Enter the resource group, subscription, automation account and keyvault name
	* In the playbook name field use "Commvault-Logic-App"
* Go to KeyVault -> Commvault-Integration-KV
* Access Configuration:
    * Permission Model = 
      * Vault Access Policy
    * Go to "Access Policies" -> "Create"
      * Under "Permissions" -> "Secret Permissions"
        * Select "Get", "List", and "Set"
        * Click "Next"
      * Under "Principal"
        * Search for "Commvault-Logic-App"
          * Select "Commvault-Logic-App from the search results
        * Click "Next"
      * Under "Application (Optional)"
        * Do nothing here except click "Next"
      * Under "Review + Create"
        * Click "Create"
  * Click "Review + Create"
  * Click "Create"

### Setup the Managed Identity
* Go to Automation Accounts -> "Commvault-Sandbox-Automation-Account" -> "Access Control (IAM)" -> "Add" -> "Add Role Assignment
  * In "Job function roles" under "role":
    * Click on "Automation Contributor" so that it is highlighted in grey
  * Click "Next"
  * Assign Access To:
    * Select "Managed Identity"
  * Members:
    * Select "Select Members"
      * Select the correct subscription
      * For Managed Identity, select "Logic App"
      * Select "Commvault-Logic-App" form the list
      * Click the blue "select" button
  * Go to the "Review + Assign" tab
    * Click the blue "Review + Assign" button
* Go to your resource group -> "Access Control (IAM)" -> "Add" -> "Add Role Assignment"
  * In "Job Function Roles" under "Role"
    * Find "Microsoft Sentinel Automation Contributor" and click it so that it is highlighted in grey
  * Under the "Members" tab
    * Assign access to: 
      * Managed Identity
    * Click "+ Select Members"
      * Select the correct subscription
      * Managed Identity:
        * Logic App
      * From the list, select "Commvault-Logic-App"
      * Click the blue "Select" button
  * Under "Review + Assign" tab
    * Click the blue "Review + Assign" button
* Go to "Logic Apps" -> "Commvault-Logic-App" -> "Identity" (under "Settings") -> "System Assigned" tab -> "Azure Role Assignments"
  * Add Role Assignment
    * Scope: 
      * KeyVault
    * Resource:
      * Commvault-Integration-KV
    * Role:
      * KeyVault Secrets Officer
    * Click the blue "Save" button

### Create the Analytic Rules:
* Go to Sentinel -> (The name of your Sentinel instance) -> Analytics (located under “Configuration”) -> Create -> Scheduled Query Rule 
  * General: 
    * Name: 
      * IDP Alert
    * Description:
      * IDP Compromised
  * Set Rule Logic:
    * Rule Query:
      SecurityIncident  
      | where Title has "Cvlt Alert"   
      and Description == "IDP Compromised"   
      and Status has "New" 
    * Run Query Every:
      * 5 minutes
    * Lookup data from the last:
      * 5 minutes
  * Incident Settings:
    * Alert Grouping:
      * Enabled
  * Review and Create:
    * Create
* Go to Sentinel -> (The name of your Sentinel instance) -> Analytics (located under “Configuration”) -> Create -> Scheduled Query Rule 
  * General: 
    * Name: 
      * Data Alert
    * Description: 
      * Data Compromised
  * Set Rule Logic: 
    * Rule Query: 
      SecurityIncident  
      | where Title has "Cvlt Alert" and Description has "Client" and Description has "Compromised" and Status has "New" 
      | extend extracted_word = extract("Client\\s(.*?)\\sCompromised", 1, Description) 
      | project TimeGenerated, 
        Title, 
        Description, 
        Status, 
        CustomDetails = extracted_word
    * Alert Details:
      * Alert Name Format: 
        * User Alert
      * Alert Description Format:
      * {{Custom Details}}
    * Run Query Every: 
      * 5 minutes
    * Lookup data from the last:
      * 5 minutes
  * Incident Settings: 
    * Alert Grouping: 
      * Enabled
  * Review and Create:
    * Create
* Go to Sentinel -> (The name of your Sentinel instance) -> Analytics (located under “Configuration”) -> Create -> Scheduled Query Rule 
  * General:
    * Name: 
      * User Alert
    * Description: 
      * User Compromised
  * Set Rule Logic:
    * Rule Query:
      SecurityIncident  
      | where Title has "Cvlt Alert" and Description has "User" and Description has "Compromised" and Status has "New" 
      | extend extracted_word = extract("User\\s(.*?)\\sCompromised", 1, Description) 
      | project TimeGenerated, 
        Title, 
        Description, 
        Status, 
        CustomDetails = extracted_word 
    * Alert Details:
      * Alert Format:
        * User Alert
      * Alert Description Format:
        * {{CustomDetails}}
    * Run Query Every:
      * 5 minutes
    * Lookup data from the last:
      * 5 minutes
  * Incident Settings:
    * Alert Grouping:
      * Enabled
  * Review and Create
    * Create
### Create The Automation Rules
* Go to Sentinel -> (The name of your Sentinel instance) -> Automation (located under “Configuration”) -> Create -> Automation Rule 
  * Automation Rule Name: 
    * Commvault-Disable-Data-Aging-Rule
  * Trigger: 
    * When incident is created
  * Conditions: 
    * If incident provider:
      * Equals
      * Microsoft Sentinel
    * Analytic Rule Name: 
      * Contains
      * Data Alert
  * In the box in the "Actions" section, select "Change Status"
  * In the box below "Change Status" in the "Actions" section, select "Closed"
  * In the box below that, select "True Positive - Suspicious Activity"
  * At the bottom of the "Actions" section, click "+ Add Action"
  * As an owner of the resource group, click the blue "Manage Playbook Permissions" text
    * Select your resource group
    * Click "Apply"
  * Click the box below "Run Playbook" in the "Actions" section
    * Select "Commvault-Logic-App"
  * Order: 
    * 1
  * Click "Apply"
* Go to Sentinel -> (The name of your Sentinel instance) -> Automation (located under “Configuration”) -> Create -> Automation Rule 
  * Automation Rule Name: 
    * Commvault-Disable-IDP-Automation-Rule
  * Trigger:
    * When incident is created
  * Conditions: 
    * If incident provider: 
      * Equals 
      * Microsoft Sentinel 
    * Analytic Rule Name: 
      * Contains 
      * IDP Alert
  * In the box in the "Actions" section, select "Change Status"
  * In the box below "Change Status" in the "Actions" section, select "Closed"
  * In the box below that, select "True Positive - Suspicious Activity"
  * At the bottom of the "Actions" section, click "+ Add Action"
  * Click the box below "Run Playbook" in the "Actions" section
    * Select "Commvault-Logic-App"
  * Order:
    * 2
  * Click "Apply"
* Go to Sentinel -> (The name of your Sentinel instance) -> Automation (located under “Configuration”) -> Create -> Automation Rule 
  * Automation Rule Name: 
    * Commvault-Disable-User-Automation-Rule
  * Trigger:
    * When incident is created
  * Conditions: 
    * If incident provider: 
      * Equals
      * Microsoft Sentinel 
    * Analytic Rule Name: 
      * Contains
      * User Alert
  * In the box in the "Actions" section, select "Change Status"
  * In the box below "Change Status" in the "Actions" section, select "Closed"
  * In the box below that, select "True Positive - Suspicious Activity"
  * At the bottom of the "Actions" section, click "+ Add Action"
  * Click the box below "Run Playbook" in the "Actions" section 
    * Select "Commvault-Logic-App"
  * Order: 
    * 3
  * Click "Apply"
### Create the Active Directory App Registration: 
* From Home, go to Azure Active Directory -> App Registrations (under “Manage”) 
* In the top left corner, click “+ New Registration” 
  * Name: 
    * Commvault_Token_Cycle_App
  * Click the blue "Register" button 
* From Home, go to Azure Active Directory -> App Registrations (under “Manage”) 
* Under “Owned Applications”, click on “Commvault_Token_Cycle_App” 
  * In the middle of the screen (under “Essentials”): 
    * Copy the “Application (client) ID” to another document. Hereon, this value will be referenced to as the App Registration Client ID.
    * Copy the “Directory (tenant) ID” to another document. Hereon, this value will be referenced to as the Tenant ID.  
  * On the left (under “Manage”), click “API Permissions” 
    * In the middle of the screen, click “+ Add A Permission” 
      * In the right window that just popped open, select “Azure Key Vault” 
        * Under “Permissions”, select “user_impersonation” 
        * On the bottom of the screen, click the blue “Add Permissions” button 
  * On the left (under “Manage”), click “Certificates & Secrets” 
    * In the middle of the screen under “Client Secrets”, click “+ New Client Secret” 
      * Description: 
        * TokenCycle
      * On the bottom of the screen, click the blue "Add" button
    * In the table in the middle of the screen, copy the “Value” of the client secret “TokenCycle”. Copy this value to another document. Hereon, this value will be referenced to as the App Registration Client Secret.  
### Define more KeyVault secrets:
* From Home, go to Key Vaults -> Commvault-Integration-KV 
* In the middle of the screen, copy the “Vault URI” to another document. Hereon, this value will be referenced to as the KeyVault URL. 
* Under “Objects” on the left, click “Secrets” 
  * On the top, click "+ Generate/Import"
    * Name: 
      * client-id
    * For "Secret Value", paste in the value of the App Registration Client ID
  * On the top, click "+ Generate/Import"
    * Name: 
      * keyvault-url 
    * For "Secret Value", paste in the KeyVault URL
  * On the top, click "+ Generate/Import"
    * Name: 
      * keyvaultsecret
    * For "Secret Value", paste in the App Registration Client Secret
  * On the top, click "+ Generate/Import"
    * Name: 
      * tenant-id
    * For "Secret Value", paste in the Tenant ID.
### Token Rotation Logic App: 
* From Home, go to Logic Apps
* In the top left corner, click "+ Add"
  * Basics: 
    * Project Details: 
      * Select your subscription and resource group 
    * Instance Details: 
      * Logic App Name: 
        * CommvaultTokenCycle
    * Play Type: 
      * Consumption 
  * In the bottom left corner, click the blue "Review + Create" button
* In the "Logic App Designer" popup menu, select "Recurrence" Under "Start with a common trigger"
* In the "Recurrence" block:
  * Interval: 
    * 5
  * Frequency: 
    * Days
* Save this by clicking the "Save" button in the top left corner. We will return to this later. 
### Token Rotation Logic App Permissions:
* From Home, go to Logic Apps -> CommvaultTokenCycle
  * On the left side, click on "Identity" (under "Settings")
    * Under "System Assigned", switch "Status" to "On"
    * Click "Save" (located just above the "Status" switch)
    * If prompted, click "Yes"
    * There should now be a blue "Azure Role Assignments" button. Click it. 
      * In the new page named "Azure Role Assignments", click "+ Add Role Assignment"
        * Scope:
          * KeyVault
        * Subscription: 
          * (Your subscription)
        * Resource:
          * Commvault-Integration-KV
        * Role:
          * Key Vault Secrets Officer
        * Click the blue "Save" button
      * Click "+ Add Role Assignment"
        * Scope:
          * Resource Group
        * Subscription: 
          * (Your subscription)
        * Resource Group:
          * (Your resource group)
        * Role: 
          * Automation Runbook Operator
        * Click the blue "Save" button
      * Click "+ Add Role Assignment"
        * Scope: 
          * Resource Group
        * Subscription: 
          * (Your subscription)
        * Resource Group:
          * (Your resource group)
        * Role: 
          * Microsoft Sentinel Contributor
        * Click the blue "Save" button
      * Click "+ Add Role Assignment"
        * Scope: 
          * Resource Group
        * Subscription: 
          * (Your subscription)
        * Resource Group:
          * (Your resource group)
        * Role: 
          * Automation Contributor
        * Click the blue "Save" button
### More KeyVault Permissions:
* From Home, go to KeyVaults -> Commvault-Integration-KV
  * On the left pane, click "Access Policies"
    * On the top left, click "+ Create"
      * Permissions: 
        * Secret Permissions:
          * Select "Get", "List", and "Set"
      * Principal:
        * Commvault_Token_Cycle_App
      * Review + Create:
        * Click the blue "Create" button on the bottom left
    * On the top left, click "+ Create"
      * Permissions: 
        * Secret Permissions:
          * Select "Get", "List", and "Set"
      * Principal: 
        * CommvaultTokenCycle
      * Review + Create:
        * Click the blue "Create" button on the bottom left
### Token Cycle Runbook:
* From Home, go to Automation Accounts -> Commvault-Automation-Account 
  * On the left pane, click “Runbooks” (under “Process Automation”)    
    * In the top left corner, click "+ Create a Runbook"
      * Name: 
        * Commvault_Cycle_Token
      * Runbook Type:
        * PowerShell
      * Runtime Version:
        * 5.1 
    * In the bottom left corner, click the blue "Create" button
    * Copy and paste the content from **runbooks/Commvault_Cycle_Token.ps1** into the runbook editor
    * In the top left, click "Save"
    * In the top left, click "Publish"
### Completing the Token Rotation Logic App: 
* From Home, go to Logic Apps -> CommvaultTokenCycle
  * On the left pane, click "Logic App Designer" (located under "Development Tools")
    * In the center of the screen (under the "Recurrence" block), click "+ New Step"
      * Search for "get secret"
      * Under All -> Actions, select "Get Secret - Azure KeyVault"
        * Name of Secret:
          * access-token
        * Rename this block to be "Access Token" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "Access Token" block), click "+ New Step"
      * Search for "get secret"
      * Under All -> Actions, select "Get Secret - Azure KeyVault"
        * Name of the secret
          * environment-endpoint-url
        * Rename this block to be "Endpoint URL" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "Endpoint URL" block), click "+ New Step"
      * Search for "get secret"
      * Under All -> Actions, select "Get Secret - Azure KeyVault"
        * Name of the Secret: 
          * keyvault-url
        * Rename this block to be "KeyVault URL" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "KeyVault URL" block), click "+ New Step"
      * Search for "get secret"
      * Under All -> Actions, select "Get Secret - Azure KeyVault"
        * Name of the Secret
          * tenant-id
        * Rename this block to be "KeyVault Tenant ID" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "KeyVault Tenant ID" block), click "+ New Step"
      * Search for "get secret"
        * Under All -> Actions, select "Get Secret - Azure KeyVault"
          * Name of the secret
            * client-id
          * Rename this block to be "KeyVault Client ID" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "KeyVault Client ID" block), click "+ New Step"
      * Search for "get secret"
      * Under All -> Actions, select "Get Secret - Azure KeyVault"
        * Name of the Secret
          * keyvaultsecret
        * Rename this block to be "KeyVault Client Secret" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "KeyVault Client ID" block), click "+ New Step"
      * Search for "create job"
      * Under All -> Actions, select "Create Job - Azure Automation"
        * Subscription: 
          * (Your subscription)
        * Resource Group:
          * (Your resource group)
        * Automation Account:
          * Commvault-Automation-Account
        * Runbook Name:
          * Commvault_Cycle_Token
        * Wait for Job:
          * Yes
        * Runbook Parameter keyvaulturl:
          * (The value of the "KeyVault URL" block)
        * Runbook Parameter apiAccessToken:
          * (The value of the "Access Token" block)
        * Runbook Parameter EnvironmentEndpointURL:
          * (The value of the "Endpoint URL" block)
        * Runbook Parameter KeyVaultClientID:
          * (The value of the "KeyVault Client ID" block)
        * Runbook Parameter KeyVaultTenantID:
          * (The value of the "KeyVault Tenant ID" block)
        * Runbook Parameter KeyVaultClientSecret:
          * (The value of the "KeyVault Client Secret" block)
      * Rename this block to be "Cycle Token Job" by clicking the three dots in the top right corner and selecting "Rename"
    * In the center of the screen (under the "cycle token job" block), click "+ New Step"
      * Search for "get job output"
      * Under All -> Actions, select "Get Job Output - Azure KeyVault"
        * Subscription:
          * (Your subscription)
        * Resource Group:
          * (Your resource group)
        * Automation Account:
          * Commvault-Automation-Account
        * Job ID:
          * (The job ID of "Cycle Token Job")
    * In the top left corner, click "Save"

## Example Usage
### Disable a compromised Commvault/Metallic IDP from Sentinel
* Go to Sentinel -> (The name of your Sentinel instance) -> Incidents (under Threat Management) -> Create Incident
  * Title:
    * Cvlt Alert
  * Description:
    * IDP Compromised
  * Severity:
    * Medium
  * Status:
    * New
  * Click "Create"
* Wait 5-10 minutes for it to run
* Check if it ran:
  * Go to Logic Apps -> Commvault-Logic-App
    * In the middle of the screen is a table with the column headers Status, Start Time, etc. 
    * Sort the rows by start time by clicking the "Start Time" column header
    * The latest run should say "Succeeded". Click it. 
    * Check to see the result of the runbook at the end of the logic app chain.
### Disable a compromised Commvault/Metallic User from Sentinel
* Go to Sentinel -> (The name of your Sentinel instance) -> Incidents (under Threat Management) -> Create Incident
  * Title:
    * Cvlt Alert
  * Description (Where "< user email >" is the email address of the user that is compromised):
    * User < user email > Compromised
  * Severity:
    * Medium
  * Status:
    * New
  * Click "Create"
* Wait 5-10 minutes for it to run
* Check if it ran:
  * Go to Logic Apps -> Commvault-Logic-App
    * In the middle of the screen is a table with the column headers Status, Start Time, etc. 
    * Sort the rows by start time by clicking the "Start Time" column header
    * The latest run should say "Succeeded". Click it. 
    * Check to see the result of the runbook at the end of the logic app chain.
### Disable Data Aging from Sentinel
* Go to Sentinel -> (The name of your Sentinel instance) -> Incidents (under Threat Management) -> Create Incident
  * Title:
    * Cvlt Alert
  * Description (Where "< client name >" is the name of the client that you would like to disable data aging on):
    * Client < client name > Compromised
  * Severity:
    * Medium
  * Status:
    * New
  * Click "Create"
* Wait 5-10 minutes for it to run
* Check if it ran:
  * Go to Logic Apps -> Commvault-Logic-App
    * In the middle of the screen is a table with the column headers Status, Start Time, etc. 
    * Sort the rows by start time by clicking the "Start Time" column header
    * The latest run should say "Succeeded". Click it. 
    * Check to see the result of the runbook at the end of the logic app chain.