# Defender for office 365 API Functions App Connector

This Functions App Connector is to connect Defender for office 365 API.

### Authentication methods supported by this connector

* Custom Authentication/Certificate Authentication

### Prerequisites For Defender for office 365 API Functions App Connector

* App Registration on azure active directory is needed , Beacuse this connector uses certificate thumprints for Authentication 
* Self generated certificate / 3rd party certificates in pfx format.

## Actions supported by AWS Systems Manager API Functions App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **Connect Exchange** | Create Session for execution of commands on office 365 cloud  |
| **Disconnect Exchange** | Finish/Clear the session created by connect exchange|
| **ListSpamPolicy** | View existing spam filter policies |
| **CreateSpamPolicy** | Create a spam filter policy |
| **CreateSpamRule** | Create a spam filter rule |
| **TenantAllowBlockList** | View entries for email addresses in the Tenant Allow/Block List|
| **CreateAllowBlockList** | create block entries for email addresses in the Tenant Allow/Block List |
| **UpdateAllowBlockList** | Modify entries for email addresses in the Tenant Allow/Block List |
| **RemoveAllowBlockListItems** | Remove entries for email addresses from the Tenant Allow/Block List |
| **ListMalwarePolicy** | View existing malware filter policies|
| **BlockMalwareFileExtension** | Add Malware file extensions to malware policy block list |

### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Function App Name

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS%2520Systems%2520Manager%2FPlaybooks%2FCustomConnector%2FAWS_SSM_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS%2520Systems%2520Manager%2FPlaybooks%2FCustomConnector%2FAWS_SSM_FunctionAppConnector%2Fazuredeploy.json)

### Post Deployment Instructions
1. Register the application in Azure AD [click the link and follow the steps](https://learn.microsoft.com/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps)
2. Once application is registered , Kindly follow the steps mentioned below
	- Store the Application ID , that will be required later when deploying the playbooks.
	- Create the self signed certificate : New-PnPAzureCertificate -OutPfx pnp.pfx -OutCert pnp.cer
	- Upload your client certificate(cer file) to the AD application
	- Upload your pfx file to Azure function : az webapp config ssl upload --certificate-file "e:\cert\pnp.pfx"  --name "<function app name>" --resource-group ""  --certificate-password "" --query thumbprint --output tsv
	- Configure Function to allow the function to read the certificate : az functionapp config appsettings set --name <app-name> --resource-group <resource-group-name> --settings WEBSITE_LOAD_CERTIFICATES=<comma-separated-certificate-thumbprints>
    - Store the thumbprint in Keyvault under secrets and have the secret name handy ,that will be required to enter under Certificate_key_name during the playbook deployment 

### How to use Defender for office 365 function app custom Connector
1. First connect to Exchange using "Connect Exchange"
2. Once you are done with work , dont forget to call "Disconnect Exchange" action

### Request body paylod of Defender for office 365 function app custom Connector actions


### References
- [Defender for office 365 Documentation](https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/anti-spam-policies-configure?view=o365-worldwide)