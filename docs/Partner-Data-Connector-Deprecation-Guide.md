# Microsoft Sentinel Data Connector Deprecation Guide for Partners

This guide describes how ISVs and partners should deprecate or replace a Microsoft Sentinel data connector.

> **Important:** Deprecate the connector before removing it. Existing customers may still depend on the connector and need time to migrate.

## 1. Determine what you are deprecating

Before submitting a request, determine whether you are deprecating a **connector template** or an entire **solution**.

### Connector template

Use template deprecation when retiring one connector implementation while keeping the solution available.

For example, if your solution contains:

- `Contoso (using Azure Functions)`
- `Contoso (via Codeless Connector Framework)`

and CCF replaces the Azure Functions implementation, deprecate only the **Azure Functions connector template**.

### Solution

Use solution deprecation when the **entire solution** is being retired.

Solution deprecation may require coordinated changes across Microsoft Sentinel Content Hub, Marketplace, and the solution repository.

## 2. Submit a deprecation request

Before making the change, submit a deprecation request to the Microsoft Sentinel connector team.

Include:

- Solution and connector name
- Whether you are deprecating a **template** or **solution**
- Reason for deprecation
- Replacement connector, if applicable
- Customer migration instructions
- Proposed deprecation/removal timeline
- ISV contact

If a replacement exists, customers should be given enough information to configure and validate the replacement before disabling the old connector. Do **not** remove the deprecated connector yet. Existing customers may need time to migrate to the replacement.

After the deprecation request is processed, the connector will be marked as **`[Deprecated]`**.
For example:

**Deprecated:**  
`Contoso Events (using Azure Functions) [Deprecated]`

**Replacement:**  
`Contoso Events (via Codeless Connector Framework)`

## 3. Remove the deprecated connector

After the agreed deprecation period and customer migration:

1. Remove the deprecated connector template from the solution.
2. Repackage and version the solution.
3. Publish the updated package.
4. Coordinate Marketplace or Content Hub removal with Microsoft when applicable.

For a **template deprecation**, remove only the deprecated template. The solution and replacement connector remain available.

For example:

**Before removal**
- Contoso Security
  - Contoso Events (using Azure Functions) **[Deprecated]**
  - Contoso Events (via Codeless Connector Framework)

**After removal**
- Contoso Security
  - Contoso Events (via Codeless Connector Framework)

> **Deprecate first, remove later.** Customers should have a clear migration path before the deprecated connector is removed.