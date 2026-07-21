| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                          |
|-------------|--------------------------------|-----------------------------------------------------------------------------|
| 3.1.0       | 16-07-2026                     | **Ingestion-volume optimization (CCF Data Connector)**: DCR transform no longer stores the raw `data`/`oracle` dynamic payloads alongside flattened columns; removed HTTP request/response header noise, CloudEvents boilerplate, duplicated fields, credential-bearing headers and the `stateChange.current.keyValue` key blob. Table schema reduced 201 → 86 columns; all columns used by the Parser, Analytic Rules, Hunting Queries, and Workbook are preserved. Fixed `SrcIpAddr` mapping typo (`ipAddres`), `data_request_id_s`/`data_request_path_s` payload-level mapping, and hyphenated request-header access (`X-Forwarded-For`, `X-Real-IP`, `oci-original-url`). **Parser** updated to v1.1.0: continues to read both `OCI_Logs_CL` and `OCI_LogsV2_CL`, and now derives `EventStartTime`/`EventEndTime` for V2 flow-log rows at read time. **Analytic Rules & Hunting Queries**: added the CCF connector (`OracleCloudInfraConnector`) to `requiredDataConnectors` alongside the existing connector. |
| 3.0.10      | 26-05-2026                     | Updated OCI connector UI to include IAM permissions guidance and removed the "Important -" label. |
| 3.0.9       | 10-02-2026                     | Add support for group Cursor                                                |
| 3.0.8       | 05-02-2026                     | fix name in package 3.0.7                                                   |
| 3.0.7       | 26-01-2026                     | Improve Instructions part of the connector with more InfoMessage.           |
| 3.0.6       | 09-12-2025                     | Support Multistream + multi partition.       |
| 3.0.5       | 13-11-2025                     | Updated partition id text box's description with zero-based indexing.       |
| 3.0.4       | 22-09-2025                     | Updated the OCI **CCF Data Connector** instructions to include information about the partition ID limitation.		 							 |
| 3.0.3       | 25-08-2025                     | Moving OCI **CCF Data Connector** to GA		 							 |
| 3.0.2       | 14-07-2025                     | Introduced new **CCF Connector** to the Solution - "OCI-Connector-CCP-Definition".|
| 3.0.1       | 05-10-2023                     | Manual deployment instructions updated for **Data Connector**.               |
| 3.0.0       | 21-08-2023                     | Modified the **Parser** by adding Columnifexists condition to avoid errors. |  
