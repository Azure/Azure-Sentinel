# NetApp Ransomware Resilience - Block User

## Overview

This playbook helps security teams block user access as part of incident response in NetApp Ransomware Resilience.

## Purpose

Use this playbook when you need a controlled way to block a user based on investigation findings, suspicious behavior, or containment actions.

## Deployment Order

This playbook should be deployed after:

1. Auth Playbook (required)

### Input Parameters

- `user_id`: User ID to block (required)
- `user_ips`: Client IPs to block (required for NFS; optional for CIFS)
- `duration`: Block duration - `permanent` or hours (`1`, `2`, `4`, `8`, `12`, `24`) (optional)

### Prerequisites

1. Auth Playbook must be deployed and functioning correctly.
2. Valid NetApp Ransomware Resilience configuration must be completed.
3. The playbook caller must provide `user_id`, and optionally `user_ips`/`duration` based on the protection scenario.

### Deployment instructions

1. Click the Deploy to Azure button. This opens the ARM template deployment wizard.
2. Provide the required parameters:
   - `PlaybookName`: Name of this playbook resource.
   - `NetAppRansomwareResilienceAuthPlaybookName`: Name of the deployed NetApp Auth playbook.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNetApp%2520Ransomware%2520Resilience%2FPlaybooks%2FNetApp-RansomwareResilience_Block_User_Playbook%2Fazuredeploy.json)

[![Deploy to Azure US Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNetApp%2520Ransomware%2520Resilience%2FPlaybooks%2FNetApp-RansomwareResilience_Block_User_Playbook%2Fazuredeploy.json)

### Post-Deployment

#### 1. Validate dependency configuration

1. Confirm the Auth playbook is deployed in the same environment.
2. Ensure the `NetAppRansomwareResilienceAuthPlaybookName` parameter matches the deployed Auth playbook name.

#### 2. Functional validation

1. Run the Block User playbook with a valid payload.
2. Verify the expected block action is applied for the target user.
3. Validate behavior with and without optional inputs (`user_ips`, `duration`).

#### 3. Microsoft Sentinel usage

1. Add this playbook to an automation rule or run it manually from an incident.
2. Pass required entities/details as playbook input (`user_id`, and optional `user_ips`/`duration`).
