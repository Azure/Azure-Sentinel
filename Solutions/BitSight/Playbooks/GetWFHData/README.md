# BitSight Get WFH Data

* [Summary](#Summary)
* [Prerequisites](#Prerequisites)
* [Deployment instructions](#Deployment-instructions)
* [Post-Deployment instructions](#Post-Deployment-instructions)


## Summary<a name="Summary"></a>

This playbook provides an end to end example of the collection of WFH information from BitSight. This will extract the IP from network session ASIM data and call the WFH api of BitSight to get the data of that specific IP and store the relevant WFH custom log table into a log analytic workspace.

### Prerequisites<a name="Prerequisites"></a>

1. Store BitSight account credentials in Key Vault and obtain keyvault name and tenantId from azure active directory.
    * Create a Key Vault with unique name
    * Go to KeyVault -> secrets -> Generate/import and create 'API-token' for storing BitSight API token

### Deployment instructions<a name="Deployment-instructions"></a>

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * Key Vault Name: Name of keyvault where secrets are stored.
    * Tenant Id: TenantId of azure active directory where keyvault is located.
    * Log Analytics Workspace Id: Id of workspace where you want to store data of WFH.
    * Log Analytics Workspace Key: Key of workspace where you want to store data of WFH.
    * WFH Table Name: WFH data table name. 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https%3A%2F%2Fportal.azure.com%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FBitSight%2FPlaybooks%2FGetWFHData%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https%3A%2F%2Fportal.azure.us%2F%23create%2FMicrosoft.Template%2Furi%2Fhttps%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FBitSight%2FPlaybooks%2FGetWFHData%2Fazuredeploy.json)

### Post-Deployment instructions<a name="Post-Deployment-instructions"></a>

##### a. Authorize connections

Once deployment is complete, authorize each connection like keyvault.

1. Click the connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save

##### b. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, one should have deployed an [ASimNetworkSession parser](https://github.com/Azure/Azure-Sentinel/tree/master/Parsers/ASimNetworkSession).
2. In Microsoft Sentinel, analytics rules should be configured to trigger an incident. 
  > 1. Add your deployed logic app in analytic rule to be trigger on every generated incident, to do this follow below steps
  >> * Select the analytic rule you have deployed.
  >> * Click on **Edit**
  >> * Go to **Automated response** tab
  >> * Click on **Add new**
  >> * Provide name for your rule, In Actions dropdown select **Run playbook**
  >> * In second dropdown select your deployed playbook
  >> * Click on **Apply**
  >> * Save the Analytic rule.
  > 2. An incident should have the **ip_address** - custom entity that contains Src ip address from ASimNetworkSession.  

#### Sample analytics rule query
```
ASimNetworkSession
| where EventSchema == "NetworkSession"
