# PolySwarmFeed_CCF

A Codeless Connector Framework (CCF) `RestApiPoller` connector that reads PolySwarm's
curated indicator feed directly from the PolySwarm TAXII 2.1 server and writes each
indicator object as a native indicator into Microsoft Sentinel's
`ThreatIntelIndicators` table. Intended for accounts without hunts configured, so they
still get native indicators on day one. Connector id `PolySwarmFeedCCFDefinition`.
Requires the `taxii` entitlement plus the specific feed's own entitlement (for
example `taxii_trustgroup`) on your PolySwarm account.

Files: `PolySwarmFeed_CCF_DataConnectorDefinition.json`, `PolySwarmFeed_CCF_DCR.json`,
`PolySwarmFeed_CCF_PollerConfig.json`.

## Summary

Query indicators from this connector with:

```
ThreatIntelIndicators | where SourceSystem == "PolySwarm" and LastUpdateMethod == "PolySwarm curated feed"
```

`Pattern` is passed through verbatim from the source (already a valid STIX pattern
string); `ObservableKey`/`ObservableValue` are best-effort parsed out of it via a
regex, with a documented fallback if a future non-hash SCO type does not match.
Because `Pattern`/`Data` (the fields Microsoft's TI matching actually uses) never
depend on the regex succeeding, a parse miss degrades gracefully instead of dropping
the indicator. `AdditionalFields` carries `pattern_version, observable_parse_note`.

## Live API facts this connector's design is built on

- **Discovery**: `GET https://api.polyswarm.network/v3/stix/taxii2/`, header
  `Accept: application/taxii+json;version=2.1`, returns three API roots:
  `trustgroup`, `ransomware`, `freemium`.
- **Authentication is HTTP Basic, not the `Authorization: <key>` header the rest of
  the PolySwarm v3 API uses.** Username is your PolySwarm account/Team number;
  password is the same Team API key. Confirmed live.
- **Collections**: each root currently has one collection (`trustgroup`'s is "14-Day
  Feed"). The collection ids are the same on every account (measured
  2026-10-16 with two accounts), so the Feed dropdown carries `{root}/collections/{id}`
  and the customer never types an id.
- **Objects endpoint**: `GET {root}/collections/{id}/objects/?added_after=...&limit=1..50`
  returns `{objects: [...], more: bool, next: <opaque token>}`. **Each element of the
  top-level `objects` array is itself a full STIX bundle**, not a flat STIX object,
  containing a mix of `malware`, `file`, `relationship`, `indicator`,
  `malware-analysis` and `attack-pattern` SDOs. Only the `indicator` objects map to
  `ThreatIntelIndicators`; the rest do not fit that table's shape. Server-side
  `match[type]=indicator` filtering did not reduce the bundle mix in testing, so
  filtering to indicator-only happens client-side, via
  `eventsJsonPaths: ["$.objects[*].objects[*]"]` at the CCF JSON-extraction layer
  (not `mv-expand` inside the ingestion-time transform KQL, since that subset's
  support for `mv-expand` is unconfirmed).
- `indicator` objects observed live carry only `id`, `pattern`, `pattern_type`,
  `pattern_version`, `valid_from`, `confidence` (a fixed `99` in every sample seen);
  no `labels`, family or description. This is the known, already-documented gap
  between the curated feed and connector A's metadata-rich hunt results; it is not a
  build defect.
- Live patterns observed were all file-hash indicators
  (`file:hashes.MD5`/`'SHA-1'`/`'SHA-256'`); no url/domain/ip indicators were
  observed in the collection tested. This may reflect that specific collection's
  content rather than a hard limitation of the feed.
- Paging: `nextPageTokenJsonPath: $.next`, `hasNextFlagJsonPath: $.more`.

## What you see on the connector page

The connector page tells the customer which of three states applies. Not configured:
details not entered yet, nothing expected. Configured but nothing has arrived yet:
normal on a new connection, usually because the account has no TAXII entitlement for
the chosen feed, or because the first poll is pending (up to the polling interval, 60
minutes by default). Error: check the `SentinelHealth` table. The connectivity
criterion is `HasDataConnectors`, which reports connected once the connector is
deployed and never raises an error or warning merely because no data has arrived.

## Empty responses (HTTP 204)

PolySwarm answers a lookup with no result as HTTP 204 and an empty body, which is the
API's not-found answer and must be zero rows, not an error. The TAXII objects endpoint
has not been observed returning a 204 for an empty window (an empty window is expected
to be an envelope with no objects), but this is not measured. The poller config sets
nothing for empty responses: no reference CCF connector (including the other threat intelligence CCF connectors) sets any such
option and none is known, so none is invented.

## Digest types

The feed carries indicator patterns for MD5, SHA-1 and SHA-256. TAXII writes
the MD5 key unquoted (`file:hashes.MD5`) and the others quoted
(`file:hashes.'SHA-1'`, `file:hashes.'SHA-256'`). The transform passes `Pattern`
through verbatim and parses `ObservableKey` and `ObservableValue` out of it with a
regex that accepts both forms, so all three parse. Consumers that
match on `ObservableKey` must accept both the quoted and unquoted MD5 form.

## Prerequisites

- A Microsoft Sentinel workspace.
- A PolySwarm account number and Team API key with the matching `taxii`/`taxii_<feed>`
  entitlement; auth against a root you are not entitled to fails.

## Configuration fields (connector UI)

| Field | Notes |
| --- | --- |
| PolySwarm Account Number | Text. Your PolySwarm Team/Account number. This is the TAXII server's Basic-auth username, not your API key. |
| PolySwarm API Key | Password field. This is the TAXII server's Basic-auth password. |
| Feed | Dropdown: Trust Group 14-day feed, Ransomware family feed, Freemium feed. Each value carries its collection. |
| Polling window (minutes) | Number, default `60`. |

## Post-deployment steps

No Azure RBAC role assignment is needed for this connector, for the same reason as
`PolySwarmHunting_CCF`: it writes to native `ThreatIntelIndicators` through Sentinel's
own managed CCF infrastructure. After deployment, open the connector in Data
Connectors, enter the fields above (the PolySwarm Trust Group's "14-Day Feed"
collection is a reasonable default), and click Connect.

## Cross-reference with Analytic Rules and Hunting Queries

The rules and queries built against the hunting connector also accept this connector
as an alternative data source, since both write the same `ThreatIntelIndicators`
shape with `SourceSystem == "PolySwarm"`: a customer can deploy either connector alone
and still satisfy the rules' requirements. See
`Data Connectors/PolySwarmHunting_CCF/readme.md`.

## Volume

About 500,000 indicators and 0.5 GB a day into ThreatIntelIndicators for the Trust Group
14-day feed, measured in a test workspace from 16 to 19 October 2026. The connector page
says so too. Microsoft Sentinel charges for data it ingests, so check its pricing before
connecting the feed.
