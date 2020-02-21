# Scaleable SYSLOG CEF Collection using VMSS
author: Nicholas DiCola

Sample is an ARM template that will deploy a Linux (RedHat or Unbuntu) Virtual Machine Scale Set.

The ARM template will deploy everything needed:
* Virtual Machine Scale
* Autoscale settings
* Storage Account
* Network Security Group
* Virtual Network
* Subnet
* Public IP Address
* Load Balancer

The ARM template includes the cloud init files which runs commands on the VM instance when it is deployed.

## Deploy RedHat VMSS
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FCEF-VMSS%2FCEF-VMSS-RH-Templatev2.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FCEF-VMSS%2FCEF-VMSS-RH-Templatev2.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

## Deploy Unbuntu VMSS
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FCEF-VMSS%2FCEF-VMSS-UB-Templatev2.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors2FCEF-VMSS%2FCEF-VMSS-UB-Templatev2.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

