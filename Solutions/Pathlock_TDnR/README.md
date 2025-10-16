# Pathlock TDnR – Microsoft Sentinel CCP Push Connector

This package contains a content-hub–style connector for ingesting Pathlock TDnR events into Microsoft Sentinel using a Data Collection Endpoint (DCE) and Data Collection Rule (DCR).

## Stream and table
- **Stream name:** `Custom-Pathlock_TDnR_CL`
- **Table name:** `Pathlock_TDnR_CL`

## Required values to configure in Pathlock
- Tenant ID
- Client (Application) ID
- Client Secret
- **DCE URL**
- **DCR Immutable ID**
- **Stream ID:** `Custom-Pathlock_TDnR_CL`

## Logs Ingestion endpoint
```
POST {DCE-URL}/dataCollectionRules/{DCR-IMMUTABLE-ID}/streams/Custom-Pathlock_TDnR_CL/ingest?api-version=2023-01-01
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Sample payload record
Matches the schema derived from your sample file and will be transformed so `TimeGenerated` is used as the event time.
A copy of `TenantId` and `SourceSystem` is kept as `TenantIdPayload` and `SourceSystemPayload` to avoid column collisions.

## Quick test (curl)
```
curl -X POST "https://<your-dce-host>/dataCollectionRules/<dcr-id>/streams/Custom-Pathlock_TDnR_CL/ingest?api-version=2023-01-01" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"records":[{"TimeGenerated":"2025-10-15T19:03:45Z","AlertSeverityText":"Low","User":"DDIC","AbapProgramName":"R_TEST","ClientId":"800"}]}'
```

## KQL sanity checks
```kusto
Pathlock_TDnR_CL
| summarize Last = max(TimeGenerated)

Pathlock_TDnR_CL
| summarize count() by AlertSeverityText
| order by count_ desc

Pathlock_TDnR_CL
| summarize Events = count() by AbapProgramName
| top 10 by Events desc
```
