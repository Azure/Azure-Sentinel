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

---

## v1.0.1 (2026-02-17)

### Patch — ARM Template Fixes

**Changes:**
- Fixed `location` parameter in inner template deployment (use `variables('workspace-location-inline')`)
- Fixed `workspace` parameter reference in inner template (use `variables('workspace-name')`)
- Corrected metadata name bracket formatting (single `[` instead of double `[[`)
- Added missing `hidden-SentinelTemplateName` and `hidden-SentinelTemplateVersion` tags on Logic App resource

---

## v1.0.0 (2026-02-17)

### Initial Release

**What it does:**
- Polls Cyren CCF (Common Connector Framework) threat intelligence feed every 6 hours
- Transforms Cyren IP reputation data into STIX-formatted threat indicators
- Pushes indicators to Microsoft Sentinel's `ThreatIntelligenceIndicator` table via the Sentinel TI `createIndicator` API
- Uses Logic App managed identity for both Sentinel API and blob storage access (no credentials stored)
- Persists the Cyren `PersistentToken` in Azure Blob Storage for efficient delta polling

**Resources deployed:**
| Resource | Type | Purpose |
|----------|------|---------|
| Storage Account | `Microsoft.Storage/storageAccounts` | PersistentToken blob storage |
| Blob Container | `cyren-state` | Stores `persistent-token-{feedId}.txt` |
| Logic App | `Microsoft.Logic/workflows` | Polls Cyren → pushes to Sentinel TI |
| Role Assignment | Sentinel Contributor | Logic App MI → workspace |
| Role Assignment | Storage Blob Data Contributor | Logic App MI → storage account |

**Cost safety parameters (ENFORCED):**
- `count`: 1000 (max records per CCF API call)
- `queryWindowInMin`: 360 (last 6 hours only)
- Pagination: `PersistentToken` (NOT Offset — avoids 99.99% duplicates)
- Logic App recurrence: Every 6 hours
- Until loop limit: 5 iterations per run (max 5,000 indicators/run)

**Supported feeds:**
- `ip_reputation` (default)
- `malware_urls`
- `phishing_urls`

**Post-deployment checklist:**
1. ✅ Verify Logic App recurrence = 6 hours
2. ✅ Verify count=1000 and queryWindowInMin=360
3. ✅ Verify PersistentToken pagination
4. ✅ Check RBAC role assignments
5. ✅ Enable the Logic App (deploys Disabled)
6. ✅ Run one manual trigger
7. ✅ Monitor run history for 24 hours

---

**Known limitations:**
- Logic App deploys in **Disabled** state — must be manually enabled after verification
- First run may take longer as it fetches the full 6-hour query window without a prior PersistentToken
- Sentinel TI `createIndicator` API processes one indicator at a time (future: batch upload)
- Rate limiting: For_Each concurrency set to 5 to avoid Sentinel API throttling
