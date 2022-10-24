# Scalable Syslog collection using VMSS and Azure Monitor Agent

This ARM template  will deploy an Ubuntu Virtual Machine Scale Set. This has been built based on the previous solution we had for CEF based on the Log Analytics Agent (MMA) [CEF-VMSS]( https://github.com/mariavaladas/Azure-Sentinel/tree/master/DataConnectors/CEF-VMSS)

The ARM template will deploy everything needed:
* Virtual Machine Scale Set
* Autoscale settings
* Storage Account
* Network Security Group
* Virtual Network
* Subnet
* Public IP Address
* Load Balancer
* Data Collection Rule
* Data Colection Rule association
* Managed identity required for AMA to authenticate

The ARM template includes the cloud init files which runs commands on the VM instance when it is deployed.

## Deploy Ubuntu VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#blade/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmariavaladas%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FazureDeploy.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fmariavaladas%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FcreateUiDefinition.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#blade/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmariavaladas%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FazureDeploy.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fmariavaladas%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FcreateUiDefinition.json)
