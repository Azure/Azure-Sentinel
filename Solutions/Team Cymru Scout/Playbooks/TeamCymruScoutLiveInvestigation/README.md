# Team Cymru Scout Live Investigation

## Summary

This playbook will fetch and ingest IP or Domain Indicator data based on input parameters given in the live investigation dashboard.

### Prerequisites

1. Make sure that the TeamCymruScoutCreateIncidentAndNotify playbook is deployed before deploying the TeamCymruScoutLiveInvestigation playbook.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
  * PlaybookName: Please do not change the playbook name, else you will not get any data for the live investigation dashboard.
  * UserName: Enter username of your Team Cymru Scout account.
  * Password: Enter password of your Team Cymru Scout account.
  * BaseURL: Enter Base URL of your Team Cymru Scout account.
  * WorkspaceName: Enter workspace name in which you want to fetch or store your data.
  * CreateIncidentAndNotifyPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTeam%20Cymru%20Scout%2FPlaybooks%2FTeamCymruScoutLiveInvestigation%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTeam%20Cymru%20Scout%2FPlaybooks%2FTeamCymruScoutLiveInvestigation%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Log ingestion

This playbook writes to Log Analytics through the [Logs Ingestion API](https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview) using its own system-assigned managed identity. The data collection endpoint, the data collection rule, the destination tables and the **Monitoring Metrics Publisher** role assignment are all created by the deployment template, so ingestion needs no manual authorization.

**Existing workspaces only.** If you deployed an earlier version of this playbook, its tables were created by the retired HTTP Data Collector API and are *classic* tables. Convert them once per workspace before the first run of the migrated playbook, otherwise ingestion fails:

```bash
resourceGroup="<resource-group>"
workspace="<workspace-name>"

# List the classic tables still present in the workspace
az monitor log-analytics workspace table list \
  --resource-group "$resourceGroup" --workspace-name "$workspace" \
  --query "[?schema.tableSubType=='Classic'].{Name:name}" -o table

# Convert each one
az monitor log-analytics workspace table migrate \
  --resource-group "$resourceGroup" --workspace-name "$workspace" \
  --table-name "<TableName>_CL"
```

> **The conversion cannot be undone.** It is a one-way operation per table.

This playbook writes the following tables:

- `Communication_Data_CL`
- `Domain_Data_CL`
- `Fingerprints_Data_CL`
- `Identity_Data_CL`
- `Insights_Data_CL`
- `Live_Investigation_Domain_Indicators_CL`
- `Live_Investigation_IP_Indicators_CL`
- `Open_Ports_Data_CL`
- `PDNS_Data_CL`
- `Proto_By_IP_Data_CL`
- `Summary_Details_CL`
- `Summary_Details_Top_Certs_Data_CL`
- `Summary_Details_Top_Fingerprints_Data_CL`
- `Summary_Details_Top_Open_Ports_Data_CL`
- `Summary_Details_Top_Pdns_Data_CL`
- `Top_Asns_By_IP_Data_CL`
- `Top_Country_Codes_By_IP_Data_CL`
- `Top_Services_By_IP_Data_CL`
- `Top_Tags_By_IP_Data_CL`
- `Whois_Data_CL`
- `X509_Data_CL`

Column names and types are unchanged, so existing parsers, workbooks and saved queries keep working.

#### b. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select a connection resource
2. Go to General → Edit API connection.
3. Click Authorize
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.
