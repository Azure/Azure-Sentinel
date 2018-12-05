# Hunting Queries

## Interface

```typescript
export enum Techniques {
    InitialAccess,
    Execution,
    Persistence,
    PrivilegeEscalation,
    DefenseEvasion,
    CredentialAccess,
    Discovery,
    LateralMovement,
    Collection,
    Exfiltration,
    CommandAndControl
}

export interface HuntingQuery {
    name: string;
    description: string;
    query: string;
    techniques?: Techniques[];
}
```

## Emphasis

* Don't close queries with semicolon `;` - The queries may be piped. For example `query | count`
* Json is using double quatation mark for strings. In your KQL queries it is best to use a single quatation mark verbatim string. So you would only need to escape the single quote. [reference](https://docs.microsoft.com/azure/kusto/query/scalar-data-types/string)
