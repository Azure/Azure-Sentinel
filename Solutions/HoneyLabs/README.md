# HoneyLabs for Microsoft Sentinel

[HoneyLabs](https://honeylabs.net) runs internet-facing honeypot sensors and publishes the
resulting indicators over TAXII 2.1. Every indicator is evidence-backed: the IP ran an exploit
or loader command against a sensor, or the URL was extracted from a payload those commands
fetched. Known research scanners are excluded, and indicators expire on their own as activity
stops.

## How ingestion works

This solution does not ship a data connector. Indicators arrive through Microsoft Sentinel's
built-in **Threat Intelligence - TAXII** connector, which polls the HoneyLabs TAXII server and
writes into the `ThreatIntelIndicators` table. The solution provides the content that sits on
top of that: a workbook, four analytic rules, four hunting queries and an enrichment playbook.

A free HoneyLabs API key is the only prerequisite.

## Setup

1. Create an API key at [honeylabs.net/dashboard](https://honeylabs.net/dashboard?src=sentinel).
   Accounts are free. The key is the password for the TAXII server.
2. If your workspace does not have the **Threat Intelligence - TAXII** connector, install the
   **Threat Intelligence** solution by Microsoft from the Content hub.
3. Open that connector, choose **Add**, and enter:

   | Field | Value |
   |---|---|
   | Friendly name | HoneyLabs |
   | API root URL | `https://honeylabs.net/taxii2/api/` |
   | Collection ID | `019bc26f-7216-562c-b110-16ccd9c553f6` |
   | Username | `taxii` |
   | Password | your HoneyLabs API key |
   | Polling frequency | hourly |

4. Optionally add a second entry for malware infrastructure, the loader and command-and-control
   URLs pulled out of captured payloads. Same API root URL and credentials, collection ID
   `e144c129-a19a-55c8-b926-dd2dfbbd8138`. It is a smaller and different signal from the
   attacker IPs and is kept separate so it does not dilute them.

Indicators appear in the **Threat intelligence** blade within a few minutes of the first poll,
with `SourceSystem` starting `HoneyLabs`. Until they do, the workbook shows these same steps in
place of its charts.

## What ships

| Item | Purpose |
|---|---|
| HoneyLabs Threat Intelligence workbook | Indicator volume and freshness, confidence bands, source ASN and country, probed CVEs, and matches against your own logs |
| 4 analytic rules | Match indicators against CommonSecurityLog, ASIM network sessions and sign-in logs |
| 4 hunting queries | First contact with high-confidence indicators, CVE prober contact, loader URL contact, and repeated contact across hosts |
| Enrich Incident - IP playbook | Adds the full HoneyLabs report for any IP entity to the incident as a comment |

## Fields on each indicator

`Confidence` grades the evidence behind an indicator: 90 means 100 or more observed attacks, 60
means a single sighting. It is there so you can pick an alerting threshold rather than mute the
feed. Labels carry the source network (`asn:ASxxxx`), origin (`country:XX`) and the indicator
kind. On paid plans the attacker-IP collection also carries CVE probers, each labelled with the
CVE ids that source went after, and the query window extends from 7 to 30 days.

Every indicator links back to its full report at `honeylabs.net/lookup`: first seen, the exact
requests, captured payloads and client fingerprints.

## Support

Community supported by HoneyLabs. Open an issue at
[honeylabs.net](https://honeylabs.net) or mail info@honeylabs.net.

- [Integration guide](https://honeylabs.net/integrations/sentinel)
- [Methodology](https://honeylabs.net/methodology)
