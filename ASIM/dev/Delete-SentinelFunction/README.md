# Deletes saved functions from a Log Analytics workspace

This PowerShell script deletes saved functions from a Log Analytics workspace. It supports wildcards and enables batch cleaning of the workspace from unneeded functions, especially when deploying a new function ARM template such as those used by Microsoft Sentinel ASIM.

The script accepts the following parameters:

| Parameter | Description |
| --------- | ----------- |
| FunctionName | A comma-delimited list of names or wildcard patterns of the function to be deleted. The list can also be specified without a parameter name. |
| WorkspaceName | The workspace the functions should be deleted from. |
| ResourceGroup | The resource group of the workspace. |
| Force | If specified, the user is not prompted for confirmation, enabling using the script as part of automation  (Optional). |
| Category | Delete functions only if they belong to this category (Optional). For example, currently, all ASIM functions use the category ASIM, which enables ensuring that the script deletes only ASIM functions even when using wildcards. |
| Emulate | If specified, the script will run without actually deleting, enabling you to list the functions about to be deleted first. |
|||

For example:

Delete a specific function

``` PowerShell
PS> Delete-SentinelFunction TestFunction -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg
```

Delete all ASIM functions (note that some older functions may not have this category)

``` PowerShell
PS> Delete-SentinelFunction * -Category ASIM -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg
```

List of functions in a workspace

``` PowerShell
PS> Delete-SentinelFunction * -Emulate -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg
```
