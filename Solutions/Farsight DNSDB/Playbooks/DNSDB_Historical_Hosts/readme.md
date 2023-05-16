# DNSDB_Historical_Hosts
author: Henry Stern, Farsight Security, Inc.

This playbook uses the Farsight DNSDB connector to automatically enrich IP Addresses found in the Sentinel incidents. This use case describes the desire to identify all Hosts that resolved to a given Address based on a time window from a starting and stopping point in time. 
Learn more about the integration via the https://docs.microsoft.com/connectors/farsightdnsdb/ or visit https://www.farsightsecurity.com/about-farsight-security/contacts/ to request a trial key.

## Screenshots

![Incident Comments](./Graphics/historical_hosts.png)


## Links to deploy the DNSDB_Historical_Hosts playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFarsight%20DNSDB%2FPlaybooks%2FDNSDB_Historical_Hosts%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFarsight%20DNSDB%2FPlaybooks%2FDNSDB_Historical_Hosts%2Fazuredeploy.json)
