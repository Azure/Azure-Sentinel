# Group-IB TI - Open proxy indicator collector

Polls the Group-IB Threat Intelligence suspicious_ip/open_proxy collection hourly using incremental seqUpdate paging, converts open proxy IP addresses into STIX 2.1 indicators, and batches them to GIBTIA_IndicatorProcessor_v2 for upload to the Microsoft Sentinel threat intelligence store.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_Suspicious_ip_open_proxy%2Fazuredeploy.json)

## Prerequisites

- A Group-IB Threat Intelligence subscription with API access to the suspicious_ip/open_proxy collection.
- GIBTIA_IndicatorProcessor_v2 must be deployed first - this playbook batches indicators to it.
- A Log Analytics workspace connected to Microsoft Sentinel.
- The deploying account holds Owner or User Access Administrator on the resource group (the template creates role assignments), or the AssignRoles parameter is set to false.

## Post-deployment

1. Nothing to authorize: the playbook writes to Log Analytics through the Data Collection Rule this template created, using its managed identity. With AssignRoles left at true the template has also assigned the playbook's two roles (Monitoring Metrics Publisher on that rule, Log Analytics Reader on the workspace); with AssignRoles=false, assign them by hand.
2. Set the GIBUsername, GIBApiKey, StartDate and LimitPerPortion parameters.
3. Wait 5-15 minutes for the role assignments to propagate, then enable the Logic App. It deploys in a Disabled state by design.
4. Upgrading from 2.0: convert the workspace's GIB* tables once with migrate-tables.sh before redeploying (see the Playbooks readme).

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
