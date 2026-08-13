# MITRE ATT&CK coverage - Fivetran solution

Verified 2026-07-22 against
https://learn.microsoft.com/en-us/azure/sentinel/mitre-coverage (Sentinel aligns
to **ATT&CK v18**) and the live ATT&CK knowledge base.

## Mappings

| Artifact | Tactic | Technique | Why it is appropriate |
| --- | --- | --- | --- |
| `Analytic Rules/FivetranIngestionGap.yaml` | Defense Evasion | **T1562** (Impair Defenses) | A stop in Fivetran log ingestion = loss/impairment of security telemetry, the core behaviour T1562 covers (disrupting logging/forwarding pipelines and SIEM ingestion). |
| `Analytic Rules/FivetranAuthFailures.yaml` | Credential Access | **T1110** (Brute Force) | A spike of authentication/authorization/credential failures in the Fivetran log stream matches the brute-force / credential-stuffing pattern against the accounts Fivetran uses. Threshold-based (>10/hour) so routine one-off credential expiry does not alert. Same mapping used by comparable Content Hub rules (Bitglass MultipleFailedLogins, GitLab BruteForce). |
| `Hunting Queries/FivetranSevereSpike.yaml` | Defense Evasion | **T1562** (Impair Defenses) | A surge of SEVERE pipeline errors can indicate the log source being degraded or tampered with. Corrected from the initial `Impact`/`T1499` (Endpoint DoS), which specifically means resource-exhaustion/flooding and does not describe pipeline errors. |

The detections cover two real, distinct risks: **protecting the integrity and
availability of the Fivetran security log source** (Defense Evasion / T1562) and
**detecting credential attacks against the Fivetran service accounts** (Credential
Access / T1110). Accuracy was prioritised over breadth - no technique is claimed
that the query does not actually evidence.

### Honesty note on T1110

The only signal fields Fivetran emits are `Level`, `CreatedAt` and `Message`;
there is no structured account or source-IP field, so no entity mappings are
asserted. The T1110 claim rests on a *volume threshold* of failure-keyword
messages, which is the defensible brute-force signal. A low count could also be
benign credential expiry, which is why the rule only fires above the threshold.

## Important version note (why we use T1562, not T1685)

In the current MITRE ATT&CK knowledge base, **Impair Defenses was renumbered from
`T1562` to `T1685`** (the old `T1562` and `T1562.008` URLs now redirect to
`T1685` / `T1685/002`). This is verifiable directly at
https://attack.mitre.org/techniques/T1562/ which issues an HTTP redirect to
https://attack.mitre.org/techniques/T1685/ (checked 2026-07-26).

However, **Microsoft Sentinel and the Azure-Sentinel Content Hub tooling still use
`T1562`** - every current solution rule maps to `T1562` and there are zero uses of
`T1685` in the repo. Using `T1685` today would fail solution validation and would
not light up the Sentinel MITRE coverage matrix. Revisit if/when Sentinel tooling
adopts the `T1685` numbering.

## How to confirm coverage after deployment

In the Defender portal: **Microsoft Sentinel > Threat management > MITRE ATT&CK**.
Search technique `T1562`; once the ingestion-gap analytics rule is active (and the
hunting query present) the tile shows active/simulated coverage for Defense Evasion
- Impair Defenses. Search `T1110`; once the auth-failures analytics rule is active
the tile shows coverage for Credential Access - Brute Force.
