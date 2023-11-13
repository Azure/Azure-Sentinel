# ASim Schema Validator

This script validates if no duplicate columns are added the ASim Schema.

## Description

When executing the script a valid path to the `ASimTester.csv` file needs to be provided in the FilesPath parameter.
The script will validate if this is a valid file based on the columns that are present.

If the `csv` is invalid an error will be shown.

The script will enummerate through all available schema's in the `csv` file and checks the schema on duplicate columns.
If **no** duplicate values are found, nothing will be returned. In case one or more duplicated values are found, the script will return an object containing the duplicate item(s).

## Example 1

```powershell
  . Validate-AsimCsv.ps1 -FilesPath C:\Users\azurekid\Downloads\ASimTester.csv
```

### Result

![image](https://github.com/SecureHats/Azure-Sentinel/assets/40334679/2515eb8a-b726-480b-b7cb-15b67a86c260)
