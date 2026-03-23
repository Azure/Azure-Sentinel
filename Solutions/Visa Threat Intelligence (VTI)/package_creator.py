import json, copy

# Load both files
with open('Package/mainTemplate.json') as f:
    main = json.load(f)

with open('DataConnectors/VisaThreatIntelligenceConnector.json') as f:
    dc = json.load(f)

# Add data connector variables (with corrected versions)
main['variables'].update({
    "dataConnectorVersionConnectorDefinition": "1.0.0",
    "dataConnectorVersionConnections": "1.0.0",
    "_dataConnectorContentIdConnectorDefinition": "VisaThreatIntelligenceConnectorTemplateConnectorDefinition",
    "dataConnectorTemplateNameConnectorDefinition": "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentIdConnectorDefinition')))]",
    "_dataConnectorContentIdConnections": "VisaThreatIntelligenceConnectorTemplateConnections",
    "dataConnectorTemplateNameConnections": "[concat(parameters('workspace'),'-dc-',uniquestring(variables('_dataConnectorContentIdConnections')))]",
    "_logAnalyticsTableId1": "VisaThreatIntelligenceIOC_CL",
    "_solutionAuthor": "Microsoft",
    "_solutionTier": "Microsoft"
})

# Extract DC resources 0-3 (skip resource 4 which is the separate contentPackage)
dc_resources = [copy.deepcopy(dc['resources'][i]) for i in range(4)]

# Insert DC resources before the contentPackage (last resource)
content_package = main['resources'].pop()
main['resources'].extend(dc_resources)
main['resources'].append(content_package)

# Add DataConnector dependency to contentPackage
content_package['properties']['dependencies']['criteria'].append({
    "kind": "DataConnector",
    "contentId": "[variables('_dataConnectorContentIdConnectorDefinition')]",
    "version": "[variables('dataConnectorVersionConnectorDefinition')]"
})

# Update description to include data connector count
content_package['properties']['descriptionHtml'] = content_package['properties']['descriptionHtml'].replace(
    "<strong>Workbooks:</strong> 1, <strong>Analytic Rules:</strong> 2",
    "<strong>Data Connectors:</strong> 1, <strong>Workbooks:</strong> 1, <strong>Analytic Rules:</strong> 2"
)

# Write merged template
with open('Package/mainTemplate.json', 'w') as f:
    json.dump(main, f, indent=2)
    f.write('\n')

print("Done - merged data connector into mainTemplate.json")
