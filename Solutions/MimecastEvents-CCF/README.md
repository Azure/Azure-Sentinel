# Mimecast Events (CCF Push) for Microsoft Sentinel

Ingests Mimecast Secure Email Gateway (SEG/CG), Targeted Threat Protection
(URL / Attachment / Impersonation), DLP and Audit events via **Mimecast Event
Push** → **Azure Monitor Logs Ingestion API**, packaged as a V3 Content Hub
solution using the Codeless Connector Framework (**Push** — no RestApiPoller).

**No Mimecast credentials are stored in Sentinel.** The Deploy button provisions
a DCE, DCR, the `MimecastEvents_CL` table and a Microsoft Entra application;
those connection values are entered on the Mimecast side (Integrations Hub →
Event Push, OAuth 2.0 client credentials).

## Architecture

```
Mimecast Event Push ──HTTPS POST (Bearer via Entra app)──▶ DCE
  token: login.microsoftonline.com/<tenant>/oauth2/v2.0/token
  scope: https://monitor.azure.com/.default                 │
                                                            ▼
                                       DCR transformKql ──▶ MimecastEvents_CL
                                                            │
                     Parsers: MimecastEvents (dedup base), MimecastCG,
                     MimecastAudit, MimecastTTPUrl, MimecastTTPImpersonation,
                     MimecastTTPAttachment, MimecastDLP
```

## Design (evidence-based)

Derived from the legacy Function App tables' real schemas and sanitized samples:

- **Single dynamic stream column** `mimecast_body`; everything extracted in the
  transform. Table stores the full payload as string plus promoted columns
  (`mimecastEventType`, `mimecastEventId`, `mimecastLogtype`, `mimecastSubtype`).
- **Derived discriminator** (records carry no uniform type field). Order:
  `auditType` → audit; `impersonationResults` → ttp_impersonation;
  `Logtype == email_ttp_ap` → email_ttp_ap; `Logtype == seg_dlp` → seg_dlp;
  any `Logtype` → seg_cg; attachment shape (`fileHash`/`sha256`) → ttp_attachment
  (checked BEFORE `url`); `url` → ttp_url; else unknown.
  Observed Logtype values: `email_receipt`, `email_process`, `email_spam`,
  `email_ttp_ap` (open enum).
- **Per-type timestamps**, 2-day clamp: `eventTime` ISO (Audit/Impersonation),
  `date` ISO+offset (TTP URL), `timestamp` epoch **milliseconds** (SEG —
  converted with `datetime(1970-01-01) + tolong(x) * 1ms`;
  `unixtime_milliseconds_todatetime()` deliberately avoided as unverified in the
  ingestion-time KQL subset).
- **Dedup keys** (read-time, `arg_max` in parsers): Audit/Impersonation → `id`;
  SEG → `processingId` (NOT `aggregateId`, which groups multiple rows);
  TTP URL → synthetic `hash_sha256(messageId|url|date)`.
- **Legacy compatibility**: per-type parsers project the legacy Function App
  column names so existing queries keep working against the views.

## Deployment & Mimecast configuration

1. Install the solution; open the connector page; click **Deploy**.
2. Copy the five values (Tenant ID, Client ID, Client secret, DCE URL, DCR
   immutable ID) into Mimecast Integrations Hub → Event Push (format JSON,
   OAuth 2.0 client credentials; token endpoint and scope as shown on the page).
3. Verify with `MimecastEvents_CL | take 10` and the parser views.

## Envelope-dependent items (verify with the first live events)

The record-level design is verified against real legacy data; the Event Push
**delivery envelope** is not yet observed. On first live data, check:

1. Whether events arrive wrapped as `{ "mimecast_body": { ... } }` per record.
   If Mimecast posts **bare event objects**, replace the stream declaration with
   explicit top-level columns (union of per-type fields) and drop the
   `mimecast_body.` prefix in the transform — the discriminator/timestamp/dedup
   logic is unchanged.
2. `eventsJsonPaths ["$"]` assumes a JSON **array** per POST; if events are
   wrapped (`{"events": [...]}`), change to `["$.events[*]"]`.
3. Key casing (`Logtype` vs `logType`) — run:
   `MimecastEvents_CL | take 1 | project mimecast_body` and inspect raw keys.
4. Payload size: Logs Ingestion API caps ~1MB/request; watch Mimecast Event
   Push error/paused states on busy tenants.

### Synthetic end-to-end test (no Mimecast needed)

```powershell
$token = (Get-AzAccessToken -ResourceUrl "https://monitor.azure.com").Token
$body  = Get-Content ".\Sample Data\MimecastEvents_CL_seg_cg.json" -Raw
Invoke-RestMethod -Method Post `
  -Uri "https://<dce>.ingest.monitor.azure.com/dataCollectionRules/<dcr-immutable-id>/streams/Custom-MimecastEvents_CL?api-version=2023-01-01" `
  -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $body
```

Then: `MimecastEvents_CL | summarize count() by mimecastEventType` and check the
parser views. (Un-defang `hxxps://` → `https://` in test payloads first if you
want URL fields realistic; keep repo sample files defanged.)

## Validation & packaging

```powershell
# local CI gate (if the clone has the runner)
pwsh .script/local-validation/build-and-validate.ps1 -SolutionName "MimecastEvents-CCF" -SkipPackaging
# package
pwsh Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1
```

Update `BasePath` in `Data/Solution_MimecastEvents-CCF.json` to your clone path
before packaging. Expected arm-ttk state: all pass except the documented
`IDs Should Be Derived From ResourceIDs` false positive on auto-generated
content-metadata ids.
