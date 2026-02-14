# NetApp Ransomware Resilience Enrich StorageVM Playbook

## Overview
This playbook enriches storage information by retrieving detailed configuration and status data for NetApp Storage Virtual Machines (SVMs). It provides valuable context when investigating incidents involving your NetApp storage infrastructure.

## Purpose
When investigating a security incident, this playbook helps you understand the storage environment by retrieving detailed information about Storage VMs, including their volumes, security settings, and current operational status.

## Deployment Order
**This playbook should be deployed FOURTH**, after:
1. ✅ Auth Playbook (required)
2. ✅ Async Poll Playbook (required)
3. ✅ Enrich IP Playbook (optional, recommended)

## What It Does
- Accepts agent ID and system ID as input
- Retrieves authentication from the Auth Playbook
- Queries the NetApp API for Storage VM details
- Returns comprehensive storage configuration information including:
  - Storage VM configuration and status
  - Associated volumes and their states
  - Security and protocol settings
  - Network interface configurations
  - Access policies

## Prerequisites
Before deploying this playbook:
1. Auth Playbook must be deployed and functioning correctly
2. Valid NetApp API credentials configured

## How to Use
This playbook can be:
- Called manually with agent ID and system ID to investigate storage configurations
- Triggered automatically as part of incident response workflows
- Combined with other playbooks to create comprehensive response actions
- Used to gather context before taking protective actions

**Input Required:**
- `agent_id`: The NetApp agent identifier
- `system_id`: The NetApp system identifier

## Use Case Example
When investigating a potential ransomware incident:
1. Use this playbook to retrieve Storage VM details
2. Identify all volumes and their current states
3. Assess which volumes may be at risk
4. Use Volume Snapshot playbook to protect critical data
5. Use Volume Offline playbook to isolate compromised volumes

## Post-Deployment Configuration
After deploying this playbook:
1. Test with valid agent ID and system ID from your NetApp environment
2. Verify the storage enrichment data is returned correctly
3. Consider integrating it into your security automation workflows

## Building Custom Workflows
This enrichment playbook is designed as a building block. Combine it with action playbooks to create complete incident response solutions:
- Enrich StorageVM → Identify critical volumes → Take snapshots → Take volumes offline if needed

## Need Help?
If enrichment isn't working, verify:
- The Auth Playbook is returning valid tokens
- The agent ID and system ID are correct and active
- Your NetApp API endpoint is accessible
- The Storage VM exists in your NetApp environment
