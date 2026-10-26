# Group-IB TI - Score incident IP addresses

Triggered by a Microsoft Sentinel incident. Retrieves the Group-IB risk score and associated categories for every IP entity on the incident and posts the result back as an incident comment.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_Score_IP%2Fazuredeploy.json)

## Prerequisites

- A Group-IB Threat Intelligence subscription with API access.
- A Log Analytics workspace connected to Microsoft Sentinel.

**Entity types:** `ip`

## Post-deployment

1. Authorize the Microsoft Sentinel API connection.
2. Assign the Microsoft Sentinel Responder role to the playbook's managed identity so it can add incident comments.
3. Set the GIBUsername and GIBApiKey parameters.
4. Attach the playbook to an automation rule so it runs when an incident is created.

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
