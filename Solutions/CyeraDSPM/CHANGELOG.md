# Changelog - CyeraDSPM Microsoft Sentinel Solution

All notable changes to this project will be documented in this file.

## [3.0.0] - 2026-03-06

### Removed
- **Azure Functions Connector**: Completely removed legacy Azure Functions-based data connector
  - Deleted `Data Connectors/CyeraDSPM_Functions/` directory and all contents
  - Removed FunctionAppDC.json connector definition
  - Removed manual deployment documentation (INSTALL.md)
  - Removed install-pack-v0_7_3.zip
  - Removed all Azure Function Python code

### Changed
- **Solution Architecture**: Simplified to single Codeless Connector Framework (CCF) connector only
  - Updated `Data/Solution_Cyera.json` to reference only CCF connector
  - Changed "Data Connectors: 2" to "Data Connectors: 1" in all documentation
  - Updated createUiDefinition.json to show single connector in deployment UI
  - Maintained all functionality - CCF connector provides same data ingestion via REST API

### Fixed
- **Deployment URLs**: Fixed broken template variable references in deployment instructions
  - Replaced `{{userguide-url}}` with working GitHub URL
  - Replaced `{{deployment-script-zip-url}}` with working raw GitHub URL
  - Fixed broken "Deploy to Azure" button syntax (removed unsupported ARM template option)
  - Updated install pack version reference from v0_7_0 to v0_7_3

### Technical Details
- **Files Modified**:
  - `Data/Solution_Cyera.json` - Removed Functions connector reference
  - `Package/mainTemplate.json` - Regenerated with single connector
  - `Package/createUiDefinition.json` - Updated to show 1 connector
- **Files Deleted**:
  - Entire `Data Connectors/CyeraDSPM_Functions/` directory
- **Impact**: Simplified deployment, eliminated manual Function App setup, aligned with Microsoft's recommended CCF approach
- **Migration**: Existing users can continue using CCF connector - no functionality loss

### Rationale
- Microsoft marketplace requirements: ARM template must exist for all deployment options or option must be removed
- CCF connector already provides all functionality via automated REST API polling
- Reduces maintenance burden and deployment complexity
- Aligns with Microsoft's recommended "Direct ingestion" approach for Sentinel solutions

## [3.0.0_RC2] - 2026-02-27

### Changed
- **Marketplace Offer ID**: Updated from `azure-sentinel-solution-cyeradspm` to `azure-sentinel-solution-cyeradspm-v3`
  - Ensures unique marketplace listing for v3.x releases
  - Distinguishes from legacy Azure Functions connector
- **First Publish Date**: Updated to reflect v3.0.4 as new major version

### Fixed
- **ASIM Schema Compliance**: Fixed DCR transformation KQL to use only supported functions
  - Removed `coalesce()` function (not supported in DCR transformations) → replaced with `iif()` pattern
  - Removed `todynamic()` function (not supported in DCR transformations) → use native dynamic fields directly
  - Removed `mv_apply` operator (not supported in DCR transformations) → simplified AssetOwner field handling
  - Fixed undefined variable reference: replaced `ownersArr` with `datastoreOwners`

### Changed
- **CyeraAssets_MS_CL Table**: All 18 ASIM fields now properly populated:
  - AssetId (string)
  - AssetName (string)
  - AssetSource (string)
  - CreatedDateTime (datetime)
  - LastModifiedDateTime (datetime)
  - ClassificationLastScanDateTime (datetime)
  - Workload (string)
  - SubWorkload (string)
  - Location (string)
  - Risks (string)
  - SensitivityLabel (string)
  - AssetOwner (dynamic array)
  - Provider (string = "Cyera")
  - AdditionalFields (dynamic object with 9 nested fields)
  - AADTenantID (string)
  - IsAssetRemoved (bool)
  - FeedType (string = "Changefeed")
  - TimeGenerated (datetime)

### Technical Details
- **File Modified**: `Data Connectors/CyeraDSPM_CCF/CyeraDSPM_DCR.json`
- **Affected Component**: Data Collection Rule transformation query for Custom-CyeraAssets_MS_CL stream
- **Impact**: DCR deployment now succeeds without InvalidTransformQuery errors
- **Validation**: Deployed and tested successfully with data flowing to all 5 custom tables

### Testing
- Deployed to Azure test environment
- Verified all ASIM fields present with correct data types
- Confirmed no DCR transformation errors
- Validated data ingestion for all 5 streams:
  - CyeraAssets_MS_CL ✓
  - CyeraDataStores_CL ✓
  - CyeraLabels_CL ✓
  - CyeraClassifications_CL ✓
  - CyeraUsers_CL ✓

## [3.0.0_RC1] - 2025-10-29

### Added
- Initial Creation of Codeless Connector Platform (CCP) connector
- Azure Functions connector for legacy support
- Support for 5 data streams from Cyera API
- RestApiPoller-based data ingestion
- JWT token authentication
- Custom table schemas for all data types
