# Scaleable SYSLOG CEF Collection using FluentD and VMSS
author: Nicholas DiCola

Sample is an ARM template that will deploy a Linux (RedHat or Unbuntu) Virtual Machine Scale Set with FluentD installed with a basic config.  The FluentD config will listen on 5514 for SYSLOG CEF formatted messages.  It will then get the GEOIP information for src or dst IP Addresses and copy the send time to agentRecieptTime.  Lastly, it will output to the local Microsoft Monitoring Agent for ingestion to Azure Sentinel.

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

***NOTE: You will need to register for the Free GeoLite Database and provide a URL that cloud-init can download the datebase (GeoLite2-City.mmdb) it from.  See https://dev.maxmind.com/geoip/geoip2/geolite2/***


## Deploy RedHat VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FFluentD-VMSS%2FFluentD-VMSS-RH-Templatev2.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors2FFluentD-VMSS%2FFluentD-VMSS-RH-Templatev2.json)

## Deploy Unbuntu VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FFluentd-VMSS%2FFluentD-VMSS-UB-Templatev2.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors2FFluentD-VMSS%2FFluentD-VMSS-UB-Templatev2.json)