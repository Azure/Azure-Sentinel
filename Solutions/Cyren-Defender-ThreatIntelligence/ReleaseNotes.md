# Cyren Defender Threat Intelligence — Release Notes

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
