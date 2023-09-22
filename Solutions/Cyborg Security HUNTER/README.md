Update root URI to have options prefilled
Remove the data connector status connectivity
No data flow in. Once configured in HUNTER, use hunter UI to access info in Sentinel and run hunts in Sentinel. 

azuresentinelpartners@microsoft.com


7/28/2023
- getting feedback for connectivity
- omit when submit the PR





 8/29/2023
 =======Starting Package Creation using V3 tool=========
Enter solution data file path : /home/cyborgmike/projects/Azure-Sentinel/Solutions/Cyborg Security HUNTER/Data
Path /home/cyborgmike/projects/Azure-Sentinel/Solutions/Cyborg Security HUNTER/Data, DefaultPackageVersion is 3.0.0
SolutionBasePath is /home/cyborgmike/projects/Azure-Sentinel/Solutions/, Solution Name Cyborg Security HUNTER
CatelogAPI Details not found for offerId azure-sentinel-solution-cyborgsecurity-hunter
CatalogAPI Offer details not found for given offerId azure-sentinel-solution-cyborgsecurity-hunter. Package Version set to Default version 3.0.0
Package version updated to 3.0.0
Package version identified is 3.0.0
Downloading /home/cyborgmike/projects/Azure-Sentinel/Solutions/Cyborg Security HUNTER/Data Connectors/Connector_CyborgSecurity_HUNTER.json
Generating Data Connector using Data Connectors/Connector_CyborgSecurity_HUNTER.json
Downloading /home/cyborgmike/projects/Azure-Sentinel/Solutions/Cyborg Security HUNTER/Hunting Queries/Prohibited Applications Spawning cmd.exe or powershell.exe.yaml
Generating Hunting Query using Hunting Queries/Prohibited Applications Spawning cmd.exe or powershell.exe.yaml
Downloading /home/cyborgmike/projects/Azure-Sentinel/Solutions/Cyborg Security HUNTER/SolutionMetadata.json
Inside of PrepareSolutionMetadata
                                                                                                                        
Validating Package\createUiDefinition.json                                                                              
  JSONFiles Should Be Valid                                                                                             
    [+] JSONFiles Should Be Valid (4 ms)                                                                                
  Allowed Values Should Actually Be Allowed                                                                             
    [+] Allowed Values Should Actually Be Allowed (70 ms)                                                               
  Controls In Outputs Must Exist                                                                                        
    [+] Controls In Outputs Must Exist (2 ms)                                                                           
  CreateUIDefinition Must Not Have Blanks                                                                               
    [+] CreateUIDefinition Must Not Have Blanks (2 ms)                                                                  
  CreateUIDefinition Should Have Schema                                                                                 
    [+] CreateUIDefinition Should Have Schema (2 ms)                                                                    
  Credential Confirmation Should Not Be Hidden                                                                          
    [+] Credential Confirmation Should Not Be Hidden (75 ms)                                                            
  Handler Must Be Correct                                                                                               
    [+] Handler Must Be Correct (3 ms)                                                                                  
  HideExisting Must Be Correctly Handled                                                                                
    [+] HideExisting Must Be Correctly Handled (149 ms)                                                                 
  Location Should Be In Outputs                                                                                         
    [+] Location Should Be In Outputs (2 ms)                                                                            
  Outputs Must Be Present In Template Parameters                                                                        
    [+] Outputs Must Be Present In Template Parameters (2 ms)                                                           
  Parameters Without Default Must Exist In CreateUIDefinition                                                           
    [+] Parameters Without Default Must Exist In CreateUIDefinition (3 ms)                                              
  Password Textboxes Must Be Used For Password Parameters                                                               
    [+] Password Textboxes Must Be Used For Password Parameters (57 ms)                                                 
  PasswordBoxes Must Have Min Length                                                                                    
    [+] PasswordBoxes Must Have Min Length (48 ms)                                                                      
  Textboxes Are Well Formed                                                                                             
    [+] Textboxes Are Well Formed (70 ms)                                                                               
  Tooltips Should Be Present                                                                                            
    [+] Tooltips Should Be Present (80 ms)                                                                              
  Usernames Should Not Have A Default                                                                                   
    [+] Usernames Should Not Have A Default (69 ms)                                                                     
  Validations Must Have Message                                                                                         
    [+] Validations Must Have Message (83 ms)                                                                           
  VMSizes Must Match Template                                                                                           
    [+] VMSizes Must Match Template (55 ms)                                                                             
