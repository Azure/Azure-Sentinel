# Migration evidence — PaloAlto-PAN-OS

Solution: **PaloAlto-PAN-OS**
Run: `20261103T114652Z-07d313a034d64006a86da04741bbadea`
Profile: **qualification**
Recorded workflow status: **inProgress**
Current solution version at export: **3.2.2** (not a packaging claim)
Requested version action: **none**
Requested target solution version: **unknown (not recorded)** (not a packaged version)
Evidence exported at (UTC): **2026-11-03T13:32:24.425026+00:00**
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
| packaging | passed | 7 |
| deployment | passed | 2 |
| mockIngestion | pending | 0 |
| alertParity | pending | 0 |
| report | pending | 0 |

## Evidence coverage

| Report | Availability | Recorded status | Items | Recorded item outcomes |
| --- | --- | --- | --- | --- |
| conversion | available | unknown | 5 | converted=5 |
| structural | available | unknown | 5 | passed=5 |
| runtimeGraph | available | unknown | 5 | passed=5; query hashes: matches=5 |
| runtimeTriage | missing | unknown | 0 | not-recorded |
| runtimeLogAnalytics | missing | unknown | 0 | not-recorded |
| runtimeAzureMonitorSdk | available | unknown | 5 | passed=5; query hashes: matches=5 |
| packaging | available | passed | 0 | not-recorded |
| queryParity | missing | unknown | 0 | not-recorded |
| alertParity | available | passed | 0 | not-recorded |
| solutionReport | available | unknown | 5 | structural: passed=5 |

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
