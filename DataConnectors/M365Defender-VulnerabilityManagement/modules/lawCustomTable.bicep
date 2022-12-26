param lawName string
param tableName string
param plan string
param columns array
param retention int = -1

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: lawName
}

resource table 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = {
  parent: logAnalyticsWorkspace
  name: tableName
  properties: {
    schema: {
      name: tableName
      columns: columns
    }
    plan: plan
    retentionInDays: retention != -1 ? retention : ''
  }
}