Validating Package\mainTemplate.json                                                                                    
  adminUsername Should Not Be A Literal                                                                                 
    [+] adminUsername Should Not Be A Literal (163 ms)                                                                  
  apiVersions Should Be Recent In Reference Functions                                                                   
    [+] apiVersions Should Be Recent In Reference Functions (4 ms)                                                      
  apiVersions Should Be Recent                                                                                          
    [?] apiVersions Should Be Recent (128 ms)                                                                           
        Could not identify provider resource for Microsoft.OperationalInsights/workspaces/providers/contentTemplates    
        The apiVersion 2021-03-01-preview was not found for the resource type: Microsoft.SecurityInsights               
        The apiVersion 2023-04-01-preview was not found for the resource type: Microsoft.SecurityInsights               
        The apiVersion 2023-04-01-preview was not found for the resource type: Microsoft.SecurityInsights               
        The apiVersion 2021-03-01-preview was not found for the resource type: Microsoft.SecurityInsights               
        Could not identify provider resource for Microsoft.OperationalInsights/workspaces/providers/contentTemplates    
        Could not identify provider resource for Microsoft.OperationalInsights/workspaces/providers/contentTemplates/Microsoft.OperationalInsights/savedSearches
        The apiVersion 2022-01-01-preview was not found for the resource type: Microsoft.SecurityInsights               
        The apiVersion 2023-04-01-preview was not found for the resource type: Microsoft.SecurityInsights               
                                                                                                                        
  artifacts parameter                                                                                                   
    [+] artifacts parameter (3 ms)                                                                                      
  CommandToExecute Must Use ProtectedSettings For Secrets                                                               
    [+] CommandToExecute Must Use ProtectedSettings For Secrets (116 ms)                                                
  DependsOn Best Practices                                                                                              
    [+] DependsOn Best Practices (93 ms)                                                                                
  Deployment Resources Must Not Be Debug                                                                                
    [+] Deployment Resources Must Not Be Debug (80 ms)                                                                  
  DeploymentTemplate Must Not Contain Hardcoded Uri                                                                     
    [+] DeploymentTemplate Must Not Contain Hardcoded Uri (5 ms)                                                        
  DeploymentTemplate Schema Is Correct                                                                                  
    [+] DeploymentTemplate Schema Is Correct (1 ms)                                                                     
  Dynamic Variable References Should Not Use Concat                                                                     
    [+] Dynamic Variable References Should Not Use Concat (1 ms)                                                        
  IDs Should Be Derived From ResourceIDs                                                                                
    [-] IDs Should Be Derived From ResourceIDs (185 ms)                                                                 
        Property: "contentProductId" must use one of the following expressions for an resourceId property:              
            extensionResourceId,resourceId,subscriptionResourceId,tenantResourceId,if,parameters,reference,variables,subscription,guid
        Property: "id" must use one of the following expressions for an resourceId property:                            
            extensionResourceId,resourceId,subscriptionResourceId,tenantResourceId,if,parameters,reference,variables,subscription,guid
        Property: "contentProductId" must use one of the following expressions for an resourceId property:              
            extensionResourceId,resourceId,subscriptionResourceId,tenantResourceId,if,parameters,reference,variables,subscription,guid
        Property: "id" must use one of the following expressions for an resourceId property:                            
            extensionResourceId,resourceId,subscriptionResourceId,tenantResourceId,if,parameters,reference,variables,subscription,guid
        Property: "contentProductId" must use one of the following expressions for an resourceId property:              
            extensionResourceId,resourceId,subscriptionResourceId,tenantResourceId,if,parameters,reference,variables,subscription,guid
        Property: "id" must use one of the following expressions for an resourceId property:                            
            extensionResourceId,resourceId,subscriptionResourceId,tenantResourceId,if,parameters,reference,variables,subscription,guid
                                                                                                                        
  Location Should Not Be Hardcoded                                                                                      
    [+] Location Should Not Be Hardcoded (341 ms)                                                                       
  ManagedIdentityExtension must not be used                                                                             
    [+] ManagedIdentityExtension must not be used (3 ms)                                                                
  Min And Max Value Are Numbers                                                                                         
    [+] Min And Max Value Are Numbers (5 ms)                                                                            
  Outputs Must Not Contain Secrets                                                                                      
    [+] Outputs Must Not Contain Secrets (4 ms)                                                                         
  Parameter Types Should Be Consistent                                                                                  
    [+] Parameter Types Should Be Consistent (192 ms)                                                                   
  Parameters Must Be Referenced                                                                                         
    [+] Parameters Must Be Referenced (17 ms)                                                                           
  Password params must be secure                                                                                        
    [+] Password params must be secure (2 ms)                                                                           
  providers apiVersions Is Not Permitted                                                                                
    [+] providers apiVersions Is Not Permitted (7 ms)                                                                   
  ResourceIds should not contain                                                                                        
    [+] ResourceIds should not contain (2 ms)                                                                           
  Resources Should Have Location                                                                                        
    [+] Resources Should Have Location (2 ms)                                                                           
  Resources Should Not Be Ambiguous                                                                                     
    [+] Resources Should Not Be Ambiguous (2 ms)                                                                        
  Secure Params In Nested Deployments                                                                                   
    [+] Secure Params In Nested Deployments (148 ms)                                                                    
  Secure String Parameters Cannot Have Default                                                                          
    [+] Secure String Parameters Cannot Have Default (1 ms)                                                             
  Template Should Not Contain Blanks                                                                                    
    [-] Template Should Not Contain Blanks (452 ms)                                                                     
        Empty property:  [] Line: 86, Column: 34                                                                        
        Empty property:  [] Line: 87, Column: 35                                                                        
        Empty property:  [] Line: 88, Column: 31                                                                        
        Empty property:  [] Line: 89, Column: 43                                                                        
        Empty property:  [] Line: 95, Column: 40                                                                        
        Empty property:  [] Line: 228, Column: 26                                                                       
        Empty property:  [] Line: 229, Column: 23                                                                       
        Empty property:  [] Line: 230, Column: 35                                                                       
        Empty property:  [] Line: 231, Column: 27                                                                       
        Empty property:  [] Line: 237, Column: 32                                                                       
                                                                                                                        
  URIs Should Be Properly Constructed                                                                                   
    [+] URIs Should Be Properly Constructed (145 ms)                                                                    
  Variables Must Be Referenced                                                                                          
    [-] Variables Must Be Referenced (69 ms)                                                                            
        Unreferenced variable: workspaceResourceId                                                                      
                                                                                                                        
  Virtual Machines Should Not Be Preview                                                                                
    [+] Virtual Machines Should Not Be Preview (191 ms)                                                                 
  VM Images Should Use Latest Version                                                                                   
    [+] VM Images Should Use Latest Version (1 ms)                                                                      
  VM Size Should Be A Parameter                                                                                         
    [+] VM Size Should Be A Parameter (110 ms)                                                                          
Pass  : 45                                                                                                              
Total : 48                                                                                                              
Fail  : 3                                                                                                               
                                                                                                                        
                                                                                                                        
                                                                                                                        
Failed arm-ttk (Test-AzTemplate): Package                                                                               
Failed arm-ttk (Test-AzTemplate) on solutions: Package 