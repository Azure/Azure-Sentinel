# Scaleable NetFlow Collection using FileBeat, Logstash and VMSS
author: Nicholas DiCola

Sample is an ARM template that will deploy a Linux (Unbuntu) Virtual Machine Scale Set with FileBeat and Logstash installed with a basic config.  The FileBeat config will listen on 2055 publicly via Azure Load Balancer. Logstash config will listen locally on 5044 for Beats input. It will then get the GEOIP information for src and/or dst IP Addresses and copy the send time to agentRecieptTime.  Lastly, it will output using the Microsoft-Output-LogAnaltics plugin for ingestion to Azure Sentinel as netflow_CL.

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

## Deploy Unbuntu VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FNetFlow%2FNetFlow-VMSS-UB-Templatev2.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors2FNetFlow%2FNetFlow-VMSS-UB-Templatev2.json)