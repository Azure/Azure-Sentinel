# Truvizy Threat Intelligence for Microsoft Sentinel

[Truvizy](https://truvizy.app) detects online scams: phishing sites, fraudulent investment pages, deepfake-driven fraud campaigns and social-engineering lures. This solution brings the scam and phishing indicators confirmed by the Truvizy detection network into Microsoft Sentinel as STIX 2.1 indicators, delivered over TAXII 2.1.

## What the feed contains

- **URL indicators**: dedicated scam and phishing pages confirmed by Truvizy.
- **Domain indicators**: dedicated scam domains. Shared platforms (youtube.com, hosting providers, link shorteners) are never listed at the domain level, so the feed is safe to use for blocking.
- Every indicator carries a confidence score (only 70+ is published) and an expiration date, so stale indicators age out automatically.
- No personal data is ever included.

## Contents of this solution

| Content | Name |
| --- | --- |
| Data connector | Truvizy Threat Intelligence (TAXII) |
| Analytics rule | Truvizy TI map URL indicator to CommonSecurityLog |
| Analytics rule | Truvizy TI map domain indicator to DnsEvents |
| Hunting query | Truvizy active indicator overview |

## Getting access

Feed credentials (TAXII username and password) are issued by the Truvizy team during onboarding. Contact [Truvizy support](https://truvizy.app/support) or email support@truvizy.app to request access.

## Connection parameters

- **API root URL**: `https://taxii.truvizy.app/api/`
- **Collection ID**: `b7c1d2e0-5a4f-4c8e-9d3a-2f6b8c1e7a90`
- **Friendly name**: use `Truvizy` (the analytics rules in this solution filter on it)
- **Polling**: once per hour recommended
