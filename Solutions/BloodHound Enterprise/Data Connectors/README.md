# Schema Documentation (Experimental)


```mermaid
%%{ init : { "theme" : "default", "block-beta" : { "curve" : "basis" }}}%%
block-beta

columns 5
  block:S
    columns 1
    block:PS
        columns 1
        Source["posture-stats ModelRiskPostureStat"]
        S_CreatedAt
        S_CriticalRiskCount
        S_DomainSid
        S_ExposureIndex
        S_Id
        S_TierZeroCount
        S_UpdatedAt
    end
    space
    block:DomainSelector
      columns 1
      O_Selector["domain selector"]
      O_Type
      O_Name
      O_Type
      O_Id
    end
  end
  space
  block:T
    columns 1
    Target["BloodhoundEnterpriseData"]
    T_ID
    T_CreatedAt
    T_DataType["data-type"]
    T_DomainSID["DomainSID"]
    T_DomainName["DomainName"]
    T_Principal["Principal"]
    T_DomainID
    T_DomainType
    T_TierZeroPrincipal["TierZeroPrincipal"]
    T_NonTierZeroPrincipal["NonTierZeroPrincipal"]
    T_ExposureIndex
    T_FindingCount
    T_TierZeroCount
  end
  space
  block:CL
    columns 1
    LOG["BloodhoundLogs_CL"]
    
  end
O_Name --> T_DomainName
O_Type --> T_DomainType
O_Id --> T_DomainID
S_CreatedAt --> T_CreatedAt
S_DomainSid --> T_DomainSID
S_ExposureIndex --> T_ExposureIndex
S_CriticalRiskCount --> T_FindingCount
S_TierZeroCount --> T_TierZeroCount
S_Id --> T_ID

style Source fill:#969,stroke:#333,stroke-width:4px
style Target fill:#969,stroke:#333,stroke-width:4px
style O_Selector fill:#969,stroke:#333,stroke-width:4px

```

#### Source

| Column Name             | Type      | Description                  | Source | Column                        |
|-------------------------|-----------|------------------------------|--------|-------------------------------------------|
| TimeGenerated           | datetime  | Timestamp when the log was generated      |        |                                           |
| domain_sid              | string    | Security Identifier of the domain         |        |                                           |
| exposure_index          | real      | Index indicating exposure level           |        |                                           |
| tier_zero_count         | real      | Count of tier zero entities               |        |                                           |
| domain_id               | string    | Identifier of the domain                  |        |                                           |
| non_tier_zero_principal | string    | Non-tier zero principal                   |        |                                           |
| tier_zero_principal     | string    | Tier zero principal                       |        |                                           |
| group                   | string    | Group information                         |        |                                           |
| principal               | string    | Principal information                     |        |                                           |
| path_id                 | string    | Identifier of the path                    |        |                                           |
| user                    | string    | User information                          |        |                                           |
| finding_id              | string    | Identifier of the finding                 |        |                                           |
| path_title              | string    | Title of the path                         |        |                                           |
| path_type               | string    | Type of the path                          |        |                                           |
| exposure                | real      | Exposure level                            |        |                                           |
| finding_count           | real      | Count of findings                         |  posture-stats (ModelRiskPostureStat)     |             CriticalRiskCount                              |
| principal_count         | real      | Count of principals                       |        |                                           |
| id                      | long      | Unique identifier                         |        |                                           |
| created_at              | datetime  | Creation timestamp                        |        |                                           |
| updated_at              | datetime  | Update timestamp                          |        |                                           |
| deleted_at              | datetime  | Deletion timestamp                        |        |                                           |
| deleted_at_v            | boolean   | Deletion status                           |        |                                           |
| severity                | string    | Severity level                            |        |                                           |
| domain_impact_value     | real      | Impact value on the domain                |        |                                           |
| domain_name             | string    | Name of the domain                        |        |                                           |
| domain_type             | string    | Type of the domain                        |        |                                           |
| data_type               | string    | Type of the data                          |        |                                           |
| event_type              | string    | Type of the event                         |        |                                           |
| event_details           | string    | Details of the event                      |        |                                           |
### Questions

 1) The ExposureIndex starts at is from 0 - .1
