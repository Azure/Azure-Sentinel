param workspaceResourceId string
param location string

var api = '2023-09-01'

var assetsMsSchema = loadTextContent('../../artifacts/tables/table.assets_ms.schema.json')
var assetsExtSchema = loadTextContent('../../artifacts/tables/table.assets_ext.schema.json')
var identitiesSchema = loadTextContent('../../artifacts/tables/table.CyeraIdentities_CL.schema.json')
var classificationsSchema = loadTextContent('../../artifacts/tables/table.CyeraClassifications_CL.schema.json')
var issuesSchema = loadTextContent('../../artifacts/tables/table.CyeraIssues_CL.schema.json')

resource createTables 'Microsoft.Resources/deploymentScripts@2022-08-01' = {
  name: 'create-law-tables'
  location: location
  kind: 'AzureCLI'
  identity: { type: 'SystemAssigned' }
  properties: {
    azCliVersion: '2.63.0'
    timeout: 'PT30M'
    retentionInterval: 'P1D'
    environmentVariables: [
      { name: 'WS_ID', value: workspaceResourceId },
      { name: 'API', value: api },
      { name: 'JSON_ASSETS_MS', value: assetsMsSchema },
      { name: 'JSON_ASSETS_EXT', value: assetsExtSchema },
      { name: 'JSON_IDENTITIES', value: identitiesSchema },
      { name: 'JSON_CLASSIFICATIONS', value: classificationsSchema },
      { name: 'JSON_ISSUES', value: issuesSchema }
    ]
    scriptContent: '''
set -euo pipefail
echo "$JSON_ASSETS_MS" > table.assets_ms.schema.json
echo "$JSON_ASSETS_EXT" > table.assets_ext.schema.json
echo "$JSON_IDENTITIES" > table.identities.schema.json
echo "$JSON_CLASSIFICATIONS" > table.classifications.schema.json
echo "$JSON_ISSUES" > table.issues.schema.json

create_table () {
  local name=$1; local file=$2
  echo "Creating table $name"
  az rest --method PUT --only-show-errors     --url "https://management.azure.com${WS_ID}/tables/${name}?api-version=${API}"     --body @"$file"
}

create_table "CyeraAssets_MS_CL" table.assets_ms.schema.json
create_table "CyeraAssets_CL" table.assets_ext.schema.json
create_table "CyeraIdentities_CL" table.identities.schema.json
create_table "CyeraClassifications_CL" table.classifications.schema.json
create_table "CyeraIssues_CL" table.issues.schema.json

echo "Tables created."
'''
  }
}

output scriptName string = createTables.name
