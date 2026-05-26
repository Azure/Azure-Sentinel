# Sentinel DCR Schema Freeze — Phase 6

These 5 Data Collection Rule (DCR) JSON definitions represent the **Phase 6 schema freeze** for
StratoSecure's Microsoft Sentinel integration. Once tenants are onboarded and custom tables are
created in Log Analytics, **columns are immutable**. Any additive schema change requires a new
DCR version and coordinated table migration. Breaking column changes are not permitted.

---

## DCR Manifest

| DCR File | Stream Name | Table | Purpose |
|---|---|---|---|
| `StratoSecure_Findings_DCR.json` | `Custom-StratoSecure_Findings_CL` | `StratoSecure_Findings_CL` | All security findings from SAST, SCA, and DAST scans, enriched with SLA, exception, and AppSec score. |
| `StratoSecure_ApiInventory_DCR.json` | `Custom-StratoSecure_ApiInventory_CL` | `StratoSecure_ApiInventory_CL` | API endpoints discovered per scan, with auth type, internet exposure, and data classification. |
| `StratoSecure_Remediation_DCR.json` | `Custom-StratoSecure_Remediation_CL` | `StratoSecure_Remediation_CL` | Immutable audit trail of every finding status transition (open→accepted, accepted→resolved, etc.). |
| `StratoSecure_ScanSummary_DCR.json` | `Custom-StratoSecure_ScanSummary_CL` | `StratoSecure_ScanSummary_CL` | One record per scan: aggregate severity counts, new vs resolved findings, and scan duration. |
| `StratoSecure_Exception_DCR.json` | `Custom-StratoSecure_Exception_CL` | `StratoSecure_Exception_CL` | Exception lifecycle events (created, expired, revoked) with approver and justification reference. |

### Column Naming Note

All DCR columns use `StraTenantId` (type: `string`) instead of `TenantId`. The name `TenantId`
is **reserved by Azure Log Analytics** and is silently overridden at ingestion. Using `StraTenantId`
ensures tenant isolation is enforced correctly in all KQL queries.

---

## SENT-07 Deferral — PlaybookRuns_CL

**PlaybookRuns_CL: intentionally excluded from Phase 6.**

Schema deferred to **Phase 9 (Sentinel Analytics Rules)**. Rationale: Sentinel playbooks require
Analytics Rules (Phase 9) to exist before trigger data is available, and the schema depends on
rule definitions that do not yet exist. Freezing a premature schema would require a breaking change
in Phase 9. SENT-07 is tracked and will be addressed when Analytics Rules are implemented.

---

## Tenant Onboarding

To deploy these DCRs for a new tenant:

1. Replace `<customer-region>` with the Azure region of the tenant's Log Analytics workspace
   (e.g., `eastus`, `westeurope`).

2. Replace `<workspace-arm-resource-id>` with the full ARM resource ID of the workspace:
   ```
   /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>
   ```

3. Deploy each DCR via ARM template or Azure CLI:
   ```bash
   az monitor data-collection rule create \
     --resource-group <customer-rg> \
     --name StratoSecure-Findings \
     --rule-file StratoSecure_Findings_DCR.json
   ```

4. Record the DCR immutable ID output (`properties.immutableId`) for each table. These IDs
   are stored in the tenant's integration config under `dcr_immutable_ids` (a dict mapping
   table name to immutable ID).

5. Configure the tenant in StratoSecure via `PUT /tenants/{id}/integrations` with the
   `dcr_immutable_ids` map populated.
