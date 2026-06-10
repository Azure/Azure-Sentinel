# Documentation

Welcome! This folder explains the **Trend Vision One → Microsoft Sentinel data connectors** in plain language — no prior Azure or Sentinel experience assumed.

The goal of these docs is simple: **anyone, from a first-day analyst to a veteran cloud engineer, should be able to read a page and understand not just *what* to click, but *why*.** If a page ever assumes knowledge you don't have, that's a bug in the docs — please open an issue.

## Start here

Read these in order if you're new:

| # | Guide | Read this if you want to… |
|---|-------|---------------------------|
| 1 | [Concepts — how it all fits together](01-concepts.md) | Understand *what* this is and *why* it's built the way it is, in everyday terms. |
| 2 | [Permissions you need (and why)](02-permissions.md) | Know exactly which Azure and Trend Vision One permissions are required, and *why* each one is needed, before you ask IT for access. |
| 3 | [Deploying the connector](03-deployment.md) | Install a connector, step by step, with screenshots-worth of detail. |
| 4 | [Using the connector day to day](04-using-the-connector.md) | Verify data is flowing, write queries, turn on alerts, and read the dashboards. |
| 5 | [Migrating from the old connector](05-migration.md) | Move off the old Azure Function based "Trend Vision One" connector onto this one — safely, without losing data. |
| 6 | [Troubleshooting](06-troubleshooting.md) | Fix the common "no data / connection failed" problems. |

## Quick links by role

- **"I just need it installed."** → [Deploying the connector](03-deployment.md)
- **"I have to request access first."** → [Permissions you need](02-permissions.md)
- **"We already use the old Trend Micro connector."** → [Migration guide](05-migration.md)
- **"Data isn't showing up."** → [Troubleshooting](06-troubleshooting.md)
- **"I'm a maintainer / Trend internal."** → [Internal test-deploy notes](internal/test-deploy.md)

## A note on the two connectors

There are **two** connectors in this repository. They are independent — you can install one, the other, or both.

- **Workbench Alerts** — the curated security incidents Trend Vision One has already correlated for you ("here is a thing worth looking at"). Medium data volume.
- **OAT (Observed Attack Techniques)** — the raw, high-volume stream of individual MITRE ATT&CK-mapped detections ("here is every suspicious technique we saw"). High data volume.

[Concepts](01-concepts.md#workbench-vs-oat-which-one-do-i-want) explains the difference in more detail and helps you choose.

---

*These docs describe version 2.x of the connectors. Last reviewed: June 2026.*
