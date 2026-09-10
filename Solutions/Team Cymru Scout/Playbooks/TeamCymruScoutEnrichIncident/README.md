# Team Cymru Scout Enrich Incident

## Summary

This playbook will fetch and ingest IP or Domain Indicator data based on Entity mapped in Microsoft Sentinel Incident and notify to pre-defined or user customizable email id.
### Prerequisites

1. User should have an outlook mail account in order to use this playbook.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
  * PlaybookName: Enter the playbook name here.
  * UserName: Enter username of your Team Cymru Scout account.
  * Password: Enter password of your Team Cymru Scout account.
  * BaseURL: Enter Base URL of your Team Cymru Scout account.
  * EmailId: Enter valid comma separated email ID(s) of receiver without space. (e.g. person1@gmail.com,person2@gmail.com)
  * WorkspaceName: Enter the log analytics workspace name in which data will be stored for incident enrichment.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTeam%20Cymru%20Scout%2FPlaybooks%2FTeamCymruScoutEnrichIncident%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTeam%20Cymru%20Scout%2FPlaybooks%2FTeamCymruScoutEnrichIncident%2Fazuredeploy.json)

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

- `Insights_Data_Incident_Based_CL`
- `Investigated_IPs_Incident_Based_CL`
- `Summary_Details_Top_Fingerprints_Data_Incident_Based_CL`
- `Summary_Details_Top_Open_Ports_Data_Incident_Based_CL`
- `Summary_Details_Top_Pdns_Data_Incident_Based_CL`
- `Whois_Data_Incident_Based_CL`

Column names and types are unchanged, so existing parsers, workbooks and saved queries keep working.

#### b. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select a connection resource
2. Go to General → Edit API connection.
3. Click Authorize
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

#### c. Assign Role to add a comment in the incident

After authorizing each connection, assign a role to this playbook.
1. Go to Log Analytics Workspace → *your workspace* → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles
4. Role: Microsoft Sentinel Contributor
5. Members: select managed identity for "assigned access to" and add your logic app as a member.
6. Click on review+assign
