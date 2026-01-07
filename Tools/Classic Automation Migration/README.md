# Classic Automation Detection Tool

**Author:** Sagi Yagen

## Overview

As Microsoft Sentinel approaches the deprecation of classic automation, this tool helps you quickly identify analytic rules that still use classic alert-trigger playbooks and need to be migrated to automation rules.

This tool contains two ARM template-based Logic Apps that scan your environment and provide a complete list of impacted analytic rules requiring migration.

> **Learn more:** [Migrate your Microsoft Sentinel alert-trigger playbooks to automation rules](https://learn.microsoft.com/en-us/azure/sentinel/automation/migrate-playbooks-to-automation-rules)

---

## Available Solutions

### 1. Subscription-Level Detection (Recommended)

**Permissions granted to the Logic App:**
- `Reader` (subscription scope)
- `Sentinel Reader` (subscription scope)

**Deployment requirement:** User must have `Owner` role on the subscription

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FClassic%20Automation%20Migration%2FClassic%20Automation%20Detect%20-%20Subscription%20Deployment%20(Prod).json)

---

### 2. Workspace-Level Detection

**Permissions granted to the Logic App:**
- `Sentinel Reader` (workspace scope)

**Deployment requirement:** User must have `Owner` role on the workspace

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FClassic%20Automation%20Migration%2FClassic%20Automation%20Detect%20-%20Workspace%20level%20(Prod).json)

---

## When to Use Each Version

| Scenario | Recommended Version |
|----------|---------------------|
| Multiple workspaces across a subscription | **Subscription-Level** |
| Enterprise-wide scan | **Subscription-Level** |
| Single workspace environment | **Workspace-Level** |
| No subscription Owner permissions | **Workspace-Level** |
| Want minimal permission scope | **Workspace-Level** |
| Need to scan multiple workspaces without subscription permissions | **Workspace-Level** (deploy per workspace) |

---

## Understanding the Output

After running the Logic App, navigate to the run history and locate the final action: **"Impacted_Analytic_Rules_List_"**

This action returns a list of analytic rules that still use classic automation:

```json
[
  {
    "WorkspaceName": "YourSentinelWorkspace",
    "AnalyticRuleName": "Suspicious Login Activity",
    "RuleId": "12345678-1234-1234-1234-123456789abc",
    "Enabled": true
  }
]
```

### 🚨 If you have results, you need to take action!

Each rule listed requires migration from classic automation to automation rules. Follow this simple step-by-step guide to perform the migration:

👉 **[Migration Guide: Classic Automation to Automation Rules](https://learn.microsoft.com/en-us/azure/sentinel/automation/migrate-playbooks-to-automation-rules)**

The migration typically takes 2-3 steps per rule and ensures your automations continue working after classic automation is deprecated.

---

## FAQ

### Can I run this multiple times?
Yes! The Logic App is non-destructive and only reads configuration data. You can run it as many times as needed.

### Will this modify my analytic rules?
No. This tool only **detects** and **reports** on analytic rules. It does not make any changes to your environment.

### What if I have hundreds of analytic rules?
The Logic App is designed to handle large environments. It processes workspaces and rules iteratively and returns all results in a single output.

### Can I customize the recurrence schedule?
Yes. After deployment, you can modify the Logic App trigger to run on any schedule you prefer, or disable the recurrence entirely and run it manually only.

### Do I need to keep the Logic App after migration?
Once you've completed all migrations, you can safely delete the Logic App. However, you may want to keep it to periodically verify that no new classic automations are added.

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Type:** Community Solution

---

> **⚠️ Disclaimer:** This is a community-contributed tool designed to assist with the migration from classic automation to automation rules. While created to help Microsoft Sentinel customers, this is not an official Microsoft product. Use at your own discretion and test in a non-production environment first.
