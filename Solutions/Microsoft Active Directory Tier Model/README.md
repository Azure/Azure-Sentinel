# Overview
---
## Microsoft Sentinel: Microsoft Active Directory Tier Model Solution

The **Microsoft Active Directory Tier Model** solution for Microsoft Sentinel provides detection, triage automation, and reporting for the Active Directory (AD) administrative tier model - Tier 0 (T0), Tier 1 (T1), and Tier 2 (T2) - across Active Directory Domain Services (AD DS / ADDS). It monitors tier-sensitive changes on Domain Controllers using Windows Security Event logs, tags and triages the resulting incidents with automation rules, and visualizes Tier Model activity in a workbook.

This solution contains:

- **19 Analytic rule templates** (TM001 - TM019)
- **1 Workbook** (Microsoft Active Directory Tier Model)
- **5 Automation rules** (deployed separately - see [Deploying the Automation Rules](#deploying-the-automation-rules))

## Try on Portal

You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Active%2520Directory%2520Tier%2520Model%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoft%2520Active%2520Directory%2520Tier%2520Model%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Active%20Directory%20Tier%20Model/Workbooks/Images/Preview/MicrosoftADTierModelWhite.png?raw=true)

## Getting Started

This solution **monitors an existing Active Directory Tier Model deployment**. Without the Tier Model deployed, the analytic rules will not match any activity and the solution provides no value. The rules key off the standard Tier 0 / Tier 1 / Tier 2 organizational unit (OU) structure (for example `OU=Tier 0 Accounts`, `OU=Tier 1 Member Servers`, `OU=Tier 0 PAW`, `OU=Tier 0 Groups`).

> **Important - do not rename the default rule names.** The analytic rules, automation rules, and workbook are tied together by the rule **names**. Each analytic rule stamps its alert title with a `(TMxxx.1)` identifier (for example `(TM002.1)`), and that identifier is the shared key across all three components:
>
> - The **automation rules** match incidents by the `(TMxxx.1)` title tag to apply tagging, severity changes, and closures.
> - The **workbook** filters and groups Tier Model incidents by these alert names.
>
> Because the analytic rule number, the automation rule, and the alert name are all linked, **renaming or modifying the default names will break the automation rules and the workbook.** Keep the default names as shipped. If you must customize a rule, preserve its `(TMxxx.1)` prefix so the dependencies continue to function.

### Prerequisites

1. **Active Directory Tier Model deployed.** Deploy and audit the Tier Model using the [Microsoft Active Directory Tier Model project](https://github.com/microsoft/ActiveDirectoryTierModel/) and its [documentation](https://microsoft.github.io/ActiveDirectoryTierModel/). If your OU names differ from the standard structure, adjust the analytic rule queries to match your environment.
2. **Domain Controller telemetry.** All Domain Controllers must run as Azure virtual machines or be onboarded to [Azure Arc](https://learn.microsoft.com/azure/azure-arc/servers/overview), with a [Data Collection Rule (DCR)](https://learn.microsoft.com/azure/azure-monitor/agents/data-collection-rule-azure-monitor-agent) that collects **Security** event logs from **every** Domain Controller into the Microsoft Sentinel workspace. See [Windows Security Events via AMA](https://learn.microsoft.com/azure/sentinel/data-connectors/windows-security-events-via-ama).
3. **Automation rules deployed.** The automation rules are required for incident tagging, severity assignment, and the workbook to function correctly.

### Deploying the Automation Rules

Microsoft Sentinel automation rules are not part of the Content Hub solution package, so they are shipped as a separate ARM template that must be deployed as a **required** post-installation step. See [Automation Rules/README.md](Automation%20Rules/README.md) for the one-click **Deploy to Azure** button and details.

## Analytic Rules

The solution installs the following 19 analytic rule templates. After installing the solution, create and enable rules from these templates in the **Manage** solution view. Each rule's alert title is prefixed with a `(TMxxx.1)` tag, which the automation rules use to identify Tier Model incidents.

| Rule | Description |
|------|-------------|
| TM001 | GROUP - Added to Group Outside the Object Tier Level |
| TM002 | OBJECT - Created or Deleted a Tier Level Object |
| TM003 | OBJECT - Moved or Recovered a Tier Level Account |
| TM004 | OBJECT - Enabled, Disabled, Unlocked, or Password Reset of a Tier Level Object |
| TM005 | GPO - Linked, Unlinked, or Enforced at Tier Level OU |
| TM006 | ACL - Modified at Tier Level OU |
| TM007 | OU - Created or Deleted at Tier Level |
| TM008 | GPO - Linked, Unlinked, or Enforced at Root of Domain |
| TM009 | ACL - Modified at Root of the Domain |
| TM010 | BITLOCKER - Stored Bitlocker Recovery Key to Tier Level Computer Object |
| TM011 | LAPS - Tier Level Computer Object LAPS Password Expiration Time Set Manually |
| TM012 | GPO - Enforced Outside of Tier Model |
| TM013 | OU - Block Inheritance was Enabled on an OU |
| TM014 | GPO - Linked, Unlinked, or Enforced at the AD Site Level |
| TM015 | ACL - Modified at KRBTGT or AdminSDHolder Object Level |
| TM016 | GROUP - Added to Well-Known or Tier Model Group |
| TM017 | GROUP - Tier 0 Added to Allow RODC Password Replication Group |
| TM018 | DOMAIN - Child Domain promoted within the Forest |
| TM019 | TRUST - A new AD Trust has been established |

## Workbook

The **Microsoft Active Directory Tier Model** workbook provides a visual summary of incidents and alerts generated by the analytic rules, broken down by severity and status. It requires the analytic rules and automation rules to be active so that incidents are tagged and triaged correctly.

## Automation Rules

The solution's 5 automation rules run in order and match incidents by the `(TMxxx.1)` title tag (no analytic-rule IDs required, so they work in any workspace):

| Order | Rule | Action |
|-------|------|--------|
| 1 | **TM000 - Tagging** | Adds the `TIERMODEL` label to every Tier Model incident |
| 2 | **TM002 - Object created/deleted** | Closes (Informational) incidents where a user or computer object was deleted |
| 3 | **TM004 - Object state change** | Sets severity to Low for Tier 1 / Tier 2 / Disabled object changes |
| 4 | **TM007 - OU created/deleted** | Closes (Informational) non-Tier 0 OU create/delete activity |
| 5 | **TM010 - BitLocker key stored** | Closes (Informational) BitLocker recovery-key storage events |

## Support

This solution is supported by Microsoft. For issues with the Tier Model deployment framework itself, see the [Active Directory Tier Model project](https://github.com/microsoft/ActiveDirectoryTierModel/).
