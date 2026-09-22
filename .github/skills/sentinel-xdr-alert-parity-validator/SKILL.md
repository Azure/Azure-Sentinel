---
name: sentinel-xdr-alert-parity-validator
description: Perform strict lab-only parity validation between a Microsoft Sentinel Analytic Rule and its migrated Defender XDR Custom Detection.
---

# Validate Analytic Rule and Custom Detection alert parity

Use this skill only in a non-production lab after conversion, structural
validation, deployment, and mock-data review have succeeded.

## Acceptance criteria

Parity is strict. For every selected rule, require:

- the same number of alerts;
- the same normalized scenario match keys;
- the same severity and tactics;
- the same normalized entities;
- the same decisive matched-event evidence; and
- no alert from the benign control records.

Any mismatch fails migration validation. Do not silently accept differences
caused by schedule, lookback, grouping, suppression, thresholds, or entity
mapping. Align those settings or report an explicit platform limitation.

## Safety and lifecycle

- Both rules must be disabled before the test starts.
- Require a unique marker that occurs in the reviewed mock payload.
- Enable only explicitly selected converted rules.
- Never use production telemetry or a production workspace.
- Do not wait with fixed sleeps. Start the run, then query when the platforms
  expose the alerts.
- Always run `complete-alert-parity` or `abort-alert-parity`; both force every
  test rule back to disabled.

## Full qualification batch

For internal solution qualification, deploy every reviewed AR/CD pair disabled,
then prepare one fixture per detection:

```json
{
  "fixtures": [
    {
      "detection": "Detection.yaml",
      "contract": "contracts/stream.json",
      "payload": "mocks/detection.json",
      "scenarioMarker": "unique-detection-marker",
      "expectedMatchKeys": ["expected-malicious-key"]
    }
  ]
}
```

Paths are resolved relative to the batch-plan file. The plan must cover every
converted detection exactly once.

Start the batch:

```powershell
sentinel-xdr-migration start-alert-parity-batch `
  --solution "<solution-path>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --plan "<qualification-plan.json>"
```

The command verifies all ARs and CDs are disabled, enables all reviewed pairs,
ingests every fixture, and emits a separate capture plan and expected-key set
for each detection. If enablement or any ingestion fails, it disables all
rules before returning the failure.

## Targeted start

```powershell
sentinel-xdr-migration start-alert-parity `
  --solution "<solution-path>" `
  --workspace-resource-id "<workspace-arm-id>" `
  --contract "<ingestion-contract>" `
  --payload "<reviewed-mock-json>" `
  --scenario-marker "<unique-marker>" `
  --expected-match-key "<expected-malicious-key>" `
  --detection "<Detection.yaml>"
```

Use the targeted command for troubleshooting a subset or rerunning one
detection. It:

1. verifies the AR and CD both exist and are disabled;
2. enables both through Azure Resource Manager and Microsoft Graph;
3. ingests the payload through `azure-monitor-logs-ingestion`;
4. writes
   `Reports/<solution>/sentinel-xdr-migration/alert-parity-state.json`; and
5. emits Sentinel and Advanced Hunting capture queries.

## Capture alerts

Prefer suitable tools advertised by the official Sentinel Triage MCP for both
capture queries. Fall back to Log Analytics CLI/API for `SecurityAlert` and
Microsoft Graph for `AlertInfo`/`AlertEvidence` only for provider-level
failures. A genuine KQL error is not a reason to change providers.

Normalize each platform result into:

```json
{
  "results": [
    {
      "detection": "Detection.yaml",
      "analyticRule": {
        "alerts": [
          {
            "matchKey": "stable-event-or-correlation-key",
            "severity": "high",
            "tactics": ["Exfiltration"],
            "entities": {},
            "evidence": {}
          }
        ]
      },
      "customDetection": {
        "alerts": []
      }
    }
  ]
}
```

Platform alert IDs are not comparable. `matchKey` must be derived from stable
mock-event or aggregation keys. Normalize entity names and evidence fields to
the same semantic shape before comparison; never remove a differing value to
manufacture parity.

The declared expected match-key set is authoritative. If both platforms alert
on the same benign control key, parity still fails. Repeat
`--expected-match-key` when multiple malicious alerts are expected; when it is
omitted, the scenario marker is the sole expected key.

## Complete or abort

```powershell
sentinel-xdr-migration complete-alert-parity `
  --solution "<solution-path>" `
  --results "<normalized-results.json>"
```

This writes `alert-parity-report.json` and disables all selected rules even
when parsing or comparison fails.

If capture cannot be completed:

```powershell
sentinel-xdr-migration abort-alert-parity --solution "<solution-path>"
```
