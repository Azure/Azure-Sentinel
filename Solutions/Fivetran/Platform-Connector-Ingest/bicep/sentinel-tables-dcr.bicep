// Fivetran Platform Connector -> Sentinel ingest: Sentinel-side infrastructure as code.
//
// Deploys the Sentinel side of the ADLS -> Function -> Logs Ingestion API -> Sentinel
// pipeline for the Fivetran Platform Connector tables:
//   1. typed custom table    Fivetran_AuditTrail_CL   (security AUDIT_TRAIL events)
//   2. generic custom table  Fivetran_Platform_CL     ({FivetranTable, Record dynamic})
//      for the other 11 reference/metadata tables (user, team, role, connection, ...)
//   3. Data Collection Rule (kind: Direct) with one stream per table + transforms.
//   4. (optional) Monitoring Metrics Publisher on the DCR for the ingest function's
//      managed identity, when its principalId is supplied. With a user-assigned managed
//      identity you can supply this up front, so the role is in place before first run
//      (no chicken-and-egg with a system-assigned identity created after the DCR).
//
// The Flex Consumption function app, its user-assigned managed identity, the Event Grid
// system topic + subscription, and the Storage Blob Data Reader grant are in
// DEPLOYMENT-GUIDE.md (CLI) because the storage account typically lives in a different
// resource group / subscription owned by the data platform team.
//
// api-versions: dataCollectionRules 2024-03-11 (exposes properties.endpoints.logsIngestion),
//               workspaces/tables 2022-10-01, roleAssignments 2022-04-01.
//
// Compile:  az bicep build -f sentinel-tables-dcr.bicep
// Deploy:   az deployment group create -g <sentinel-rg> -f sentinel-tables-dcr.bicep \
//             -p workspaceName=<workspace-name> functionPrincipalId=<uami-principal-id>

targetScope = 'resourceGroup'

@description('Azure region. Must match the Log Analytics workspace region.')
param location string = resourceGroup().location

@description('Name of the EXISTING Log Analytics workspace with Sentinel enabled.')
param workspaceName string

@description('Data Collection Rule name.')
param dcrName string = 'dcr-fivetran-platform'

@description('Interactive (Analytics) retention in days for the audit table. 30-730.')
@minValue(30)
@maxValue(730)
param auditRetentionInDays int = 365

@description('Total retention in days (interactive + archive) for the audit table. 30-2556.')
@minValue(30)
@maxValue(2556)
param auditTotalRetentionInDays int = 730

@description('Interactive (Analytics) retention in days for the reference table. 30-730. Reference/dimension data changes rarely, so a shorter interactive window is usually enough while keeping the Analytics plan so it can be joined for enrichment.')
@minValue(30)
@maxValue(730)
param referenceRetentionInDays int = 90

@description('Optional: object (principal) id of the ingest function\'s managed identity. When set, grants it Monitoring Metrics Publisher on the DCR. Prefer a user-assigned managed identity so this is known before deploy.')
param functionPrincipalId string = ''

var auditTable = 'Fivetran_AuditTrail_CL'
var platformTable = 'Fivetran_Platform_CL'
var auditStream = 'Custom-${auditTable}'
var platformStream = 'Custom-${platformTable}'
// Built-in role: Monitoring Metrics Publisher
var monitoringMetricsPublisherRoleId = '3913510d-42f4-4e42-8a64-420c390055eb'

resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: workspaceName
}

resource auditTableRes 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = {
  parent: workspace
  name: auditTable
  properties: {
    plan: 'Analytics'
    retentionInDays: auditRetentionInDays
    totalRetentionInDays: auditTotalRetentionInDays
    schema: {
      name: auditTable
      description: 'Fivetran Platform Connector AUDIT_TRAIL events, ingested from the Managed Data Lake parquet via the Logs Ingestion API.'
      columns: [
        { name: 'TimeGenerated', type: 'dateTime', description: 'Ingestion timestamp, derived from captured_at in the DCR transform.' }
        { name: 'id', type: 'string', description: 'Immutable AUDIT_TRAIL row id (primary key; used for dedupe).' }
        { name: 'captured_at', type: 'dateTime', description: 'When the audited action occurred.' }
        { name: 'user_id', type: 'string', description: 'Fivetran user id that performed the action (actor).' }
        { name: 'action', type: 'string', description: 'The action performed (operation).' }
        { name: 'interaction_method', type: 'string', description: 'How the action was performed (UI, API, terraform, ...).' }
        { name: 'primary_resource_type', type: 'string', description: 'Type of the primary object acted on.' }
        { name: 'primary_resource_id', type: 'string', description: 'Id of the primary object acted on.' }
        { name: 'secondary_resource_type', type: 'string', description: 'Type of the secondary object.' }
        { name: 'secondary_resource_id', type: 'string', description: 'Id of the secondary object.' }
        { name: 'old_values', type: 'dynamic', description: 'Prior values (JSON), parsed in the DCR transform.' }
        { name: 'new_values', type: 'dynamic', description: 'New values (JSON), parsed in the DCR transform.' }
      ]
    }
  }
}

