# Cloudflare CCF migration mocks

Each analytic rule has an isolated raw `Custom-Cloudflare` payload containing
the minimum malicious scenario needed to produce exactly one query result and
a boundary-safe benign control. `validation-manifest.json` records the expected
result count and stable entity keys for strict AR/CD parity.

| Rule | Mock | Malicious / benign records |
|---|---|---:|
| Bad client IP | `BadClientIp.json` | 1 / 1 |
| Client request from country in blocklist | `ClientRequestFromBlockedCountry.json` | 1 / 1 |
| Empty user agent | `EmptyUserAgent.json` | 1 / 1 |
| Multiple error requests from single source | `MultipleErrorsSingleSource.json` | 101 / 100 |
| Multiple user agents for single source | `MultipleUserAgentsSingleSource.json` | 11 / 10 |
| Unexpected client request | `UnexpectedClientRequest.json` | 1 / 1 |
| Unexpected POST requests | `UnexpectedPostRequests.json` | 1 / 1 |
| Unexpected URI | `UnexpectedURI.json` | 1 / 1 |
| WAF Allowed threat | `WAFAllowedThreat.json` | 1 / 1 |
| XSS probing pattern | `XSSProbingPattern.json` | 1 / 1 |

The threshold controls deliberately sit exactly at the non-triggering boundary.
The "multiple error requests" source rule does not inspect response status, so
its mock validates the implemented GET-count behavior rather than its title.

The WAF payload uses the current CCF fields `SecurityAction`,
`SecurityRuleID`, and `SecurityRuleDescription`. The parser maps those fields
to the legacy WAF names required by the analytic rule.

Ingest only one file at a time into a non-production lab while its selected AR
and CD are the only enabled pair. The authoritative DCR transform supplies
`TimeGenerated`.
