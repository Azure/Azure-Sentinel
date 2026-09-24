# Web Session Essentials Summarization Capability

This Logic App ingests summarized Web Session data into custom Log Analytics tables by using the Logs Ingestion API. Enabling this playbook incurs additional cost.

## Summary

The playbook improves Web Session Essentials solution performance by creating four tables containing analytics based on the ASIM Web Session schema:

- `WebSession_Summarized_SrcInfoV1_CL`
- `WebSession_Summarized_SrcIPV1_CL`
- `WebSession_Summarized_DstIPV1_CL`
- `WebSession_Summarized_ThreatInfoV1_CL`

The V1 table names avoid conflicts with existing classic tables. The playbook uses a data collection endpoint (DCE), data collection rule (DCR), and its managed identity to ingest summarized data.

## Deployment Instructions

1. Deploy the playbook by selecting the applicable button:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F7c679ec0cbcbaf50c510bb534592e054a540983f%2FSolutions%2FWeb%2520Session%2520Essentials%2FPlaybooks%2FSummarizeWebSessionData_logingestion%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F7c679ec0cbcbaf50c510bb534592e054a540983f%2FSolutions%2FWeb%2520Session%2520Essentials%2FPlaybooks%2FSummarizeWebSessionData_logingestion%2Fazuredeploy.json)

2. Deploy the playbook to a resource group in the same Azure region as the Log Analytics workspace.
3. Provide the required parameters:
   - **Playbook Name**: The default is `SummarizeWebSessionData-logingestion`.
   - **Log Analytics Name**: The Log Analytics workspace that contains the Web Session data.
   - **Resource Group Name** and **Subscription ID**: The workspace resource group and subscription.

The deployment creates the DCE, DCR, V1 custom tables, and grants the playbook managed identity the Monitoring Metrics Publisher role on the DCR.

## Post-Deployment Instructions

Authorize the Azure Monitor Logs API connection if prompted:

1. Open the Azure Monitor Logs API connection.
2. Select **Edit API connection**.
3. Select **Authorize**, sign in, and then save the connection.

The Logs Ingestion API uses the playbook's managed identity. No Azure Log Analytics Data Collector connection or workspace key is required.