# Enrich-Sentinel-IPQualityScore-IP-Address-Reputation
author: David Mackler, IPQualityScore

This playbook uses the IPQS Fraud and Risk Scoring connector to automatically enrich IP Addresses found in the Sentinel incidents. This Playbook Template provides the Reputation such as **Critical, High Risk, Moderate Risk, Suspicious, Clean** based on Fraud Score. 

Learn more about the integration via the https://docs.microsoft.com/connectors/ipqsfraudandriskscor/ or visit https://www.ipqualityscore.com/contact-us to request a trial key.

## Sentinel Incident Comments Screenshot

![Incident Comments](./Graphics/comments.png)

## Reputation Threat Metrix

![Threat Metrix](./Graphics/ip_threat_metrix.png)

## Links to deploy the Enrich-Sentinel-IPQualityScore-IP-Address-Reputation playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIPQualityScore%2FPlaybooks%2FEnrich-Sentinel-IPQualityScore-IP-Address-Reputation%2Fazuredeploy.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIPQualityScore%2FPlaybooks%2FEnrich-Sentinel-IPQualityScore-IP-Address-Reputation%2Fazuredeploy.json)
