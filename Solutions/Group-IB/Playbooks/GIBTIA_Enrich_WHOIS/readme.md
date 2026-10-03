# Group-IB TI - Enrich incident with WHOIS data

Triggered by a Microsoft Sentinel incident. Runs a Group-IB WHOIS lookup for every IP and domain entity on the incident and posts registration and ownership details back as incident comments.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_Enrich_WHOIS%2Fazuredeploy.json)

## Prerequisites

- A Group-IB Threat Intelligence subscription with API access.
- A Log Analytics workspace connected to Microsoft Sentinel.

**Entity types:** `ip`, `dns`

## Post-deployment

1. Authorize the Microsoft Sentinel API connection.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity so it can add incident comments.
3. Set the GIBUsername and GIBApiKey parameters.
4. Attach the playbook to an automation rule so it runs when an incident is created.

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
