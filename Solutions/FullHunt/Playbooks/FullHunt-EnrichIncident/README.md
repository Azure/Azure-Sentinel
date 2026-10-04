# FullHunt - Incident Enrichment

## Summary

Enriches the IP, Host, URL and DNS entities of a Microsoft Sentinel incident with FullHunt context and adds one consolidated incident comment: IP network and Tor context, host exposure (IP, live status, open ports, organization), and domain context (apex, known hosts, WHOIS). Uses up to 2 credits per IP and 1 per host, URL or domain, capped by MaxEntitiesPerType.

Lookups never trigger active scanning; they return FullHunt's existing data. A failed lookup (for example HTTP 403 when a FullHunt module is not enabled, or when credits are exhausted) is reported in the comment and does not stop the other lookups.

### Prerequisites

1. Deploy the FullHunt custom connector (Playbooks/FullHuntCustomConnector) to the same resource group first.
2. A FullHunt API key. Each lookup consumes 1 FullHunt credit.

### Deployment Instructions

1. Deploy the [FullHunt custom connector](../FullHuntCustomConnector/README.md) first.
2. Click the Deploy to Azure button. This launches the ARM template deployment wizard.
3. Fill in the parameters:
   * PlaybookName: Name of the playbook (Logic App) (default: FullHunt-EnrichIncident).
   * FullHuntConnectorName: Name of the deployed FullHunt custom connector (default: FullHuntCustomConnector).
   * MaxEntitiesPerType: Maximum number of entities of each type to look up per incident (limits FullHunt credit use) (default: 5).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichIncident%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHunt-EnrichIncident%2Fazuredeploy.json)

### Post-Deployment Instructions

1. Authorize the FullHunt API connection: open the Logic App, select API connections, choose the FullHunt connection, select Edit API connection, enter your FullHunt API key and save.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity on the Microsoft Sentinel workspace, so it can read incidents and add comments.
3. Create an automation rule that runs this playbook when incidents are created. For deeper single-entity lookups use the FullHunt IP, Host and Domain enrichment playbooks.
