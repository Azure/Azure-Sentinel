# Group-IB TI - Indicator processor (required adapter)

Required adapter for the Group-IB collector playbooks. Receives batched STIX 2.1 indicators from the collectors and uploads them to Microsoft Sentinel with Upload_Indicators_V2 using a managed identity. Deploy this playbook before any Group-IB collector.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_IndicatorProcessor_v2%2Fazuredeploy.json)

## Prerequisites

- A Log Analytics workspace connected to Microsoft Sentinel.

## Post-deployment

1. Assign the Microsoft Sentinel Contributor role to the playbook's managed identity at workspace scope.
2. Enable the Logic App. It deploys in a Disabled state by design.
3. Deploy the Group-IB collector playbooks afterwards. Each one batches indicators to this adapter by name.

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
