# Group-IB TI - Public leak collector

Polls the Group-IB Threat Intelligence osi/public_leak collection hourly using incremental seqUpdate paging and writes public data leaks to the GIBOSIPublicLeak_CL custom table in Log Analytics for use in analytics rules and hunting queries.

## Quick Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FGIBTIA_OSI_PublicLeak%2Fazuredeploy.json)

## Prerequisites

- A Group-IB Threat Intelligence subscription with API access to the osi/public_leak collection.
- A Log Analytics workspace connected to Microsoft Sentinel.

## Post-deployment

1. Authorize the Azure Monitor Logs and Azure Log Analytics Data Collector API connections.
2. Assign both the Microsoft Sentinel Contributor and Log Analytics Contributor roles to the playbook's managed identity at workspace scope. Both are required.
3. Set the GIBUsername, GIBApiKey, StartDate and LimitPerPortion parameters.
4. Enable the Logic App. It deploys in a Disabled state by design. Records appear in GIBOSIPublicLeak_CL after the first successful run.

---

Part of the Group-IB Threat Intelligence integration. See [the Playbooks readme](../readme.md) for the full catalog, architecture and deployment order.
