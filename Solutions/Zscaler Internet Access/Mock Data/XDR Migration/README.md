# Zscaler Internet Access migration mock

`DiscordCDNRiskyDownload.json` contains one allowed synthetic download of an
executable from a Discord CDN attachment URL. It validates `Discord CDN Risky
File Download`.

The record follows the raw `Custom-nss_web_CL` stream contract, not the
`CommonSecurityLog` destination schema. Ingest it only into a non-production
lab through a DCR using the authoritative connector transform. Refresh
`TimeGenerated` when validating a rule with a short lookback.
