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
- The current contract tool may provision an isolated DCE/DCR pair as part of
  its supported route. A DCE is generally needed for private-link ingestion or
  when a DCR has no ingestion endpoint; it is not a universal Logs Ingestion
  API requirement. Check DCE-creation permission only when the selected plan
  includes a DCE.
- Do not add another input stream to an existing connector DCR.
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
   projects the destination columns. A public table schema does not reveal a
   connector's internal parser or enrichment logic; the anonymous
   [`/v1/metadata` endpoint](https://api.loganalytics.io/v1/metadata) is schema
   metadata, not ingestion capability or parser evidence. See the
   [Logs Ingestion API overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
   and [table feature matrix](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables-features).
4. For a custom table, define the complete `_CL` destination schema.
5. For a standard table, confirm the table exists and specify its documented
   `Microsoft-*` output stream and supported Logs Ingestion API route.
   Structured records enter through the customer-authored `Custom-*` input
   stream and `transformKql`; do not assume reserved or service-managed
   destination columns are writable.
   - During Sentinel solution Qualification, prefer a DCR listed or referenced
     by the solution only when that DCR is already deployed in the locked
     workspace and exactly matches the fixture contract, public `Custom-*`
     input stream, schema/transform, destination, and endpoint. A package
     reference alone does not prove that the DCR exists or is compatible.
     Otherwise use a separate contract-specific DCR route; the current tool
     may provision an isolated DCE/DCR pair as part of that route. Never
     change an existing connector DCR or add an input stream to it.
   - Keep resource names unique for any DCE/DCR pair provisioned by the
     contract.
   - Reuse is allowed only when that DCR already contains exactly the same
     `Custom-*` input stream.
   - If a shared DCR already contains other streams, use a separate
     contract-specific route; do not update the shared DCR and wait for
     propagation.
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
