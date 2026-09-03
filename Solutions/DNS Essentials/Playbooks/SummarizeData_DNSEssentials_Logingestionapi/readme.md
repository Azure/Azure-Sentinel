# DNS Essentials Summarization Capability

This Logic App ingests summarized DNS data into custom Log Analytics tables by using the Logs Ingestion API. Enabling this playbook incurs additional cost.

## Summary

The playbook improves DNS Essentials solution performance by creating two tables containing analytics based on the ASIM DNS schema:

- `DNS_Summarized_Logs_sourceInfoV1_CL`
- `DNS_Summarized_Logs_ipV1_CL`

The V1 table names avoid conflicts with existing classic tables. The playbook uses a data collection endpoint (DCE), data collection rule (DCR), and its managed identity to ingest summarized data.

## Deployment Instructions

1. Deploy the playbook by selecting the applicable button:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F6b56bc665b5d452ecd4819f5168149016fff0a5e%2FSolutions%2FDNS%2520Essentials%2FPlaybooks%2FSummarizeData_DNSEssentials_Logingestionapi%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F6b56bc665b5d452ecd4819f5168149016fff0a5e%2FSolutions%2FDNS%2520Essentials%2FPlaybooks%2FSummarizeData_DNSEssentials_Logingestionapi%2Fazuredeploy.json)

2. Deploy the playbook to a resource group in the same Azure region as the Log Analytics workspace.
3. Provide the required parameters:
   - **Playbook Name**: The default is `SummarizeDNSData_DNS_logingestion`.
   - **Log Analytics Name**: The Log Analytics workspace that contains the DNS data.
   - **Resource Group Name** and **Subscription ID**: The workspace resource group and subscription.

The deployment creates the DCE, DCR, V1 custom tables, and grants the playbook managed identity the Monitoring Metrics Publisher role on the DCR.

## Post-Deployment Instructions

Authorize the Azure Monitor Logs API connection if prompted:

1. Open the Azure Monitor Logs API connection.
2. Select **Edit API connection**.
3. Select **Authorize**, sign in, and then save the connection.

The Logs Ingestion API uses the playbook's managed identity. No Azure Log Analytics Data Collector connection or workspace key is required.