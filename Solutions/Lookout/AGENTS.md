# Azure Sentinel - Lookout Solution - Agent Guide

## Validation & Testing
- **Run KQL validation**: `dotnet test .script/tests/KqlvalidationsTests/Kqlvalidations.Tests.csproj --filter "FullyQualifiedName~Lookout" --configuration Release`
- **Run template schema validation**: `dotnet test .script/tests/detectionTemplateSchemaValidation/DetectionTemplateSchemaValidation.Tests.csproj --filter "FullyQualifiedName~Lookout" --configuration Release`
- **Version check**: `bash .script/checkThatTemplatesVersionWasChanged.sh` (checks all modified detection rules)
- **Package solution**: `pwsh Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1 -solutionName 'Lookout'`

## Architecture
- **Solutions/Lookout/**: Main solution folder with Analytic Rules, Data Connectors, Parsers, Workbooks, Hunting Queries
- **Package/**: Contains versioned .zip files (mainTemplate.json + createUiDefinition.json) for deployment
- **Parser**: `LookoutEvents.yaml` - transforms `LookoutMtdV2_CL` raw table into normalized fields
- **.script/tests/**: All CI/CD validation tests (KQL, schema, connectors, versions)

## Code Style & Conventions
- **Analytic rules**: Must have `version`, `entityMappings`, `requiredDataConnectors` with valid `connectorId` (check `.script/tests/detectionTemplateSchemaValidation/ValidConnectorIds.json`)
- **Queries**: Use parser function (`LookoutEvents`) NOT raw tables (`LookoutMtdV2_CL`) in analytic rules
- **Versions**: Increment version in YAML whenever modifying a detection rule (required for PR validation)
- **Connector IDs**: Use `LookoutAPI` for Lookout solution (must match ValidConnectorIds.json)
- **Parser columns**: Avoid duplicate field names in `extend` and `project` statements
- **Solution versioning**: Update `Data/Solution_Lookout.json`, `SolutionMetadata.json`, and `ReleaseNotes.md` together
- **Package updates**: Regenerate `Package/X.X.X.zip` after template changes using packaging tool or manual zip of mainTemplate.json + createUiDefinition.json
