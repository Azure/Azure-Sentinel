# Azure Cognitive Search

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cognitive%20Search](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cognitive%20Search) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Cognitive Search](../connectors/azurecognitivesearch-ccp.md)

**Publisher:** Microsoft

Azure Cognitive Search is a cloud search service that gives developers infrastructure, APIs, and tools for building a rich search experience over private, heterogeneous content in web, mobile, and enterprise applications. This connector lets you stream your Azure Cognitive Search diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Policy**: owner role assigned for each policy assignment scope

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Cognitive Search diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure Cognitive Search log-streaming configuration to a collection of instances, defined as a scope. Follow the instructions below to create and apply a policy to all current and future instances. Note, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Cognitive Search at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureCognitiveSearch_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Cognitive%20Search/Data%20Connectors/AzureCognitiveSearch_CCP.JSON) |

[→ View full connector details](../connectors/azurecognitivesearch-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Cognitive Search](../connectors/azurecognitivesearch-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
