# NetApp Ransomware Resilience Async Poll Playbook

## Overview
This playbook monitors the status of asynchronous NetApp operations by polling job status until completion or timeout. It acts as a helper playbook for operations that take time to complete.

## Purpose
When you perform actions like taking snapshots or taking volumes offline, these operations run asynchronously in the NetApp system. This playbook continuously checks the job status and notifies you when the operation completes, fails, or times out.

## Deployment Order
**This playbook MUST be deployed SECOND**, after:
1. ✅ Auth Playbook (required)

## What It Does
- Polls NetApp job status at regular intervals
- Monitors asynchronous operations until completion
- Handles timeout scenarios for long-running jobs
- Returns final job status to the calling playbook
- Provides operation results back to parent workflows

## Prerequisites
Before deploying this playbook:
1. The Auth Playbook must be successfully deployed and functioning
2. Valid NetApp API credentials configured in the Auth Playbook

## How It Works
1. Receives a job ID, agent ID, system ID, and source from a calling playbook
2. Requests an authentication token from the Auth Playbook
3. Polls the NetApp API for job status at regular intervals
4. Continues polling until the job completes, fails, or times out
5. Returns the final status to the calling playbook

## When Is This Used?
This playbook is automatically called by other action playbooks such as:
- Volume Snapshot Playbook
- Volume Offline Playbook
- Any other playbook that initiates asynchronous NetApp operations

You typically won't call this playbook directly—it's invoked automatically by other playbooks that need to wait for operation completion.

## Post-Deployment Configuration
After deploying this playbook:
1. Test it by triggering with a valid job ID from a NetApp operation
2. Monitor the run history to verify successful polling behavior
3. Adjust timeout settings if needed based on your environment

## Need Help?
If polling isn't working correctly, verify:
- The Auth Playbook is functioning and returning valid tokens
- The job ID being polled is valid and active
- Your NetApp API endpoint is accessible
