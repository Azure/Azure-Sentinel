# NetApp Ransomware Resilience Enrich IP Playbook

## Overview
This playbook enriches IP address information by retrieving detailed network interface data from the NetApp Ransomware Resilience API. It helps you investigate network-related security incidents by providing context about storage network interfaces.

## Purpose
When investigating a security incident involving a suspicious IP address, this playbook retrieves detailed information about the network interface from your NetApp storage systems, including associated volumes, storage VMs, and access patterns.

## Deployment Order
**This playbook should be deployed THIRD**, after:
1. ✅ Auth Playbook (required)
2. ✅ Async Poll Playbook (required)

## What It Does
- Accepts an IP address as input
- Retrieves authentication from the Auth Playbook
- Queries the NetApp API for network interface details associated with that IP
- Polls asynchronously for the enrichment results
- Returns detailed network interface information including:
  - Network interface configuration
  - Associated storage VMs
  - Connected volumes
  - Access policies and protocols

## Prerequisites
Before deploying this playbook:
1. Auth Playbook must be deployed and functioning correctly
2. Async Poll Playbook must be deployed and functioning correctly
3. Valid NetApp API credentials configured

## How to Use
This playbook can be:
- Called manually with an IP address to investigate
- Integrated into automation rules triggered by Microsoft Sentinel alerts
- Chained with other playbooks in your incident response workflow
- Combined with Volume Snapshot or Volume Offline playbooks for remediation

**Input Required:**
- `ip_address`: The IP address you want to investigate

## Use Case Example
When you receive an alert about suspicious activity from an IP address:
1. This playbook enriches the IP with NetApp storage context
2. You identify which storage VM and volumes are exposed
3. Based on the findings, you can take protective actions using other playbooks

## Post-Deployment Configuration
After deploying this playbook:
1. Test with a known valid IP address from your NetApp environment
2. Verify the enrichment data is returned correctly
3. Consider integrating it into your incident response automation rules

## Building Custom Workflows
This enrichment playbook is a building block. You can combine it with other playbooks to create complete incident response workflows. For example:
- Enrich IP → Identify volume → Take snapshot → Take volume offline

## Need Help?
If enrichment isn't working, verify:
- The Auth Playbook is returning valid tokens
- The Async Poll Playbook is functioning correctly
- The IP address exists in your NetApp environment
- Your NetApp API endpoint is accessible
