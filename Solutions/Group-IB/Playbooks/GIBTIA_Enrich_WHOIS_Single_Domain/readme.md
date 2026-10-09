# Group-IB TI - WHOIS lookup for a single domain entity

Entity-triggered playbook. Run it against a single domain entity from the incident investigation graph or the entity page to retrieve Group-IB WHOIS registration data and post the result as an incident comment.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_Enrich_WHOIS_Single_Domain%2Fazuredeploy.json)

## Prerequisites

- A Group-IB Threat Intelligence subscription with API access.
- A Log Analytics workspace connected to Microsoft Sentinel.

**Entity types:** `dns`

## Post-deployment

1. Authorize the Microsoft Sentinel API connection.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity so it can add incident comments.
3. Set the GIBUsername and GIBApiKey parameters.
4. Run it from an incident's investigation graph or from the entity page using Run playbook. Entity-triggered playbooks cannot be attached to automation rules.
5. When run outside an incident the enrichment still executes, but there is no incident to comment on - the result is visible in the Logic App run history.

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
