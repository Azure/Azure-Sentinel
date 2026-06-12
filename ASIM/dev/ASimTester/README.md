# ASIM testers

## ASIM schema tester

This test validates your parser schema whether column names and types are correct, unnormalized columns are present, and whether mandatory, recommended, or optional fields are missing. To run the test against your parser, run the following query on your Microsoft Sentinel workspace after installing the tester:

```kusto
<parser> | getschema | invoke ASimSchemaTester('<schema>')
```

Refer to this [link](https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas) for supported schema name values.

## ASIM data tester

This test validates the output values from your parser or ASIM table. To run the test against your data, run the following query on your Microsoft Sentinel workspace after installing the tester:

```kusto
<parser or table name> | invoke ASimDataTester('<schema>')
```

Replace the parser or table name of your choice.

Refer to this [link](https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas) for supported schema name values.


## More information

For more information on using the tester refer to the document [Develop an ASIM parser](https://learn.microsoft.com/azure/sentinel/normalization-develop-parsers#test-parsers).

To learn more about ASIM, refer to [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM).

<br>

## Deployment links

| Tool | Azure | Azure Gov |
| ---- | ----- | --------- |
| All | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdev%2FASimTester%2FASimTester.json) | [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdev%2FASimTester%2FASimTester.json) |
| Schema Tester | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdev%2FASimTester%2FASimSchemaTester.json) | [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdev%2FASimTester%2FASimSchemaTester.json) |
| Data Tester | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdev%2FASimTester%2FASimDataTester.json) | [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2Fdev%2FASimTester%2FASimDataTester.json) |

