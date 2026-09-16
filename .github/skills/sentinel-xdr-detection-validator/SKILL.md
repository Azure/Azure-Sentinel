---
name: sentinel-xdr-detection-validator
description: Validate generated XDR Detection YAML structurally and validate source and converted KQL through official Microsoft Sentinel Triage MCP tools first, with direct API fallback.
---

# Validate XDR Detection YAML

Use the `sentinel-xdr-migration` CLI for deterministic planning, structural
validation, fallback execution, and reporting. Runtime query execution prefers:

- Microsoft Sentinel Triage MCP for every query operation supported by the
  connected server:
  `https://sentinel.microsoft.com/mcp/triage`.
- Log Analytics CLI/API as the original Sentinel-query fallback.
- Microsoft Graph Advanced Hunting through the CLI as the Advanced Hunting
  fallback.

## Provider fallback policy

Inspect the connected Triage MCP tools and use a suitable advertised tool
first. Do not invent a tool name or assume a capability. Fall back to the
corresponding direct provider only when Triage cannot act as a provider,
including:

- the MCP server or the required query tool is unavailable;
- authentication, consent, or permission fails;
- the request times out or the MCP service returns a transient/provider error;
- a provider failure prevents completion of the full solution batch.

Original Sentinel queries fall back to Log Analytics. Advanced Hunting queries
fall back to Graph. Do not fall back when Triage successfully executes the
request and returns a real KQL semantic/runtime error. That is a detection
failure, not an MCP failure. Do not combine providers within one query-family
report; if Triage fails mid-batch, rerun that complete batch through its direct
provider.

## Workflow

1. Run `sentinel-xdr-migration doctor`.
2. On first run, run `sentinel-xdr-migration setup --non-interactive`.
3. Ask before launching interactive authentication. Never block offline conversion.
4. Run:

   ```powershell
   sentinel-xdr-migration validate --solution "<solution-path>"
   ```

5. Stop if structural errors remain.
6. Generate the complete runtime plan:

   ```powershell
   sentinel-xdr-migration validation-plan --solution "<solution-path>"
   ```

   Use advertised official Triage MCP tools first for every supported
   `sentinelQuery` and `advancedHuntingQuery`. For Advanced Hunting, invoke
   `RunAdvancedHuntingQuery`. If the connected MCP does not advertise a
   suitable original Sentinel workspace-query tool, use the Log Analytics
   CLI/API path without treating that capability gap as a KQL failure.

   Normalize Advanced Hunting results into a JSON file containing exactly one
   entry per detection:

   ```json
   {
     "results": [
       {
         "detection": "Example.yaml",
         "status": "passed",
         "statusCode": 200,
         "rowCount": 0,
         "schemaColumnCount": 12,
         "error": null
       }
     ]
   }
   ```

   Allowed statuses are `passed`, `failed`, and `blocked`. Then record the
   provider results:

   ```powershell
   sentinel-xdr-migration record-runtime-validation `
     --solution "<solution-path>" `
     --provider triage-mcp `
     --results "<normalized-results.json>"
   ```

7. If and only if Triage has an Advanced Hunting provider-level failure, run
   the complete Advanced Hunting batch through Graph:

   ```powershell
   sentinel-xdr-migration validate-advanced-hunting --solution "<solution-path>"
   ```

8. Both providers create normalized JSON and self-contained HTML reports under
   `XDR Detections`. Treat `blocked` as an environment gap, not a conversion
   failure.
9. For every rule:
   - execute the original `sentinelQuery`;
   - execute the `advancedHuntingQuery`;
   - record whether each query binds and executes;
   - compare returned entity columns when representative rows exist.
10. Zero rows are not proof of behavioral parity. Record them as execution
   success with data validation still pending.
11. Do not change `contentProvenance.conversion.status` to `validated` unless
   both queries execute and the entity output has been reviewed.

Return a per-rule result and an overall pass/needs-review summary.
