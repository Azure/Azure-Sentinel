# Abnormal Security (Push) — optional table-name prefix

Design + proof-of-concept for letting a customer **namespace the connector's
Log Analytics tables with an optional prefix**, so the CCF Push connector can
be deployed on a workspace where the tables would otherwise collide with an
existing set (e.g. a workspace that already ingested Abnormal data under the
same `ABNORMAL_SECURITY_*_CL` names via the legacy Azure Functions connector).

> Status: **design + validated PoC**. The productized change (wiring the prefix
> through `createUiDefinition` → `mainTemplate` and regenerating the package)
> is tracked separately; this folder documents the mechanism and provides a
> working template that reproduces the intended runtime behavior.

## Problem

The Push connector creates nine `ABNORMAL_SECURITY_*_CL` tables with a fixed
DCR schema. If those exact table names already exist with a **different**
schema (for example, auto-typed columns from the Data Collector API — `guid`
vs `string`, or split numeric columns), the connector's **Deploy** step fails
with `Invalid output table schema … columns … do not exist in the new schema
or have different types`, because Log Analytics forbids changing a column's
type or dropping a column on an existing table.

## Solution: optional prefix, applied at install time

Add an **optional** `tablePrefix`. Empty ⇒ current behavior (byte-for-byte).
Non-empty (e.g. `CT`) ⇒ tables become `CT_ABNORMAL_SECURITY_*_CL`, avoiding the
collision. The separator `_` is inserted automatically:

```
pfx = [if(empty(parameters('tablePrefix')), '', concat(parameters('tablePrefix'), '_'))]
```

### Why the prefix lives on the output side only

A DCR decouples the **input stream** (`streamDeclarations`) from the **output
table** (`dataFlows[].outputStream`). Prefixing only the output table + the
`outputStream`, and **leaving the input stream names unchanged**, means the
sender keeps posting to `Custom-ABNORMAL_SECURITY_THREAT_LOG` exactly as today
— the DCR routes it to the prefixed table. **No change is required on the
Abnormal push side.**

### Why it must be baked at install (not Connect)

The framework `DeployPushConnectorButton` accepts no custom input, so the prefix
cannot be a field on the Deploy button. Instead it is collected in the Content
Hub install wizard (`createUiDefinition`) and **baked into the stored connector
content** using single-bracket ARM evaluation (`[concat(parameters('tablePrefix'),
'…')]`), which ARM resolves at install and stores as a literal. When the Deploy
button later instantiates that content, the table/DCR names are already
prefixed. (Contrast with `[[ … ]]`, which the package uses to defer evaluation
to Connect time — the prefix must NOT be deferred.)

## Backward compatibility

- Default `tablePrefix` is empty; the `if(empty(...))` guard yields the original
  names, so existing installations and existing CCF customers are unaffected.
- Input stream names are unchanged, so no sender changes.

## PoC template (`ccf_prefixed_deploy.json`)

A self-contained ARM template that reproduces the runtime behavior for
validation. Deploy it via the portal's **Deploy a custom template** (or
`az deployment group create`). Only input is the optional `tablePrefix`;
DCE/DCR names are auto-derived.

Validated: deployed with `tablePrefix=CT`, pushed a record to the unchanged
`Custom-ABNORMAL_SECURITY_THREAT_LOG` stream, and confirmed it landed in
`CT_ABNORMAL_SECURITY_THREAT_LOG_CL` with the transform applied.

## Productization checklist (package regeneration)

- `createUiDefinition.json`: add an optional "Table prefix" text input → output.
- `mainTemplate.json`: add `tablePrefix` parameter; in the connector
  `contentTemplate`, express table names, DCR `outputStream`, and
  `dataConnectorDefinitions.dataTypes`/connectivity queries as single-bracket
  `[concat(parameters('tablePrefix'), '…')]`. Leave input `streamDeclarations`
  unchanged.
- Route Analytic Rules / Hunting Queries / Workbook through the Parsers, and
  bake the prefix in the four parser `FunctionQuery`s (fewest baked spots).
- Bump the solution version; refresh `ReleaseNotes.md`; regenerate the package
  with the V3 packaging tool; validate with an empty prefix (`arm-ttk` + KQL).
