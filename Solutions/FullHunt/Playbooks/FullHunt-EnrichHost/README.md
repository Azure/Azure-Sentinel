# FullHunt - Host Enrichment

## Summary

Enriches a Host entity (host name plus DNS domain) with FullHunt's attack surface record: IP, live status, open ports, ASN, cloud and CDN, tags, TLS certificate and last seen. Adds the results as an incident comment. Uses 2 FullHunt credits per run.

Lookups never trigger active scanning; they return FullHunt's existing data. A failed lookup (for example HTTP 403 when a FullHunt module is not enabled, or when credits are exhausted) is reported in the comment and does not stop the other lookups.

### Prerequisites

1. Deploy the FullHunt custom connector (Playbooks/FullHuntCustomConnector) to the same resource group first.
2. A FullHunt API key. Each lookup consumes 1 FullHunt credit.
3. The intel lookup requires the FullHunt Data Intelligence module; without it the comment notes HTTP 403 and the host lookup still runs.

### Deployment Instructions

1. Deploy the [FullHunt custom connector](../FullHuntCustomConnector/README.md) first.
2. Click the Deploy to Azure button. This launches the ARM template deployment wizard.
3. Fill in the parameters:
   * PlaybookName: Name of the playbook (Logic App) (default: FullHunt-EnrichHost).
   * FullHuntConnectorName: Name of the deployed FullHunt custom connector (default: FullHuntCustomConnector).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichHost%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichHost%2Fazuredeploy.json)

### Post-Deployment Instructions

1. Authorize the FullHunt API connection: open the Logic App, select API connections, choose the FullHunt connection, select Edit API connection, enter your FullHunt API key and save.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity on the Microsoft Sentinel workspace, so it can read incidents and add comments.
3. Run the playbook from a Host entity in an incident, or from an automation rule. Host names that are not public DNS names (for example internal machine names) return no FullHunt data.
