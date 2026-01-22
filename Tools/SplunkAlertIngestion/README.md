Author: Kosta Sotic, Senior Security Architect - Customer Success Tech Strategy @ Microsoft

Permissions needed:
- User Access Administrator on the resource group where Sentinel is (for granting permissions to the created Data Collection Rule)
- Contributor on the resource group where Sentinel is (for creating needed Azure resources)

PowerShell script can be run from Azure Cloud Shell:
- Upload DCR, LogicApp and main.ps1 to your Azure Cloud Shell
- Run the script with all the required parameters (./SplunkAlertIngestion.ps1 -ServicePrincipalName "" -tableName "" -workspaceResourceId "" -dataCollectionRuleName "" -location "")
- After the script has completed, LogicApp trigger URL will be displayed, copy that value

  As a last step, on Splunk side edit alert for which you want to send to Sentinel and create a trigger action for the Webhook. In the URL portion paste the URL you got from the completed script and Save.



