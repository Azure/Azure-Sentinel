# Copy Log Analytics Workspace tables
## Author: @TheAlistairRoss

This PowerShell script, `Copy-AzOperationsInsightsTable`, is designed to facilitate the copying of tables schema and creating a custom log copy. This is useful when splitting data via data collection rules, but ensuring the same schema output.

## Prerequisites

Before using this script, ensure that you have the following:

- Permissions to read and write tables to a Log Analytics workspace. Miniumum built in roles that acheive this are.
    - Log Analytics Contributor, 
    - Monitoring Contributor
    - Sentinel Contributor
- PowerShell Modules
    - Az.Accounts
    - Az.Resources
    - Az.OperationalInsights

## Usage

1. Open a PowerShell session.
2. Load the function into your environment
3. Run the function based on one of the following examples.

### Example 1: Copy the table schema and use the same name
This method will copy the Syslog table schema create a custom table called **Syslog_CL** with the Basic plan type in the same workspace
```powershell
Copy-AzOperationalInsightsTable `
    -WorkspaceResourceId "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/myWorkspace"  `
    -SourceTableName "Syslog"
```
### Example 2: Copy the table schema and use the different name, and set the plan type to Analytics
This method will copy the Syslog table schema create a custom table called **Syslog_Testing_CL** with the Analytics plan type in the same workspace
```powershell
Copy-AzOperationalInsightsTable `
    -WorkspaceResourceId "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/myWorkspace"  `
    -SourceTableName "Syslog" `
    -TargetTableName "Syslog_Testing_CL" `
    -TablePlan Analytics
```


- This script currently supports copying tables within the same workspace only.
- The script does not handle schema changes, retention, data transformations or copy data from one table to another during the copy process.

