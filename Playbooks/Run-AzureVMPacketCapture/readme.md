# Run-AzureVMPacketCapture
author: Nathan Swift

This playbook will take start a packet capture on a Azure VM Windows or Linux using Network Watcher, the capture will run for ten minutes, and will be stored on a blob storage account.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRun-AzureVMPacketCapture%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRun-AzureVMPacketCapture%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

**Additional Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to authenticate and authorize against management.azure.com to searhch the hostname entity in Azure Resource Graph and execute a packet capture on the Azure VM. Your Azure VM must have the Network Watcher extension installed.

Assign RBAC 'Reader' role to the Logic App at the Subscription level.
Assign RBAC 'Virtual Machine Contributor' role to the Logic App at the Subscription level.
Assign RBAC 'Network Contributor' role to the Logic App at the Subscription level.