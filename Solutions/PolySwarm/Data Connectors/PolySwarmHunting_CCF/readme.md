# PolySwarmHunting_CCF

A Codeless Connector Framework (CCF) `RestApiPoller` connector that polls your
PolySwarm live hunt results (`/v3/hunt/live/list`) and writes each result as a native
indicator into Microsoft Sentinel's `ThreatIntelIndicators` table. Because the
indicators are native, Microsoft's own built-in indicator matching rules run against
them automatically, alongside this solution's analytics rules. Connector id
`PolySwarmHuntingCCFDefinition`. Requires the live hunting entitlement on your
PolySwarm account.

Files: `PolySwarmHunting_CCF_DataConnectorDefinition.json`,
`PolySwarmHunting_CCF_DCR.json`, `PolySwarmHunting_CCF_PollerConfig.json`.

## Summary

Each hunt result becomes one file-hash indicator per digest it carries (SHA-256, SHA-1
and MD5), because most customer logs carry MD5 or SHA-1 rather than SHA-256. The
`Pattern` is `[file:hashes.'SHA-256' = '<value>']`, `[file:hashes.'SHA-1' = '<value>']`
or `[file:hashes.'MD5' = '<value>']`, with the digest lowercased. `Confidence` comes from
PolyScore, `SourceSystem` is `PolySwarm`, `LastUpdateMethod` is `PolySwarm hunting`,
labels come from malware family and tags, and `AdditionalFields` carries `polyscore,
family, rule_name, community, permalink, tags, detections, digest_type, stixIdHex` (the
last is the hash seed used to build the deterministic `indicator--` id, kept for
traceability). The id is derived from digest type, digest value, community and rule
name, so the same digest from the same rule always lands on the same id. A result that
carries only some digests produces only those indicators. Hunt results carry `sha256`, `sha1` and `md5` on every row. The permalink is constructed
(`https://polyswarm.network/scan/results/file/<sha256>/<instance_id>`), not returned
by the API; it uses the hunt row's own `instance_id` and the result's SHA-256 (empty if
the result has no SHA-256), and has not been click-verified in a browser.

The DCR has three data flows on the same input stream, each writing to
`Microsoft-ThreatIntelIndicators`: one per digest (SHA-256, SHA-1, MD5). Each flow's
transform keeps only rows where its digest is non-empty and emits a single indicator for
it. They use only `where`, `extend` and `project` and functions the reference CCF
transforms already use, deliberately avoiding `mv-expand`, whose support in transforms
is unconfirmed. All three flows writing to the same table was confirmed in a live workspace in October
2026.

Query indicators from this connector with:

```
ThreatIntelIndicators | where SourceSystem == "PolySwarm" and LastUpdateMethod == "PolySwarm hunting"
```

## Live API facts this connector's design is built on

- `/v3/hunt/live/list` accepts only a relative `since` parameter in minutes.
  `start`/`end`/`start_date`/`end_date` are silently ignored (confirmed live: a
  2020-01-01 end date still returned current results identical to no filter). This
  connector's `since` window is bound to the same `queryWindowInMin` parameter that
  sets the CCF poll interval, since there is no CCF macro for "elapsed minutes" the
  way there is for absolute window timestamps.
- `community` and `rule_name` are real, server-validated filters (an unknown
  community returns HTTP 400; an unmatched rule name returns HTTP 204).
  `min_polyscore` could not be proven to filter server-side in black-box testing; it
  is exposed as a connector input because the spec calls for it and `0` is a safe
  no-op, but do not rely on it enforcing a minimum without a live Azure-side check.
- Paging uses `{"has_more": bool, "limit": int, "offset": "<opaque token>", "result":
  [...]}`. `offset` is an opaque token to echo back, not an integer skip-count. A
  window with zero results returns HTTP 204 with an empty body. Wired as CCF's
  `NextPageUrl` paging type, `nextPageTokenJsonPath: $.offset`, `nextPageParaName:
  offset`, `hasNextFlagJsonPath: $.has_more`.
- Authentication: the live `Authorization` header takes the raw key with no prefix.
  CCF's APIKey auth defaults `ApiKeyIdentifier` to the literal string `"token"` when
  not otherwise specified, which would have produced `Authorization: token <key>`
  (wrong). The connector sets `"ApiKeyName": "Authorization"` with no `ApiKeyIdentifier`.
  An empty `ApiKeyName` is rejected by Azure at Connect ("The ApiKeyName field is
  required", lab 2026-10-16). Whether a prefix is added is confirmed by the first poll:
  PolySwarm answers 401 to a prefixed key.

## Lag margin and overlap

`/v3/hunt/live/list` only accepts a relative `since` in minutes, so each poll asks for
the polling window plus a fixed lag margin of 10 minutes (the constant `10` in the
`since` expression of `PolySwarmHunting_CCF_PollerConfig.json`). A poll that runs late
therefore still reaches back to the end of the previous window and cannot open a gap.
The overlap is harmless: every indicator id is derived from the digest type and value
(plus community and rule name), so a hit seen twice updates the same indicator instead
of adding a duplicate.

## What you see on the connector page

The connector page tells the customer which of three states applies. Not configured:
no key entered yet, nothing expected. Configured but nothing has arrived yet: normal on
a new connection, usually because there are no live hunt rules in PolySwarm or none has
matched in the window, or because the first poll is pending (up to the polling
interval, 15 minutes by default). Error: check the `SentinelHealth` table. The
connectivity criterion is `HasDataConnectors`, which reports connected once the
connector is deployed and never raises an error or warning merely because no data has
arrived.

## Empty responses (HTTP 204)

An empty hunt window, an unmatched rule name and a lookup with no result are all
answered with HTTP 204 and an empty body (measured; see the recorded fixtures). That
is the API's not-found answer, so it must produce zero rows and no error. The poller
config sets nothing for this: no reference CCF connector in Microsoft's public
solutions repository (including the other threat intelligence CCF connectors) sets any option for empty responses, and no such
setting is known, so none is invented. In a live workspace, polls with nothing new produced no rows
and the connector stayed connected.

## Prerequisites

- A Microsoft Sentinel workspace.
- A PolySwarm Team API key with the live hunting entitlement.
- At least one live PolySwarm hunt rule configured and producing results; a connector
  with no hunt results has nothing to poll, and the connector page says so.

## Configuration fields (connector UI)

| Field | Notes |
| --- | --- |
| PolySwarm API Key | Password field. Your PolySwarm Team API key. |
| Community | Required text, default `public`. A private community's short name, never its display name (a display name returns 400). |