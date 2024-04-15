# Scaleable SYSLOG CEF Collection using Logstash and VMSS
author: Nicholas DiCola

Sample is an ARM template that will deploy a Linux (RedHat or Unbuntu) Virtual Machine Scale Set with logstash installed with a basic config.  The Logstash config will listen on 5514 (Note: Logstash runs in as non-root and connect bind to 514 without special configuration) for SYSLOG CEF formatted messages.  It will then get the GEOIP information for src or dst IP Addresses and copy the send time to agentRecieptTime.  Lastly, it will output to the local Microsoft Monitoring Agent for ingestion to Azure Sentinel.

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
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FLogstash-VMSS%2FLogstash-VMSS-RH-Templatev2.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors2FLogstash-VMSS%2FLogstash-VMSS-RH-Templatev2.json)

## Deploy Unbuntu VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FLogstash-VMSS%2FLogstash-VMSS-UB-Templatev2.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors2FLogstash-VMSS%2FLogstash-VMSS-UB-Templatev2.json)