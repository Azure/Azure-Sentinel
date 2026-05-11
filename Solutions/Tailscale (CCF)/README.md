# Tailscale (CCF)

Microsoft Sentinel solution that ingests Tailscale telemetry via the OAuth2-secured Tailscale API.

## Data connectors

Install **one** of these connectors based on your Tailscale plan:

| Connector | Endpoint(s) | Tailscale plan | Status |
|---|---|---|---|
| **Tailscale Standard (CCF)** | `/logging/configuration` | Personal (Free) + Standard | **Included** |
| Tailscale Premium (CCF) | `/logging/configuration` + `/logging/network` | Premium + Enterprise | Planned |

The split mirrors what the Tailscale API actually exposes per tier — Network flow logs are only available on Premium and above. If you're on Personal or Standard, install Tailscale Standard; if you're on Premium or Enterprise install Tailscale Premium (which covers both endpoints).

## Contents

- **Data connector** — Sentinel UI card ("Tailscale Standard (CCF)") that uses OAuth2 client-credentials auth, polling the configuration endpoint every 5 minutes.
- **Custom table** — `Tailscale_Configuration_CL` (typed columns for actor, action, target, origin, new, old).
- **5 analytic rules**:
  - New API access token or OAuth client created (Medium)
  - Policy file (ACL) modified (Medium)
  - Auth key created (Low)
  - Exit node advertised or approved (Low)
  - Mass credential revocation in short window (High)

## Pre-requisites

1. A Microsoft Sentinel-enabled Log Analytics workspace.
2. A Data Collection Endpoint (DCE) in the same region.
3. A Tailscale OAuth client with the **Audit Logs - Read** scope:
   - Generate at <https://login.tailscale.com/admin/settings/oauth>
   - Copy the Client ID and Client Secret (secret shown only once)
4. Your tailnet name (e.g. `tail-XXXX.ts.net`) from the [Keys page](https://login.tailscale.com/admin/settings/keys).

## Connect

1. Install this solution via **Content Hub**.
2. Sentinel → **Data Connectors** → search "Tailscale Standard (CCF)" → **Open connector page**.
3. Supply:
   - Tailscale tailnet name
   - OAuth Client ID
   - OAuth Client Secret
4. Click **Connect**. Polling begins on a 5-minute cadence.

## Why OAuth client, not a personal API token

Tailscale's `logging/configuration` endpoint requires the `logs:configuration:read` scope. Personal API access tokens (`tskey-api-...`) are unscoped — when used against this endpoint, the API returns HTTP 200 but with `logs: null`, silently. OAuth clients are required to grant the specific scope.

## Verification

After Connect, in Sentinel Logs:

```kql
Tailscale_Configuration_CL
| sort by TimeGenerated desc
| take 50
```

## Support

Community-supported solution maintained by noodlemctwoodle. Issues: <https://github.com/noodlemctwoodle/Azure-Sentinel/issues>.
