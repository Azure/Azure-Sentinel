| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------------------------------|
| 3.1.1       | 23-04-2026                     | Fixed CCF connector deploy-time failures. Switched paging configuration to `Offset` type to match the IONIX API's standard DRF pagination. Removed upfront `CyberpionActionItems_CL` table schema declaration so the connector can deploy successfully into workspaces that still have the table from the legacy push connector — the table is now created (greenfield) or extended (migrating) automatically by the Data Collection Rule on first write. |
| 3.1.0       | 16-02-2026                     | Added new CCF RestApiPoller data connector (recommended). Automatic daily polling from IONIX API. Old push connector marked as deprecated - will be removed June 2026. Updated workbook and analytics rule with id_s deduplication. |
| 3.0.0       | 20-09-2023                     | A UI-only update as part of a re-branding from "Cyberpion" to "IONIX" (no change to core functionality) \| v1.0.1 | 
         
                                                                                                                 
