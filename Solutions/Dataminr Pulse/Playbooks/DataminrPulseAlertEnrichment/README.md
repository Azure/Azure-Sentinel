# Dataminr Pulse Alert Enrichment

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)


## Summary<a name="Summary"></a>

This playbook provides an end-to-end example of how alert enrichment works. This will extract the IP, Domain, HostName, URL or Hashes from the generated incident and call the Get alerts API of Dataminr Pulse to get the data associated with that parameter and enrich the incident by adding Dataminr Pulse alerts data as an incident comment.

### Prerequisites<a name="Prerequisites"></a>

1. Users must have a valid pair of Dataminr Pulse API Client ID and secret credentials.
2. Store client credentials in Key Vault and obtain keyvault name and tenantId.
    * Create a Key Vault with unique name
    * Go to KeyVault -> secrets -> Generate/import and create 'DataMinrPulse-clientId'& 'DataMinrPulse-clientSecret' to store client_id and client_secret respectively. Also create a secret named 'DataMinrPulse-DmaToken' to store dmaToken.

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Key Vault Name: Name of keyvault where secrets are stored.
    * Tenant Id: TenantId of azure active directory where keyvault is located.
    * BaseURL: Baseurl for your Dataminr account.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDataminr%20Pulse%2FPlaybooks%2FDataminrPulseAlertEnrichment%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fportal.azure.us%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDataminr%20Pulse%2FPlaybooks%2FDataminrPulseAlertEnrichment%2Fazuredeploy.json)


### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Keyvault connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Assign Role to add comment in incident

After authorizing each connection, assign role to this playbook.

1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles
4. Role: Microsoft Sentinel Contributor
5. Members: select managed identity for "assigned access to" and add your logic app as member.
6. Click on review+assign

#### c. Add Access policy in Keyvault

Add access policy for playbook's managed identity to read, write secrets of keyvault.

1. Go to logic app → <your logic app> → identity → System assigned Managed identity and copied it.
2. Go to keyvaults → <your keyvault> → Access policies → create.
3. Select all keys & secrets permissions. Click next.
4. In principal section, search by copied identity object ID. Click next.
5. Click review + create.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, Configure the analytic rules to trigger an incident.
  * Analytic Rule must contain atleast one of the below fields mapped in Custom Details to successfully run this playbook.
    * DstDomain
    * DstHostname
    * DstIpAddr
    * DstMacAddr
    * SrcDomain
    * SrcFileMD5
    * SrcFileSHA1
    * SrcFileSHA256
    * SrcFileSHA512
    * SrcHostname
    * SrcIpAddr
    * SrcMacAddr
    * TargetFileMD5
    * TargetFileSHA1
    * TargetFileSHA256
    * TargetFileSHA512
    * Url
2. In Microsoft Sentinel, Configure the automation rules to trigger the playbook. 
  * Go to Microsoft Sentinel -> <your workspace> -> Automation 
  * Click on **Create** -> **Automation rule**
  * Provide name for your rule
  * In Analytic rule name condition, select analytic rule which you have created.
  * In Actions dropdown select **Run playbook**
  * In second dropdown select your deployed playbook
  * Click on **Apply**
  * Save the Automation rule.
