# Welcome to Microsoft Sentinel Training Lab

<p align="center">
<img src="./Images/sentinel-labs-logo.png?raw=true">
</p>

## Introduction
These labs help you get ramped up with Microsoft Sentinel and provide hands-on practical experience for product features, capabilities, and scenarios. 

The lab deploys an Microsoft Sentinel workspace and ingests pre-recorded data to simulate scenarios that showcase various Microsoft Sentinel features. You should expect very little or no cost at all due to the size of the data (~10 MBs) and the fact that Microsoft Sentinel offers a 30-day free trial.

## Prerequisites

To deploy Microsoft Sentinel Trainig Lab, **you must have a Microsoft Azure subscription**. If you do not have an existing Azure subscription, you can sign up for a free trial [here](https://azure.microsoft.com/free/).

## Last release notes

* Version 1.0 - Microsoft Sentinel Training Lab 

## Getting started

Below you can see all the [modules](#Modules) that are part of this lab. Although in general they can be completed in any order, you must start with [Module 1](./Modules/Module-1-Setting-up-the-environment.md) as this deploys the lab environment itself.

## Modules

[**Module 1 – Setting up the environment**](./Modules/Module-1-Setting-up-the-environment.md)
- [The Microsoft Sentinel workspace](./Modules/Module-1-Setting-up-the-environment.md#exercise-1-the-azure-sentinel-workspace)
- [Deploy the Microsoft Sentinel Training Lab Solution](./Modules/Module-1-Setting-up-the-environment.md#exercise-2-deploy-the-azure-sentinel-training-lab-solution)
- [Configure Microsoft Sentinel Playbook](./Modules/Module-1-Setting-up-the-environment.md#exercise-3-configure-azure-sentinel-playbook)
 
[**Module 2 – Data Connectors**](./Modules/Module-2-Data-Connectors.md)
- [Enable Azure Activity data connector](./Modules/Module-2-Data-Connectors.md#exercise-1-enable-azure-activity-data-connector)
- [Enable Azure Defender data connector](./Modules/Module-2-Data-Connectors.md#exercise-2-enable-azure-defender-data-connector)
- [Enable Threat Intelligence TAXII data connector](./Modules/Module-2-Data-Connectors.md#exercise-3-enable-threat-intelligence-taxii-data-connector)

[**Module 3 – Analytics Rules**](./Modules/Module-3-Analytics-Rules.md)
- [Analytics Rules overview](./Modules/Module-3-Analytics-Rules.md#exercise-1-analytics-rules-overview)
- [Enable Microsoft incident creation rule](./Modules/Module-3-Analytics-Rules.md#exercise-2-enable-microsoft-incident-creation-rule)
- [Review Fusion Rule (Advanced Multistage Attack Detection)](./Modules/Module-3-Analytics-Rules.md#exercise-3-review-fusion-rule-advanced-multistage-attack-detection)
- [Create custom analytics rule](./Modules/Module-3-Analytics-Rules.md#exercise-4-create-azure-sentinel-custom-analytics-rule)
- [Review resulting security incident](./Modules/Module-3-Analytics-Rules.md#exercise-5-review-resulting-security-incident)

[**Module 4 – Incident Management**](./Modules/Module-4-Incident-Management.md)
- [Review Microsoft Sentinel incident tools and capabilities](./Modules/Module-4-Incident-Management.md#exercise-1-review-azure-sentinel-incident-tools-and-capabilities)
- [Handling Incident "Sign-ins from IPs that attempt sign-ins to disabled accounts"](./Modules/Module-4-Incident-Management.md#exercise-2-handling-incident-sign-ins-from-ips-that-attempt-sign-ins-to-disabled-accounts)
- [Handling "Solorigate Network Beacon" incident](./Modules/Module-4-Incident-Management.md#exercise-3-Handling-solorigate-network-beacon-incident)
- [Hunting for more evidence](./Modules/Module-4-Incident-Management.md#exercise-4-Hunting-for-more-evidence)
- [Add IOC to Threat Intelligence](./Modules/Module-4-Incident-Management.md#exercise-5-Add-IOC-to-Threat-Intelligence)
- [Handover incident](./Modules/Module-4-Incident-Management.md#exercise-6-Handover-incident)
 
[**Module 5 – Hunting**](./Modules/Module-5-Hunting.md)
- [Hunting on a specific MITRE technique](./Modules/Module-5-Hunting.md#exercise-1-Hunting-on-a-specific-MITRE-technique)
- [Bookmarking hunting query results](./Modules/Module-5-Hunting.md#exercise-2-Bookmarking-hunting-query-results)
- [Promote a bookmark to an incident](./Modules/Module-5-Hunting.md#exercise-3-Promote-a-bookmark-to-an-incident)

[**Module 6 – Watchlists**](./Modules/Module-6-Watchlists.md)
- [Create a Watchlist](./Modules/Module-6-Watchlists.md#exercise-1-create-a-watchlist)
- [Whitelist IP addresses in the analytics rule](./Modules/Module-6-Watchlists.md#exercise-2-whitelist-ip-addresses-in-the-analytics-rule)

[**Module 7 - Threat Intelligence**](./Modules/Module-7-Threat-Intelligence.md)
- [Threat Intelligence data connectors](./Modules/Module-7-Threat-Intelligence.md#exercise-1-threat-intelligence-data-connectors)
- [Explore the Threat Intelligence menu](./Modules/Module-7-Threat-Intelligence.md#exercise-2-explore-the-threat-intelligence-menu)
- [Analytics Rules based on Threat Intelligence data](./Modules/Module-7-Threat-Intelligence.md#exercise-3-analytics-rules-based-on-threat-intelligence-data)
- [Threat Intelligence Workbook](./Modules/Module-7-Threat-Intelligence.md#exercise-5-threat-intelligence-workbook)

[**Module 8 - Microsoft Sentinel Content hub**](./Modules/Module-8-Azure-Sentinel-Solutions.md)
- [Explore Microsoft Sentinel Content hub](./Modules/Module-8-Azure-Sentinel-Solutions.md#exercise-1-explore-azure-sentinel-content-hub)
- [Deploy a new solution](./Modules/Module-8-Azure-Sentinel-Solutions.md#exercise-2-deploy-a-new-solution)
- [Review and enable deployed artifacts](./Modules/Module-8-Azure-Sentinel-Solutions.md#exercise-3-review-and-enable-deployed-artifacts)
