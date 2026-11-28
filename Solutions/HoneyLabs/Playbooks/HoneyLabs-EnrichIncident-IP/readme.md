# HoneyLabs-EnrichIncident-IP

Enriches Microsoft Sentinel incidents with HoneyLabs honeypot intelligence.

For every IP entity on a new incident, the playbook queries the HoneyLabs
lookup API (`https://honeylabs.net/lookup/<ip>?format=json`) and adds a
comment with:

- the verdict (exploitation, scanning, probing, or recognized research scanner)
  and its confidence,
- first-contact events and interactive sessions, each in total and in the
  last 7 days,
- first seen and last seen timestamps,
- a link to the full report (payloads, CVEs probed, ports, fingerprints).

It also tags the incident `HoneyLabs: <verdict>` and raises a Low, Medium or
Informational incident to High when the verdict is malicious. An address
HoneyLabs has never seen gets no comment.

## Prerequisites

- A HoneyLabs API key, created free at
  [honeylabs.net/dashboard?src=sentinel](https://honeylabs.net/dashboard?src=sentinel) under API keys.
  Lookup calls are metered against the key's daily credit quota.

## Post-deployment

1. Grant the playbook's system-assigned managed identity the **Microsoft
   Sentinel Responder** role on the resource group.
2. Attach the playbook to an automation rule that fires on incident creation
   for incidents with IP entities.
