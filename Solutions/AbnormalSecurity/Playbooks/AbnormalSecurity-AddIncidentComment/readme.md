# Abnormal Security - Add Incident Comment

This playbook is triggered when a Microsoft Sentinel incident is created. It adds a comment to the
incident summarizing the Abnormal Security alert (provider, severity, title) so analysts have Abnormal
context inline.

It uses only the Microsoft Sentinel connector with a system-assigned managed identity and requires no
third-party credentials.

## Quick Deployment

After deployment:

1. Assign the **Microsoft Sentinel Responder** role to the playbook's managed identity on the resource
   group or workspace.
2. Create an **Automation Rule** that runs this playbook on incidents created by the Abnormal Security
   analytic rules.

## Prerequisites

None beyond a Microsoft Sentinel-enabled Log Analytics workspace and the role assignment above.
