# Cato Networks for Microsoft Sentinel

Cato Networks solution version **3.1.0** provides one CCF Push data connector and 12 query-time source functions for six Microsoft ASIM schemas: NetworkSession, Dns, WebSession, Authentication, AlertEvent, and AuditEvent. The parsers are version **3.0.0**. This release is a preview; mapping review and certification are pending.

The CCF connector uses the existing `CatoNetworksEvents_CL` table, and the parsers query its raw rows without changing them or creating normalized tables. This release does not change the existing connector's ingestion, DCR, or RBAC model. Installing or updating the Content Hub solution does not automatically change an existing DCR schema.

## Query the parsers

Each schema has a `vim<Schema>Cato_CatoNetworksEvents_CL` source function with ASIM filter parameters and an `ASim<Schema>Cato_CatoNetworksEvents_CL` wrapper that does not filter. These examples use the source functions with valid parameter names and values; omit optional parameters to use their defaults.

```kusto
vimNetworkSessionCato_CatoNetworksEvents_CL(
    starttime=ago(24h), endtime=now(),
    srcipaddr_has_any_prefix=dynamic(["10.0.0.0/8"]),
    eventresult="Success")
| take 10
```

```kusto
vimDnsCato_CatoNetworksEvents_CL(
    starttime=ago(24h), endtime=now(),
    domain_has_any=dynamic(["example.com"]), eventtype="Query")
| take 10
```

```kusto
vimWebSessionCato_CatoNetworksEvents_CL(
    starttime=ago(24h), endtime=now(),
    url_has_any=dynamic(["example.com"]), eventresult="Success")
| take 10
```

```kusto
vimAuthenticationCato_CatoNetworksEvents_CL(
    starttime=ago(24h), endtime=now(),
    username_has_any=dynamic(["alice"]), eventresult="Success")
| take 10
```

```kusto
vimAlertEventCato_CatoNetworksEvents_CL(
    starttime=ago(24h), endtime=now(),
    threatcategory_has_any=dynamic(["Malware"]))
| take 10
```

```kusto
vimAuditEventCato_CatoNetworksEvents_CL(
    starttime=ago(24h), endtime=now(),
    actorusername_has_any=dynamic(["alice"]))
| take 10
```

For example, query the nonfiltering NetworkSession wrapper with:

```kusto
ASimNetworkSessionCato_CatoNetworksEvents_CL()
| take 10
```

The other wrappers follow the same naming pattern: `ASimDnsCato_CatoNetworksEvents_CL()`, `ASimWebSessionCato_CatoNetworksEvents_CL()`, `ASimAuthenticationCato_CatoNetworksEvents_CL()`, `ASimAlertEventCato_CatoNetworksEvents_CL()`, and `ASimAuditEventCato_CatoNetworksEvents_CL()`.

## Installation and parser updates

After publication, install or update version 3.1.0 through the normal Microsoft Sentinel Content Hub workflow. The solution includes the CCF connector and its managed parser function definitions; generic Microsoft ASIM unifier registration is a separate, explicit configuration step and is not automatic.

### Manual parser updates

Use these public repository templates to install or update parsers for an existing connector:

- [CCF parser template](https://github.com/catonetworks/cato-sentinel/blob/main/asim/ccfTemplate.json)
- [ARM parser template](https://github.com/catonetworks/cato-sentinel/blob/main/asim/armTemplate.json)

The ARM parser template is for an existing connector with a configurable destination table; it does not create a new connector.

### CCF schema updates

The root [`updateTemplate.json`](https://github.com/catonetworks/cato-sentinel/blob/main/updateTemplate.json) is for CCF schema updates only, not parser updates.

Parser updates are manual and on demand; there is no scheduled automatic parser update or reconciliation. Saved-function resource names and aliases remain stable across manual and Content Hub delivery. Back up customer edits before updating: either delivery can replace a same-name managed parser definition.