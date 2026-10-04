# FullHunt - IP Enrichment

## Summary

Enriches an IP entity with FullHunt context: ASN, organization, geolocation, cloud and CDN provider, hosts observed on the IP, and Tor exit node status. Adds the results as an incident comment. Uses 3 FullHunt credits per run (2 for IPv6).

Lookups never trigger active scanning; they return FullHunt's existing data. A failed lookup (for example HTTP 403 when a FullHunt module is not enabled, or when credits are exhausted) is reported in the comment and does not stop the other lookups.

### Prerequisites

1. Deploy the FullHunt custom connector (Playbooks/FullHuntCustomConnector) to the same resource group first.
2. A FullHunt API key. Each lookup consumes 1 FullHunt credit.
3. The intel lookup requires the FullHunt Data Intelligence module; without it the comment notes HTTP 403 and the other lookups still run.

### Deployment Instructions

1. Deploy the [FullHunt custom connector](../FullHuntCustomConnector/README.md) first.
2. Click the Deploy to Azure button. This launches the ARM template deployment wizard.
3. Fill in the parameters:
   * PlaybookName: Name of the playbook (Logic App) (default: FullHunt-EnrichIP).
   * FullHuntConnectorName: Name of the deployed FullHunt custom connector (default: FullHuntCustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichIP%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichIP%2Fazuredeploy.json)

### Post-Deployment Instructions

1. Authorize the FullHunt API connection: open the Logic App, select API connections, choose the FullHunt connection, select Edit API connection, enter your FullHunt API key and save.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity on the Microsoft Sentinel workspace, so it can read incidents and add comments.
3. Run the playbook from an IP entity in an incident, or from an automation rule.
