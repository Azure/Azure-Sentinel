# Commvault -- Sentinel Integration

This Sentinel integration enables Commvault users to ingest alerts and other data into their Sentinel instance. With Analytic Rules, Sentinel can automatically create Sentinel incidents from incoming events and logs.

## Key Features

- Using Azure KeyVault, Commvault access tokens are automatically rotated, providing enhanced security.
- Perform automated actions such as disabling IDP, specific users, or data aging on your Commvault/Metallic environment from inside Sentinel.

## Prerequisites

- Administrative access to your Commvault/Metallic environment.
- Administrative access to your Azure Resource Group and Subscription.
- Access to your Azure Cloud Shell.
- A Microsoft Sentinel instance in the aforementioned Azure Resource Group.
- An Azure Log Analytic Workspace in the aforementioned Azure Resource Group.

## Inventory of Required Assets

The following Azure assets need to all be created in order for this integration to function properly. In addition to these assets, proper permissions need to be granted. When following the installation instructions, please use the same asset names to ensure compatibility.

### KeyVault

- A KeyVault which stores all required credentials as *secrets*.

### KeyVault Secrets

All of these secrets are stored in the KeyVault mentioned above. For the first time setup, their values need to be manually retrieved.

- **access-token:** The access token for Commvault/Metallic.
- **environment-endpoint-url:** The URL of your Commvault/Metallic endpoint. Which is in the format:
  - Command center url: https://*{hostname}*/commandcenter/api
  - WebService url: http://*{hostname}*:*{port}*/SearchSvc/CVWebService.svc

### Sentinel Analytic Rules

Each of these Analytic Rules run on a continuous basis and are querying for the manually triggered Sentinel incident. Once it discovers a specific incident, a new incident is created that triggers the corresponding Automation Rule.

- **IDP Compromised:** The Sentinel Analytic Rule that continuously searches for a manually created Sentinel Incident pertaining to a compromised Commvault/Metallic IDP.
- **User Compromised:** The Sentinel Analytic Rule that continuously searches for a manually created Sentinel Incident pertaining to a compromised Commvault/Metallic user.
- **Data Aging:** The Sentinel Analytic Rule that continuously searches for a manually created Sentinel Incident pertaining to a request to disable data aging on a specific Commvault/Metallic client.

## Installation

### Create The KeyVault

- Go to KeyVault -> Create
  - Basics:
    - Select the correct subscription and resource group
    - KeyVault name:
      - Commvault-Integration-KV

### Create the KeyVault Secrets

- Go to KeyVault -> "Commvault-Integration-KV" -> Secrets (Under "Objects") -> "Generate/Import"
  - Upload Options:
    - Manual
  - Name:
    - access-token
  - Secret Value:
    - (Your Commvault/Metallic access token)
  - Enabled:
    - Yes
  - Click "Create"
- Go to KeyVault -> "Commvault-Integration-KV" -> Secrets (Under "Objects") -> "Generate/Import"
  - Upload Options:
    - Manual
  - Name:
    - environment-endpoint-url
  - Secret Value:
    - (Your Commvault/Metallic endpoint's URL)
  - Enabled:
    - Yes
  - Click "Create"

### Install Commvault Cloud Solution

- Go to Sentinel -> Content hub (located under “Configuration”) -> Search for "Commvault Cloud" -> Install

### Upload and Run PowerShell Script Setup-CommvaultAutomation

- Open Azure Cloud Shell
- Upload the file `Tools\Setup-CommvaultAutomation.ps1` to Azure Cloud Shell
- Run the PowerShell script, before the step `Create the Analytic Rules`:

  ```powershell
  ./Setup-CommvaultAutomation.ps1
    ```

### Create the Analytic Rules

- Go to Sentinel -> Content hub (located under “Configuration”) -> Click on "Commvault Cloud" -> Click on "Manage"
- Click on "CommvaultSecurityIQ Alert" -> Click on "Create Rule" -> Follow the steps by clicking "Next" -> Click on "Save" in the last step
- Repeat the above steps for the other Analytic rules in the solution

### Create the Playbooks

- Go to Sentinel -> Content hub (located under “Configuration”) -> Click on "Commvault Cloud" -> Click on "Manage"
- Click on "logic-app-disable-data-aging" -> Click on "Configuration" -> Select "Commvault Disable Data Aging Logic App Playbook" -> Click on "Create Playbook"
- Finish the steps by clicking Next
- Enter the keyvault name used in above steps in the Parameter "keyvaultName"
- Click on "Create Playbook" after finishing all the steps.
- Repeat the above steps for other playbooks in the solution

### Upload and Run PowerShell Script AssignLogicAppRoles

- Open Azure Cloud Shell
- Upload the file `Tools\AssignLogicAppRoles.ps1` to Azure Cloud Shell
- Run the PowerShell script, after the step `Create the Playbooks`:

  ```powershell
  ./AssignLogicAppRoles.ps1
    ```

## Playbooks

### logic-app-disable-data-aging

This script disables the Archive Pruning feature for clients in Commvault based on the provided client name or hostname.

### logic-app-disable-saml-provider

This script disables the SAML Identity Providers in the environment.

### logic-app-disable-user

This script disables the user in Commvault environment based on the username provided.
