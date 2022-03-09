# Delete Log Analytics saved functions

Use this tool to delete saved functions in a LA workspace

To use:

 `>>  Delete-LASavedFunction DeleteM*, TestFunction* -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg`

Parameters:
- FunctionName:
  Specifies a comma delimited list of saved function name to be deleted. Accepts wildchars. 

- WorkspaceName
        Specifies the workspace where functions are saved.

- ResourceGroup
        Specifies the resource group of workspace.

        
- Force
        If set the user will not be prompted for approval. Be causious!

- Category
        Specifies the category of deleted functions.


