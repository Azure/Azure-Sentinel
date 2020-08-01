# Deploy Function App for getting Oracle Cloud Identity Audit Events data into Azure Sentinel
This function app will poll Oracle Cloud Identity Audit Events API every 5 mins for logs.  It is designed to get AuditEvents.

## Deployment and Configuration
### Add Oracle Confidential App, Generate Base 64 ClientID:ClientSecret string, and Find IDCS Uri
1. Review: https://aka.ms/AA94w2h

#### : Deploy via Azure ARM Template
1.  Deploy the template.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FOIDCS%20Data%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>

2. Deploy permissions for the function to the Key Vault.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FOIDCS%20Data%2Fazuredeploy2.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>

### Assign MSI OIDCS Data Function
1. Go to Azure Sentinel Workspace and IAM Blade and add OIDCS Data Function as a Reader Role

### Confiugure Settings for the Function
1. Go to the Azure Portal.
2. Go to the resource group that was created.  Click the Function.
3. Click Platform Features Tab.
4. Click Configuration under General.
5. click edit next to b64clientidsecret.
6. Update the value using your copied properties.
* @Microsoft.KeyVault(SecretUri=https://<dnsname>/secrets/b64clientidsecret/<versionstring>)
7. Click Ok.
8. click edit next to workspaceKey.
9. Update the value using your copied properties
* @Microsoft.KeyVault(SecretUri=https://<dnsname>/secrets/workspaceKey/<versionstring>)
10. Click Ok.
11.  Update each setting
* ICDS = idcs-YOURCLOUDINSTANCE.identity.oraclecloud.com
* workspaceId is your Azure Sentinel workspace id
12. Click Save
13. Go back to the function and click start under the overview blade.
