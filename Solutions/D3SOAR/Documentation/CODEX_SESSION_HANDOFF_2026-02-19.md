# D3SOAR Sentinel Packaging Handoff (2026-02-19)

## Scope Completed
This session moved D3SOAR from manual package editing to V3 packaging-tool driven generation using CCF connector files.

## Environment Notes
- Repo: `C:\projects\Azure-Sentinel`
- Packaging tool: `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1`
- PowerShell 7 required for V3 in this repo (`?:` syntax in common scripts).
- Installed/used pwsh path: `C:\Program Files\PowerShell\7\pwsh.exe`
- `pwsh` may not be on PATH in Windows PowerShell 5.1 shell; invoke with full path if needed.

## User-Provided D3 API Contract (Implemented)
- Endpoint example: `https://poc.bemimo.com/ce_site/VSOC/api/command/GetIncidentsWithNewParameters`
- Method: `POST`
- Auth header: `d3jwt: <token>`
- Request body structure uses:
  - `Username`, `Site`, `Timestamp`
  - `CommandParams` with filter, static fields, dynamic fields, time range, paging
- Response events path: `rawData.incidents[]`

## Files Created/Updated
### CCF source files
- `Solutions/D3SOAR/Data Connectors/D3SOAR_CCF/D3SOAR_DataConnectorDefinition.json`
- `Solutions/D3SOAR/Data Connectors/D3SOAR_CCF/D3SOAR_PollingConfig.json`
- `Solutions/D3SOAR/Data Connectors/D3SOAR_CCF/D3SOAR_DCR.json`
- `Solutions/D3SOAR/Data Connectors/D3SOAR_CCF/D3SOAR_Table.json`

### Solution metadata/input
- `Solutions/D3SOAR/Data/Solution_D3SOAR.json`
- `Solutions/D3SOAR/SolutionMetadata.json`

### Generated package artifacts
- `Solutions/D3SOAR/Package/createUiDefinition.json`
- `Solutions/D3SOAR/Package/mainTemplate.json`
- `Solutions/D3SOAR/Package/testParameters.json`
- `Solutions/D3SOAR/Package/3.0.2.zip`
- `Solutions/D3SOAR/Package/3.0.3.zip`
- `Solutions/D3SOAR/Package/3.0.4.zip`
- `Solutions/D3SOAR/Package/3.0.5.zip`

## Current Connector Design
- Target custom table: `D3SOARIncidents_CL`
- Poller:
  - REST API poller
  - POST to D3 endpoint
  - API key auth with header name `d3jwt`
  - events path: `$.rawData.incidents[*]`
- DCR:
  - Stream: `Custom-D3SOARIncidents`
  - Transform maps D3 incident fields to normalized columns (`IncidentNumber`, `IncidentSeverity`, etc.)
  - `RawRecord` kept as `dynamic`
- Table schema aligned to transform output columns.

## Important Adjustments Made
- Removed blank array field from poller payload template (`Incident Numbers: []`) to pass `Template Should Not Contain Blanks`.
- Switched DCR `dataCollectionEndpointId` in source to placeholder style:
  - `"dataCollectionEndpointId": "{{dataCollectionEndpointId}}"`

## Latest Packaging Command (working)
Run from:
`C:\projects\Azure-Sentinel\Tools\Create-Azure-Sentinel-Solution\V3`

```powershell
& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -File '.\createSolutionV3.ps1' -SolutionDataFolderPath 'C:\projects\Azure-Sentinel\Solutions\D3SOAR\Data' -VersionMode local -VersionBump patch
```

## Current Status
- Packaging succeeds.
- Package JSON files are valid.
- arm-ttk result at end of session: **48/49 pass**, **1 failure remains**:
  - `IDs Should Be Derived From ResourceIDs`

## Remaining Known Issue
`IDs Should Be Derived From ResourceIDs` appears tied to tool-generated CCF/content package id expressions and CCF metadata/id conventions (`contentProductId`, `id`, `dataCollectionRuleImmutableId` patterns in generated template). This remained after source-side hardening and regeneration.

## Recommended Next Steps
1. Decide if 48/49 is acceptable for current dev/test milestone.
2. If strict pass is required, inspect and patch generated `Package/mainTemplate.json` post-generation (or update shared packaging/common scripts) for ID expression compliance.
3. Optional cleanup:
   - Keep only latest zip (`3.0.5.zip`) and remove old package zips.
4. Optional metadata cleanup:
   - Add `version` to `Solutions/D3SOAR/SolutionMetadata.json` to remove tool warning about metadata version update.

## Fast Restart Checklist (next session)
1. Verify CCF source files still match desired API contract.
2. Re-run packaging command above with PowerShell 7.
3. Review generated package diff.
4. Re-check arm-ttk result and decide whether to accept or patch remaining ID rule.

