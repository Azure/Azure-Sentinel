# Premium / Enterprise Tailscale endpoints

Endpoints that gave 403 or are explicitly Premium-tier features. These are NOT polled by the **Tailscale Standard (CCF)** connector. They should be added to **Tailscale Premium (CCF)** when validating that connector against a real Premium tailnet.

## Already in Premium connector

- `/logging/network` -> `Tailscale_Network_CL` - network flow logs (Premium feature; scope `logs:network:read`)

## Premium-only data sources to ADD to Premium connector

| Endpoint | Scope | Yields | Notes |
|---|---|---|---|
| `/posture/integrations` | `feature_settings:read` | List of MDM/EDR integrations (Jamf, Kandji, Intune, Kolide, Microsoft Defender for Endpoint, CrowdStrike Falcon, SentinelOne, etc.) configured for device posture enforcement | Endpoint returns 200 with empty list on Standard tier - only meaningful on Premium |

## Tier-gated but uses scopes we already grant

| Endpoint | Scope | Status | Notes |
|---|---|---|---|
| `/user-invites` | needs WRITE `users` scope | 403 with `users:read` | Tailscale requires write scope to read invites (PII concern). Audit log captures invite events (CREATE/UPDATE/DELETE on USER_INVITE targets) so we have visibility without granting elevated scope. |
| `/acl` snapshot | `policy_file:read` | 403 with our scopes | Audit log captures full ACL document on every change (Old + New + Actor). Snapshot is redundant. |

## Aliases / paths that 404 because the data lives at the canonical name

Some external references (third-party MCP servers, blog posts) use names that Tailscale's API returns 404 for at the exact path - but the data is already available via the canonical endpoint, which the connector polls today. Don't add new pollers for these:

- `/audit-logs` -> canonical path is `/logging/configuration`, polled by both Standard and Premium audit pollers. Returns `{"logs":[...]}` with `start`/`end` query params (verified live, May 2026).
- `/network-flow-logs` -> canonical path is `/logging/network`, polled by the Premium network poller. `/network-logs` is also a working alias for the same data.

## Endpoints that 404'd on Tailscale's API (tier-independent)

Genuinely missing paths - no known canonical alternative:

- `/services`, `/services/*` - Tailscale Services (newer feature, may require enablement)
- `/contacts` - tailnet contact info
- `/status`, `/log-streaming`, `/nameservers` - alternate paths used by some clients

If Tailscale ships these endpoints in future, add as needed.

## Split-DNS coverage decision

`/dns/split-dns` returns a dynamic-key object (`{"domain.example": ["resolver"]}`) that doesn't fit Sentinel CCP's strict-schema model. Covered via audit-log-based analytic rules and a hunting query instead - strictly richer than a periodic snapshot because we get the full Old + New diff + actor attribution on every change.
