# Commvault - Sentinel Integration

Integrate Commvault with Sentinel to ingest alerts and data for automated incident creation via Analytic Rules.

## Key Features

- Automate actions (disable IDP, users, data aging) within your Commvault/Metallic environment from Sentinel.

## Prerequisites

- Commvault/Metallic admin access.
- Azure Resource Group/Subscription admin access.
- Azure Cloud Shell access.
- Microsoft Sentinel instance in your Azure Resource Group.
- Azure Log Analytic Workspace in your Azure Resource Group.

## Inventory of Required Assets

The following Azure assets are required for this integration. Ensure proper permissions are granted. Use consistent asset names during installation.

### KeyVault

- A KeyVault to securely store credentials as secrets. **KeyVault permission model should be set to Access Policy.**

### KeyVault Secrets

These secrets are stored in your KeyVault. Their initial values need manual retrieval.

- **access-token:** The access token for Commvault/Metallic.
- **environment-endpoint-url:** The URL of your Commvault/Metallic endpoint, in the format:
  - Command center url: `https://<hostname>/commandcenter/api`
  - WebService url: `http://<hostname>:<port>/SearchSvc/CVWebService.svc`

## Installation

### Create The KeyVault

- Azure Portal -> KeyVault -> Create -> Basics (select subscription, resource group, provide a KeyVault name).

### Create the KeyVault Secrets

- Azure Portal -> Your KeyVault -> Secrets (Under "Objects") -> "Generate/Import" -> Manual:
  - Name: `access-token`, Secret Value: (Your Commvault/Metallic access token), Enabled: Yes -> Create.
  - Name: `environment-endpoint-url`, Secret Value: (Your Commvault/Metallic endpoint's URL), Enabled: Yes -> Create.

### Install Commvault Cloud Solution

- Sentinel -> Content hub (under “Configuration”) -> Search for "Commvault Cloud" -> Install.

### Configure Data Connector

- Sentinel -> Data connectors -> Search for "CommvaultSecurityIQ (using Azure Functions)" -> Open connector page -> Deploy to Azure -> Fill up the required details -> Create.

### Upload and Run PowerShell Script Setup-CommvaultAutomation

- Azure Cloud Shell -> Click on **Manage files** -> Upload `Tools\Setup-CommvaultAutomation.ps1` -> Run:
  ```powershell
  ./Setup-CommvaultAutomation.ps1
    ```

### Create the Analytic Rules

- Sentinel -> Content hub (under “Configuration”) -> Click on "Commvault Cloud" -> Click on "Manage" -> Click on "Commvault Cloud Alert" -> Click on "Create Rule" -> Follow the steps by clicking "Next" -> Click on "Save".
- Repeat for other Analytic rules in the solution.

### Create the Playbooks

- Sentinel -> Content hub (under “Configuration”) -> Click on "Commvault Cloud" -> Click on "Manage":
  - Click on "logic-app-disable-data-aging" -> Click on "Configuration" -> Select "Commvault Disable Data Aging Logic App Playbook" -> Click on "Create Playbook" -> Finish steps -> Enter your KeyVault name in the "keyvaultName" parameter -> Click on "Create Playbook".
  - Repeat the above steps for other playbooks in the solution.

### Upload and Run PowerShell Script AssignLogicAppRoles

- Azure Cloud Shell -> Click on **Manage files** -> Upload `Tools\AssignLogicAppRoles.ps1` -> Run:
  ```powershell
  ./AssignLogicAppRoles.ps1
    ```

## Playbooks

### logic-app-disable-data-aging

Disables Archive Pruning for specified Commvault clients (by name or hostname).

### logic-app-disable-saml-provider

Disables SAML Identity Providers in the Commvault environment.

### logic-app-disable-user

Disables a specific user within the Commvault environment (by username).
