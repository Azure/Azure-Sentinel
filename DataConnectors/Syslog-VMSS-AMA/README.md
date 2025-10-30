# Scalable Syslog collection using VMSS and Azure Monitor Agent

This ARM template  will deploy an Ubuntu Virtual Machine Scale Set to forward Syslog to Microsoft Sentinel using Azure Monitor Agent (AMA). This has been built based on the previous solution we had for CEF with Log Analytics Agent (MMA) [CEF-VMSS]( https://github.com/mariavaladas/Azure-Sentinel/tree/master/DataConnectors/CEF-VMSS)

The ARM template will deploy everything needed:
* Virtual Machine Scale Set
* Autoscale settings
* Network Security Group
* Virtual Network
* Subnet
* Public IP Address
* Load Balancer
* Data Collection Rule
* Data Colection Rule association
* Managed identity required for AMA to authenticate

The ARM template includes a cloud init to run the required to commands on the VM instances to enable syslog collection.

## Deploy Ubuntu VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FazureDeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FazureDeploy.json)
