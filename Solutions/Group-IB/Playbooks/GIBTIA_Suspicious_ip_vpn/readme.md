# Group-IB TI - VPN indicator collector

Polls the Group-IB Threat Intelligence suspicious_ip/vpn collection hourly using incremental seqUpdate paging, converts VPN IP addresses into STIX 2.1 indicators, and batches them to GIBTIA_IndicatorProcessor_v2 for upload to the Microsoft Sentinel threat intelligence store.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_Suspicious_ip_vpn%2Fazuredeploy.json)

## Prerequisites

- A Group-IB Threat Intelligence subscription with API access to the suspicious_ip/vpn collection.
- GIBTIA_IndicatorProcessor_v2 must be deployed first - this playbook batches indicators to it.
- A Log Analytics workspace connected to Microsoft Sentinel.

## Post-deployment

1. Authorize the Azure Monitor Logs and Azure Log Analytics Data Collector API connections.
2. Assign both the Microsoft Sentinel Contributor and Log Analytics Contributor roles to the playbook's managed identity at workspace scope. Both are required.
3. Set the GIBUsername, GIBApiKey, StartDate and LimitPerPortion parameters.
4. Enable the Logic App. It deploys in a Disabled state by design.

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
