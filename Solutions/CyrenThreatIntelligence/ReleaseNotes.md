**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2      | 11-02-2026                    | Fixed CCF paging duplication bug: Changed from Offset paging to PersistentToken paging to prevent duplicate data ingestion when Cyren API startOffset exceeds initial offset. Added DCR transform filter for time-based deduplication. |
| 3.0.1      | 27-01-2026                    | Cost optimization: Changed from offset-based paging to time-based filtering (startTime/endTime) to prevent historical data re-ingestion. Updated queryWindowInMin to 120 minutes per MS reviewer recommendation. |
| 3.0.0      | 16-11-2025                    | Initial Cyren Threat Intelligence CCF solution package, including all connector and ARM templates. |
