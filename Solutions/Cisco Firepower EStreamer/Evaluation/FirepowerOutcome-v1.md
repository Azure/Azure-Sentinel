# Cisco Firepower response outcome contract v1

This contract makes detection and response decisions machine-readable without introducing a new data store or an AI dependency. Playbooks emit the record in a Microsoft Sentinel incident comment. Humans remain authoritative for containment decisions.

## Record format

```text
[FirepowerOutcome:v1] signal=<ml-only|signature|corroborated|unknown>; decision=<policy-denied|approved|rejected|not-required|unknown>; containment=<not-attempted|succeeded|failed|unchanged>; reason=<stable-reason-code>; ruleVersion=<version>; policyVersion=1.0.0
```

Values are deliberately bounded. Free-form analyst explanation may follow the record but must not replace it.

## Safety invariants

1. `signal=ml-only` cannot produce automatic containment. The Teams HITL path requires an explicit analyst decision and records that decision before any change.
2. An AI-generated recommendation cannot modify production analytics, policies, or Firepower objects directly.
3. Candidate changes must be replayed against the cases below and reviewed by a human.
4. Every promoted change records its rule, playbook, policy, and evaluation-corpus versions.
5. Ambiguous parsing fails closed to `signal=unknown` and cannot silently become an automatic containment path.

## Deterministic evaluation cases

| Case | Evidence | Expected signal | Expected decision/outcome |
|---|---|---|---|
| E01 | GID 411 only | `ml-only` | `policy-denied/not-attempted` |
| E02 | `is_ml_only` only | `ml-only` | `policy-denied/not-attempted` |
| E03 | GID 1 and high-priority classification | `signature` | eligible for policy-controlled response |
| E04 | GID 411 plus independent signature for the same flow/window | `corroborated` | eligible for HITL response |
| E05 | malformed or missing GID | `unknown` | no automatic containment |
| E06 | no IP entity | any | `not-required/not-attempted` |
| E07 | Firepower object does not exist | any eligible | `approved/failed` |
| E08 | Firepower update succeeds | any eligible | `approved/succeeded` |
| E09 | analyst rejects Teams card | any | `rejected/not-attempted` |
| E10 | Teams approval expires | any | `unknown/not-attempted` |

## Controlled improvement loop

Outcome records and workbook trends may be used by an external agent to propose KQL, mapping, threshold, or playbook changes. A proposal must include the triggering evidence, a diff, replay results for every evaluation case, cost impact, safety-invariant results, and a rollback condition. Promotion occurs only through a reviewed pull request and canary deployment.
