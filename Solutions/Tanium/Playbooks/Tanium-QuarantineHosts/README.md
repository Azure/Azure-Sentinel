# Tanium-QuarantineHosts

## Overview
This playbook will tell Tanium to quarantine the machine(s) in question for any incidents in Microsoft Sentinel. It will add the status of the quarantine as a comment inside the incident. This is intended to run against any incident in Microsoft Sentinel that was generated from the "Tanium Threat Response Alerts" analytic rule.

## Prerequisites
Alerts from Tanium Threat Response will not trigger an incident in Microsoft Sentinel without "Tanium Threat Response Alerts" analytic rule. Without this rule, this playbook will not have the desired effect.

## Post-Deployment Instructions
After deploying the playbook, you must authorize the connections leveraged.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the left), click "API Connections".
3. Ensure each connection has been authorized.