resource platformTableRes 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = {
  parent: workspace
  name: platformTable
  properties: {
    // Analytics (not Basic/Auxiliary): these reference tables are used to JOIN/enrich
    // audit and other events. Basic and Auxiliary plans restrict cross-table joins, so
    // keep Analytics here and control cost with a shorter interactive retention instead.
    plan: 'Analytics'
    retentionInDays: referenceRetentionInDays
    totalRetentionInDays: referenceRetentionInDays
    schema: {
      name: platformTable
      description: 'Fivetran Platform Connector reference/metadata tables (user, team, role, connection, destination, account, ...) as a generic envelope; full row in Record.'
      columns: [
        { name: 'TimeGenerated', type: 'dateTime', description: 'Ingestion timestamp (now() in the DCR transform).' }
        { name: 'FivetranTable', type: 'string', description: 'Source Fivetran table name (e.g. user, role, connection).' }
        { name: 'Record', type: 'dynamic', description: 'Full source row as JSON, parsed in the DCR transform.' }
      ]
    }
  }
}

resource dcr 'Microsoft.Insights/dataCollectionRules@2024-03-11' = {
  name: dcrName
  location: location
  kind: 'Direct'
  properties: {
    streamDeclarations: {
      '${auditStream}': {
        columns: [
          { name: 'id', type: 'string' }
          { name: 'captured_at', type: 'datetime' }
          { name: 'user_id', type: 'string' }
          { name: 'action', type: 'string' }
          { name: 'interaction_method', type: 'string' }
          { name: 'primary_resource_type', type: 'string' }
          { name: 'primary_resource_id', type: 'string' }
          { name: 'secondary_resource_type', type: 'string' }
          { name: 'secondary_resource_id', type: 'string' }
          { name: 'old_values', type: 'string' }
          { name: 'new_values', type: 'string' }
        ]
      }
      '${platformStream}': {
        columns: [
          { name: 'FivetranTable', type: 'string' }
          { name: 'Record', type: 'string' }
        ]
      }
    }
    destinations: {
      logAnalytics: [
        {
          workspaceResourceId: workspace.id
          name: 'sentinelWorkspace'
        }
      ]
    }
    dataFlows: [
      {
        streams: [ auditStream ]
        destinations: [ 'sentinelWorkspace' ]
        transformKql: 'source | extend TimeGenerated = captured_at | extend old_values = parse_json(old_values), new_values = parse_json(new_values)'
        outputStream: auditStream
      }
      {
        streams: [ platformStream ]
        destinations: [ 'sentinelWorkspace' ]
        transformKql: 'source | extend TimeGenerated = now() | extend Record = parse_json(Record)'
        outputStream: platformStream
      }
    ]
  }
  dependsOn: [
    auditTableRes
    platformTableRes
  ]
}

resource dcrRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionPrincipalId)) {
  name: guid(dcr.id, functionPrincipalId, monitoringMetricsPublisherRoleId)
  scope: dcr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', monitoringMetricsPublisherRoleId)
    principalId: functionPrincipalId
    principalType: 'ServicePrincipal'
  }
}

@description('Paste into the function app setting DCR_RULE_ID.')
output dcrImmutableId string = dcr.properties.immutableId

@description('Paste into the function app setting DCR_ENDPOINT.')
output logsIngestionEndpoint string = dcr.properties.endpoints.logsIngestion

output auditStream string = auditStream
output platformStream string = platformStream
