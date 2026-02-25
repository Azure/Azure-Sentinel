# Cyren Defender Threat Intelligence — Release Notes

## v3.0.0 (2026-02-23)

### Major Release — Production-Ready Packaging

**Changes:**
- Repackaged solution as v3.0.0 for Microsoft Sentinel Content Hub submission
- Upgraded `contentSchemaVersion` to 3.0.0 for compatibility with latest Sentinel solution schema
- Logic App template validated end-to-end: Cyren CCF feed → STIX indicators → Sentinel `ThreatIntelligenceIndicator` table
- NDJSON response parsing corrected: split by newline, filter empty lines, parse each line as individual JSON object
- `feedId` parameter corrected to camelCase (`feedId` not `feed_id`) per Cyren CCF API spec
- `PersistentToken` correctly extracted from last NDJSON response line and persisted to Azure Blob Storage
- `runAfter` dependency added for first-run scenario (no prior PersistentToken)
- Managed identity authentication: Logic App MI granted Sentinel Contributor + Storage Blob Data Contributor roles
- All resources use `[variables('workspace-location-inline')]` for location consistency
- Workspace parameter references updated to use `[variables('workspace-name')]`
- Hidden Sentinel tags (`hidden-SentinelTemplateName`, `hidden-SentinelTemplateVersion`, `hidden-SentinelWorkspaceId`) applied to Logic App resource for Content Hub visibility


