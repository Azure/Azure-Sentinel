# CrowdStrike_Base 
 ## Summary
This is Crowdstrike base template which is used to generate access token and this is used in actual crowdstrike templates. This playbook gets triggered when a new Http request is created and this is being called from other Crowdstrike playbooks.

![CrowdStrike_Base](./images/designerScreenshotLight.png)
### Prerequisites 

1. Azure Key vault is required for storing the Crowdstrike ClientID and Secrets, create key vault if not exists [learn how](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2F201-key-vault-secret-create%2Fazuredeploy.json)
2. Add Crowdstrike Client ID and Client Secret in Key vault secrets and capture the keys which are required during the template deployment


### Deployment instructions 
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:

    * keyvault_vaultName: Enter the Key vault name where the client ID and client secret is stored. secrets in key vault are used to generate the authorization key.
    * ClientID: Enter the client Id key name used in key vault
    * ClientSecret: Enter the client secret key name used in key vault
    * Service_Endpoint: Enter the service endpoint of crowdstrike ex: {https://crowdsrtikeurl.com}
    * Playbook_Name: Enter the playbook name here (Ex:CrowdStrike_Base)
    
    
### Post-Deployment instructions 
#### a. Authorize playbook
Once deployment is complete, we need to add the playbook in the access policy of the Keyvault [learn how](https://docs.microsoft.com/azure/key-vault/general/assign-access-policy-portal)


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCrowdStrike%2FPlaybooks%2FCrowdStrike_Base%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCrowdStrike%2FPlaybooks%2FCrowdStrike_Base%2Fazuredeploy.json)


## Playbook steps explained

### When a Http request is received
When a http request is received from another playbook or if this playbook is run manually, this playbook will be triggered

### Initialize variable ClientID
Initialize a string variable which holds the ClientID key name from Keyvault

### Initialize variable ClientSecret
Initialize a string variable which holds the ClientSecret key name from Keyvault

### Get secret - Client ID
This gets the Client Id secret Value from Keyvault

### Get secret - Client Secret
This gets the ClientSecret secret Value from Keyvault

### Initialize variable Falcon Host URL
Initialize a string variable which holds the crowdstrike host Url

### HTTP - Get Access Token
This action will get the OAuth2 access token from Crowdstike using ClientID and ClientSecret as inputs

### Parse JSON - Access Token Response
This action will parse the response in to Json format

### Response
This holds the access token and Crowdstrike host URL
