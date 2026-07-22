# PRODAFT USTA - Payment Card Fraud Intelligence - Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.0       | 08-07-2026                     | Initial Solution Release. Codeless (CCF) data connector for compromised payment-card tickets with ingestion-time PAN redaction (only BIN, last 4 digits, brand, and length are stored). Two **Analytic Rules** (payment card exposed; non-expired payment card exposed), one **Hunting Query**, an overview **Workbook**, a query-time dedup **Parser**, and an on-demand backfill **Playbook** (Logs Ingestion API via managed identity) for loading historical data. |
