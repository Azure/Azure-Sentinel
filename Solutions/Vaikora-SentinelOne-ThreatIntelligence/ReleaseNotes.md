# Vaikora-SentinelOne Threat Intelligence - Release Notes

## Version 3.0.0 (2026-04-02)

### Initial Release

**Solution Overview:**
Polls the Vaikora AI Agent Security API every 6 hours for high-severity and anomaly agent actions, then pushes indicators of compromise (IOCs) to SentinelOne's Threat Intelligence API for automated detection and response.

**Features:**
- **Vaikora Action Polling:** Polls `/api/v1/actions` every 6 hours with `per_page=100` — no pagination token needed
- **Smart Filtering:** Only processes actions where `severity == High/Critical` or `is_anomaly == true`
- **SentinelOne IOC Push:** Maps Vaikora actions to SentinelOne IOC format (SHA256 type using `log_hash`) and pushes via the Threat Intelligence API
- **STAR Rule Auto-Creation:** Creates a SentinelOne STAR detection rule for Vaikora indicators on first run
- **Risk Score Severity Mapping:** Maps `risk_score` (0-100) to SentinelOne severity (2-7)
- **Content Hub Ready:** Packaged as a Microsoft Sentinel Solution with Content Hub support

**Playbook: pb-vaikora-to-sentinelone**
- Recurrence: Every 6 hours (UTC)
- Vaikora API: `https://api.vaikora.com/api/v1/actions`
- Auth: `X-API-Key` header
- Filter: `severity` in (High, Critical) OR `is_anomaly == true`
- SentinelOne API: `/web/api/v2.1/threat-intelligence/iocs`
- IOC Type: SHA256 (from `log_hash` field)
- IOC Validity: 90 days
- IOC Source: `Vaikora AI Agent Security (Data443)`

**Severity Mapping:**

| risk_score | SentinelOne severity |
|------------|---------------------|
| 0 - 30     | 2                   |
| 31 - 50    | 3                   |
| 51 - 70    | 4                   |
| 71 - 85    | 5                   |
| 86 - 95    | 6                   |
| 96 - 100   | 7                   |

**Parameters Required:**
- `VaikoraApiKey` - Vaikora API key (used as `X-API-Key` header)
- `VaikoraAgentId` - Vaikora Agent ID to poll
- `SentinelOne_ApiToken` - SentinelOne API token
- `SentinelOne_BaseUrl` - SentinelOne console URL
- `SentinelOne_AccountId` - SentinelOne account ID (required in all IOC push requests)

**Known Limitations:**
- Fetches up to 100 actions per run (`per_page=100`) — no cursor-based pagination
- IOC type fixed to SHA256 using `log_hash`; IP/URL extraction from action content not yet implemented
- Per-record POST to SentinelOne (batch optimization planned for v1.1)
- No automatic retry for SentinelOne rate limiting (uses Logic App default retry policy)
