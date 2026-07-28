# PRODAFT USTA - Account Takeover Prevention — Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.0       | 06-07-2026                     | Initial Solution Release. Codeless (CCF) data connector for compromised-credential tickets with ingestion-time password redaction (only strength signals are stored). Two **Analytic Rules** (corporate credential compromised; compromised credential used in a successful Entra ID sign-in), one **Hunting Query**, an overview **Workbook**, a query-time dedup **Parser**, and an on-demand backfill **Playbook** (Logs Ingestion API via managed identity) for loading historical data. |
