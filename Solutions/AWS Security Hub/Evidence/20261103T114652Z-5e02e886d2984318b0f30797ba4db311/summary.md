# Migration evidence — AWS Security Hub

Solution: **AWS Security Hub**
Run: `20261103T114652Z-5e02e886d2984318b0f30797ba4db311`
Profile: **qualification**
Recorded workflow status: **inProgress**
Current solution version at export: **3.2.2** (not a packaging claim)
Requested version action: **none**
Requested target solution version: **unknown (not recorded)** (not a packaged version)
Evidence exported at (UTC): **2026-11-03T13:27:15.976470+00:00**
Evidence exporter: **sentinel-xdr-migration 0.1.0** (export tool, not historical run version)
Exporter Python: **3.12.10**

**This is a local, curated snapshot, not trusted attestation or a new test run.**
Reported passes are not independently verified. Missing evidence is not a pass.
Content hashes describe export-time bytes, not proof of what historical tests ran.

## All workflow stages

| Stage | Recorded status | Attempts |
| --- | --- | --- |
| discovery | passed | 1 |
| conversion | passed | 1 |
| validation | passed | 1 |
| packaging | passed | 3 |
| deployment | passed | 1 |
| mockIngestion | passed | 1 |
| alertParity | passed | 0 |
| report | passed | 0 |

## Evidence coverage

| Report | Availability | Recorded status | Items | Recorded item outcomes |
| --- | --- | --- | --- | --- |
| conversion | available | unknown | 8 | converted=8 |
| structural | missing | unknown | 0 | not-recorded |
| runtimeGraph | available | unknown | 8 | passed=8; query hashes: matches=8 |
| runtimeTriage | missing | unknown | 0 | not-recorded |
| runtimeLogAnalytics | missing | unknown | 0 | not-recorded |
| runtimeAzureMonitorSdk | available | unknown | 8 | passed=8; query hashes: matches=8 |
| packaging | available | passed | 0 | not-recorded |
| queryParity | missing | unknown | 0 | not-recorded |
| alertParity | available | passed | 8 | passed=8 |
| solutionReport | available | unknown | 8 | structural: unknown=8 |

See `evidence.json` for every result (including failures, blocks and not-run),
relative paths, hashes, version decisions and provenance mismatches.

Source-query provenance mismatches detected: **0**.
Missing/unsupported provenance remains unverified, even when this count is zero.

## Limitations

- Raw messages, provider records, alerts, credentials and lab identities are omitted.
- Historical commands/tool versions and baseline decisions have no supported persisted contract.
- New runtime reports bind results to the exact source or Advanced Hunting query hash; legacy or mismatched hashes are stale/unbound. Hashes do not attest that a provider executed the query.
- Unknown fields/statuses are excluded or marked unknown, never interpreted as success.
- This directory is never read as workflow state or included in Marketplace packages.
