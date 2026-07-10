# Gambit Security Solution for Microsoft Sentinel

The Gambit Security solution ingests **policy issues** from [Gambit Security](https://gambit.security/) into Microsoft Sentinel using the Codeless Connector Framework (CCF) **Push** model.

## What it ingests

Gambit Security pushes each policy issue as an already-shaped record into the `GambitPoliciesIssues_CL` table. Every row is **denormalized** with the context needed to triage the issue without a join:

- **Resource context** — `ResourceDisplayId`, `ResourceType`, `HostPlatform`, `Environment`.
- **Affected systems** — `AffectedSystems` (array of system display names impacted by the issue).
- **Policy context** — `PolicyId`, `PolicyName`, `PolicyDescription`, `PolicyCategories`, `Severity`, `BusinessImpacts`, `RemediationSteps`.
- **Lifecycle** — `State` (Active / Resolved / Removed), `IssueStatus`, `CreatedAt`, `LastEvaluationTime`.

Records are append-only; each issue is re-emitted as its state changes. Gambit performs the field mapping, so the Data Collection Rule uses a pure passthrough transform (`transformKql: source`).

## Parser

`GambitPoliciesIssues` is a saved function that returns the latest row per issue:

```kusto
GambitPoliciesIssues_CL
| summarize arg_max(TimeGenerated, *) by IssueId
```

`IssueId` is the dedup key — always query through the `GambitPoliciesIssues` parser to see current issue state rather than the raw append-only table.

## Analytic rule

`Gambit Security - Critical Policy Issue Promotion` is a scheduled rule (1-day frequency/period) that promotes any **Active, High-severity** issue to a Microsoft Sentinel incident:

```kusto
GambitPoliciesIssues
| where State == "Active" and Severity == "High"
```

It maps `ResourceDisplayId` to Host and Azure Resource entities and surfaces `PolicyName`, `PolicyCategories`, `IssueStatus`, `AffectedSystems`, `Environment`, and `RemediationSteps` as custom incident details.

## Deployment

Deploy the connector from the Microsoft Sentinel Content Hub. The **Deploy** button provisions the `GambitPoliciesIssues_CL` table, the Data Collection Rule and Endpoint, and an Entra app registration granted **Monitoring Metrics Publisher** on the DCR. The connector page then surfaces the five credentials (Tenant ID, Application ID, Application Secret, Data Collection Endpoint URI, Data Collection Rule Immutable ID) and the stream name (`Custom-GambitPoliciesIssues`) that Gambit Security consumes to push issues.
