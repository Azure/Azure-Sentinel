# AWS VPC Flow Logs Solution - Developer Notes

### 1. Polling Configuration Fix
Due to a bug in CCF (Common Collection Framework), you must set the destination table to null in the polling configuration file:

```json
"destinationTable": null
```

### 2. Main Template File Format Update
In the `mainTemplate.json` file, update the `fileFormat` parameter as shown below, then update the zip package with the modified template:

```json
"fileFormat": {
  "defaultValue": [
    "Json"
  ],
  "type": "array",
  "minLength": 1
}
```

## Post-Update Steps
After making these changes, ensure you update the solution package (zip file) with the modified `mainTemplate.json` file.