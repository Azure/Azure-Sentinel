# FullHunt - Domain Enrichment

## Summary

Enriches a DNS (domain) entity with FullHunt context: apex domain, known hosts and subdomains, WHOIS registrar and dates, host exposure summary (live, cloud and CDN hosts), passive DNS, cloud certificates and domain-collection context. Adds the results as an incident comment. Uses 4 FullHunt credits per run, or 5 when domain details are requested.

Lookups never trigger active scanning; they return FullHunt's existing data. A failed lookup (for example HTTP 403 when a FullHunt module is not enabled, or when credits are exhausted) is reported in the comment and does not stop the other lookups.

### Prerequisites

1. Deploy the FullHunt custom connector (Playbooks/FullHuntCustomConnector) to the same resource group first.
2. A FullHunt API key. Each lookup consumes 1 FullHunt credit.

### Deployment Instructions

1. Deploy the [FullHunt custom connector](../FullHuntCustomConnector/README.md) first.
2. Click the Deploy to Azure button. This launches the ARM template deployment wizard.
3. Fill in the parameters:
   * PlaybookName: Name of the playbook (Logic App) (default: FullHunt-EnrichDomain).
   * FullHuntConnectorName: Name of the deployed FullHunt custom connector (default: FullHuntCustomConnector).
   * MaxHostsForDetails: Call domain details (full host records) only when the domain has at most this many hosts (default: 500).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichDomain%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichDomain%2Fazuredeploy.json)

### Post-Deployment Instructions

1. Authorize the FullHunt API connection: open the Logic App, select API connections, choose the FullHunt connection, select Edit API connection, enter your FullHunt API key and save.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity on the Microsoft Sentinel workspace, so it can read incidents and add comments.
3. Run the playbook from a DNS entity in an incident, or from an automation rule. Subdomains are resolved to their registrable (apex) domain automatically.
