# Scalable Syslog collection using VMSS and Azure Monitor Agent

This ARM template  will deploy an Ubuntu 24.04 LTS Virtual Machine Scale Set to forward Syslog to Microsoft Sentinel using Azure Monitor Agent (AMA). This has been built based on the previous solution we had for CEF with Log Analytics Agent (MMA) [CEF-VMSS]( https://github.com/mariavaladas/Azure-Sentinel/tree/master/DataConnectors/CEF-VMSS)

The ARM template will deploy everything needed:
* Virtual Machine Scale Set
* Autoscale settings
* Network Security Group
* Virtual Network
* Subnet
* Public IP Address
* Load Balancer
* Data Collection Rule
* Data Collection Rule association
* Managed identity required for AMA to authenticate

The ARM template includes a cloud init to run the required to commands on the VM instances to enable syslog collection.

## Deploy Ubuntu VMSS
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FazureDeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FSyslog-VMSS-AMA%2FazureDeploy.json)

## Notes

This template was updated with the following fixes and modernizations:

* **Base image** upgraded from Ubuntu 18.04-LTS (end-of-life since April 2023) to Ubuntu 24.04 LTS.
* **NSG bug fixes:**
  * The `Allow-SSH` rule used `protocol: UDP`, which blocked SSH (TCP/22) reachable through the load balancer's inbound NAT pool — corrected to `Tcp`.
  * The `Allow-Syslog` rule used `protocol: UDP` only, which did not match the load balancer's TCP/514 syslog rule — broadened to `*` (TCP + UDP).
  * The subnet's NSG reference used an invalid resource provider `Microsoft.Networks/networkSecurityGroups` (extra "s") — corrected to `Microsoft.Network/networkSecurityGroups`.
* **AMA** Azure Monitor Linux Agent extension bumped from `1.22` to `1.33` (auto-upgrade remains enabled).
* **Autoscale** API version updated from `2014-04-01` to `2022-10-01`, and the scale-in/scale-out cooldown increased from 1 minute to 5 minutes to reduce scaling thrash.
* **Data Collection Rule / association** API version updated from `2021-09-01-preview` to the GA `2022-06-01`.

> Looking for **Syslog/CEF over TLS (port 6514)**? A community reference implementation that extends this template with mutual-TLS-capable certificate handling is available at [sentinel-syslog-tls-collector](https://github.com/x3nc0n/sentinel-syslog-tls-collector).
