---
name: azure-monitor-logs-ingestion
description: Ingest synthetic JSON records into Azure Monitor custom tables or supported Microsoft standard tables by provisioning a writable Custom-* DCR input stream.
---

# Ingest mock data into Azure Monitor Logs

Use `Tools\AzureMonitorLogsIngestion` when the user wants to load synthetic or
mock JSON records into a Log Analytics table.

## Safety

- Use a non-production workspace.
- Never commit tenant IDs, workspace IDs, resource IDs, credentials, tokens, or
  customer telemetry.
- Require a declared `Custom-*` input stream for both custom and standard
  destinations.
- Never POST directly to a reserved `Microsoft-*` stream.
- Provision one contract-specific DCE/DCR pair for each standard-table input
  contract. Do not add another input stream to an existing DCR.
- Do not claim that every standard table is supported. Preserve and report
  Azure `InvalidStream` and schema errors.
- Do not alter or delete existing connector DCRs.

## Workflow

1. Install and check authentication:

   ```powershell
   python -m pip install -e Tools\AzureMonitorLogsIngestion
   azure-monitor-logs-ingestion doctor
   ```

2. Create a version 1 contract from the examples under
   `Tools\AzureMonitorLogsIngestion\examples`.
3. Define the raw input columns and a transform that explicitly casts and
   projects the destination columns.
4. For a custom table, define the complete `_CL` destination schema.
5. For a standard table, confirm the table exists and specify its documented
   `Microsoft-*` output stream.
   - Give the contract unique `resources.dce` and `resources.dcr` names.
   - Reuse is allowed only when that DCR already contains exactly the same
     `Custom-*` input stream.
   - If a shared DCR already contains other streams, create a separate pair.
     Do not update the shared DCR and wait for propagation.
6. Validate without Azure writes:

   ```powershell
   azure-monitor-logs-ingestion inspect --contract <path> --payload <path>
   ```

7. Provision and ingest:

   ```powershell
   azure-monitor-logs-ingestion run `
     --contract <path> `
     --payload <path> `
     --report <report-path>
   ```

8. If ingestion returns `403`, assign Monitoring Metrics Publisher on the DCR
   to the sending identity, or rerun provisioning with `--principal-id` for a
   service principal or managed identity.
9. For post-ingestion query verification, prefer a suitable query tool
   advertised by the official Sentinel Triage MCP. If the MCP capability is
   unavailable or has a provider-level failure, verify through the CLI:

   ```powershell
   azure-monitor-logs-ingestion verify --contract <path>
   ```

   A genuine KQL or table error returned by the MCP is not a reason to retry
   through the CLI.

Report the destination table, record and batch counts, DCR/DCE resource IDs,
immutable DCR ID, DCR row/drop/transform metrics when available, verification
result, warnings, and the report path. An HTTP success confirms acceptance,
not completion of downstream processing.
