## 1.0
- Converted MCAS Acitivyt Data connector from Logic Apps to Azure Function
- Splitting the data if it is more than 25MB

## 2.0
- Function Schedule (CRON Expression) as parameter
- Updated StorageAccountName and KeyVaultName
- Updated Path for Function Package
- Deleted the usage of Storage Account to write last run executions
- Writing Last Run executions to Azure Storage Table

## 3.0
- LA Custom Table Name as parameter
- Updated Unix Timestamp (Epoch) Calculations