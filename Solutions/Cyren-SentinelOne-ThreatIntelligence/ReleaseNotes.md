# Cyren-SentinelOne Threat Intelligence - Release Notes

## Version 1.0.0 (2026-02-17)

### Initial Release

**Solution Overview:**
Polls Cyren CCF threat intelligence feeds and pushes IOCs to SentinelOne's Threat Intelligence API for automated detection and response.

**Features:**
- **Cyren CCF Polling:** Polls the Cyren CCF API every 6 hours using PersistentToken-based pagination (no duplicates, no Offset)
- **SentinelOne IOC Push:** Transforms Cyren IP reputation indicators to SentinelOne IOC format and pushes via the Threat Intelligence API
- **STAR Rule Auto-Creation:** Automatically creates a SentinelOne STAR detection rule for Cyren indicators on first run
- **Cost Safety:** Pre-configured with `count=1000` and `queryWindowInMin=360` to prevent excessive API usage
- **Content Hub Ready:** Packaged as a Microsoft Sentinel Solution with Content Hub support

**Playbook: pb-cyren-to-sentinelone**
- Recurrence: Every 6 hours (360 minutes)
- Cyren API: `https://api-feeds.cyren.com/v1/feed/data`
- Default Feed: `ip_reputation`
- Pagination: PersistentToken (max 10 pages per run)
- SentinelOne API: `/web/api/v2.1/threat-intelligence/iocs`
- IOC Type: IPV4
- IOC Validity: 90 days

**Cost Safety Parameters (DO NOT MODIFY):**
| Parameter | Value | Reason |
|-----------|-------|--------|
| count | 1000 | Max records per API call |
| queryWindowInMin | 360 | Only last 6 hours of data |
| Recurrence | 6 hours | Minimum polling interval |
| Pagination | PersistentToken | Prevents duplicates (NOT Offset) |
| Max Pages | 10 | Cap at 10,000 records per run |

**Parameters Required:**
- `Cyren_JwtToken` - Cyren CCF JWT Bearer token
- `Cyren_FeedId` - Feed ID (default: `ip_reputation`)
- `SentinelOne_ApiToken` - SentinelOne API token
- `SentinelOne_BaseUrl` - SentinelOne console URL
- `SentinelOne_AccountId` - SentinelOne account ID

**Known Limitations:**
- Currently supports IPV4 indicator type only (IPv6 support planned)
- Per-record POST to SentinelOne (batch optimization planned for v1.1)
- No automatic retry for SentinelOne rate limiting (uses Logic App default retry)
