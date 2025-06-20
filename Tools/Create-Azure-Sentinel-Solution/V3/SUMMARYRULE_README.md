# Steps to Package Summary Rules:

1. In your solution folder within the `Azure-Sentinel` repository, [navigate here](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions) and create a new folder named `SummaryRules`. Inside this folder, create your SummaryRule file with the `.yaml` extension. For guidance, refer to the [documentation here](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/summary-rules?tabs=azure-resource-manager) or examine example files from [this link](https://github.com/Azure/Azure-Sentinel/tree/master/Summary%20rules).
   
2. After creating your Summary Rule file, go to the `Data` folder and open your data input file.

3. Add a new attribute called `SummaryRules` or `Summary Rules` as an `array` type, similar to how other content types like `Analytic Rules` and `Hunting Queries` are defined. Inside this array, provide the path to your summary rule file.  
   For example:  
   `"SummaryRules": [ "SummaryRules/yourfileName.yaml" ]`

4. Any files listed in this array will be included in the packaging process.

5. Required properties for the Summary Rule file can be found in the parameters table in the [documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/summary-rules?tabs=azure-resource-manager).

6. After making the changes as outlined in the previous steps, you can create a package by following the instructions in the V3 packaging tool. For more details on packaging tool, refer to the [V3 guide here](https://github.com/Azure/Azure-Sentinel/blob/master/Tools/Create-Azure-Sentinel-Solution/V3/README.md).

7. Once the package is generated, it will be located in the Package folder within your solution. The `createUiDefinition.json` file will contain the count of `Summary Rules`.

8. The `mainTemplate.json` file will include a `type` entry of `Microsoft.OperationalInsights/workspaces/summaryLogs` under `contentTemplates` for the resource.

9. To test your `mainTemplate.json`, use the `Deploy a custom template` option from the Azure portal, or upload your `.zip` package to the Marketplace. After testing is complete, you can proceed with publishing to the Marketplace.

## References:
[Summary Rule Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/summary-rules?tabs=azure-resource-manager)
