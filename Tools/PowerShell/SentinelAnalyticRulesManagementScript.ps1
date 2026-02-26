<#
.SYNOPSIS
This script contains cmdlets that automates the massive creation, backup, deletion and update of Analytic Rules in Microsoft Sentinel.

.DESCRIPTION
   Version: 1.0
   Release Date: 2024-03-03
   Author: Stefano Pescosolido (https://www.linkedin.com/in/stefanopescosolido/)
   Short Link: https://aka.ms/sarms
   Presentation & demo: https://www.youtube.com/watch?v=5WO6bfpkrTI <--- WATCH IT FOR SEEING THIS SCRIPT IN ACTION!!! 

#############################

>> HOW TO LAUNCH IT AND WHAT TO EXPECT?

1. Download this script file from GitHub
2. Search for the string "LAUNCHING SECTION"; it's the final section of this script file. 
3. Set the input parameters and choose the cmdlet to launch based on your environment and needs. 
   Note: the "LAUNCHING SECTION" has detailed comments on how to set the parameters.
4. When the parameters are set, open a powershell window and launch the script by calling its file name. 
   Note: The directory from where you launch the script will contain the output log file.   
5. If you are not blocked by the initial checks of the launching conditions, soon you'll see the classical "device login" message. 
   Proceed with the authentication to Azure accordingly: open a browser, put the specified device code, authenticate with a valid user.  
   Note: you need to authenticate with a user having the rights to read and create Analytic Rules and modify Solutions in Sentinel 
   (min. role: Microsoft Sentinel Contributor). Rights on the local computer may be required to read and write the input/output CSV files.   
6. Wait for the end of the execution while reading the output messages.
7. Read the final statistics. If needed, read the content of the log file. 
#############################

.NOTES
The script requires PowerShell 7. 
* Check the version of your powershell by using: $PSVersionTable.PSVersion
* Install it by launching: winget search Microsoft.PowerShell
(https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows)

The script also requires the powershell module Az.Accounts 
(https://learn.microsoft.com/en-us/powershell/module/az.accounts)

Part of the code in this script is taken from https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Sentinel-All-In-One

.DISCLAIMER
This script is provided "as is", without warranty of any kind. 
No extensive testing as been made. Use with caution and at your own risk.

#>



##################################################################################################
# CMDLET section
##################################################################################################

function New-SentinelRules {
    param(
        [Parameter(Mandatory = $true)][string]$SubscriptionId,
        [Parameter(Mandatory = $true)][string]$ResourceGroup,
        [Parameter(Mandatory = $true)][string]$Workspace,
        [Parameter(Mandatory = $true)][string]$Region,
        [Parameter(Mandatory = $false)][bool]$SimulateOnly = $false,
        [Parameter(Mandatory = $false)][int]$LimitToMaxNumberOfRules = 0,
        [Parameter(Mandatory = $false)][string]$InputCsvFile,
        [Parameter(Mandatory = $false)][char]$CsvSeparatorChar,
        [Parameter(Mandatory = $false)][string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
    )
    
    ExecuteRequest -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
    -Mode ([ExecutionMode]::NewRules)   `
    -Simulate $SimulateOnly  `
    -LimitToMaxNumberOfRules $LimitToMaxNumberOfRules  `
    -InputCsvFile $InputCsvFile `
    -CsvSeparatorChar $CsvSeparatorChar  `
    -SeveritiesToInclude $SeveritiesToInclude #-verbose
}

function Get-SentinelTemplates{
    param (
        [Parameter(Mandatory = $true)][string]$SubscriptionId,
        [Parameter(Mandatory = $true)][string]$ResourceGroup,
        [Parameter(Mandatory = $true)][string]$Workspace,
        [Parameter(Mandatory = $true)][string]$Region,
        [Parameter(Mandatory = $false)][string]$OutputAnalyticRuleTemplatesCsvFile,
        [Parameter(Mandatory = $false)][char]$CsvSeparatorChar
    )
    
    ExecuteRequest -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
    -Mode ([ExecutionMode]::GetTemplates) -OutputAnalyticRuleTemplatesCsvFile $OutputAnalyticRuleTemplatesCsvFile   `
    -CsvSeparatorChar $CsvSeparatorChar -SuppressWarningForExportCsv $true
}

function Get-SentinelRules{
    param (
        [Parameter(Mandatory = $true)][string]$SubscriptionId,
        [Parameter(Mandatory = $true)][string]$ResourceGroup,
        [Parameter(Mandatory = $true)][string]$Workspace,
        [Parameter(Mandatory = $true)][string]$Region,
        [Parameter(Mandatory = $false)][string]$OutputRulesCsvFile,
        [Parameter(Mandatory = $false)][char]$CsvSeparatorChar
    )
    
    ExecuteRequest -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
    -Mode ([ExecutionMode]::GetRules) -OutputRulesCsvFile $OutputRulesCsvFile   `
    -CsvSeparatorChar $CsvSeparatorChar -SuppressWarningForExportCsv $true
}

function Export-SentinelRules{
    param (
        [Parameter(Mandatory = $true)][string]$SubscriptionId,
        [Parameter(Mandatory = $true)][string]$ResourceGroup,
        [Parameter(Mandatory = $true)][string]$Workspace,
        [Parameter(Mandatory = $true)][string]$Region,
        [Parameter(Mandatory = $true)][string]$BackupFolder,
        [Parameter(Mandatory = $false)][string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
    )
    
    ExecuteRequest -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
    -Mode ([ExecutionMode]::BackupRules)   `
    -BackupFolder $BackupFolder `
    -SeveritiesToInclude $SeveritiesToInclude #-verbose
}

function Remove-SentinelRules{
    param (
        [Parameter(Mandatory = $true)][string]$SubscriptionId,
        [Parameter(Mandatory = $true)][string]$ResourceGroup,
        [Parameter(Mandatory = $true)][string]$Workspace,
        [Parameter(Mandatory = $true)][string]$Region,
        [Parameter(Mandatory = $false)][bool]$SimulateOnly = $false,
        [Parameter(Mandatory = $false)][int]$LimitToMaxNumberOfRules = 0,
        [Parameter(Mandatory = $false)][string]$BackupFolder,
        [Parameter(Mandatory = $false)][string]$InputCsvFile,
        [Parameter(Mandatory = $false)][char]$CsvSeparatorChar,
        [Parameter(Mandatory = $false)][string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
    )
    
    ExecuteRequest -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
    -Mode ([ExecutionMode]::DeleteRules)   `
    -Simulate $SimulateOnly  `
    -LimitToMaxNumberOfRules $LimitToMaxNumberOfRules  `
    -BackupFolder $BackupFolder  `
    -InputCsvFile $InputCsvFile `
    -CsvSeparatorChar $CsvSeparatorChar  `
    -SeveritiesToInclude $SeveritiesToInclude #-verbose
}

function Update-SentinelRules{
    param (
        [Parameter(Mandatory = $true)][string]$SubscriptionId,
        [Parameter(Mandatory = $true)][string]$ResourceGroup,
        [Parameter(Mandatory = $true)][string]$Workspace,
        [Parameter(Mandatory = $true)][string]$Region,
        [Parameter(Mandatory = $false)][bool]$SimulateOnly = $false,
        [Parameter(Mandatory = $false)][int]$LimitToMaxNumberOfRules = 0,
        [Parameter(Mandatory = $false)][string]$BackupFolder,
        [Parameter(Mandatory = $false)][string]$InputCsvFile,
        [Parameter(Mandatory = $false)][char]$CsvSeparatorChar,
        [Parameter(Mandatory = $false)][string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
    )
    
    ExecuteRequest -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
    -Mode ([ExecutionMode]::UpdateRules)   `
    -Simulate $SimulateOnly  `
    -LimitToMaxNumberOfRules $LimitToMaxNumberOfRules  `
    -BackupFolder $BackupFolder  `
    -InputCsvFile $InputCsvFile `
    -CsvSeparatorChar $CsvSeparatorChar  `
    -SeveritiesToInclude $SeveritiesToInclude #-verbose
}

##################################################################################################
# Helper functions section
##################################################################################################

function CreateAuthenticationHeader {
    param (
        [Parameter(Mandatory = $true)][string]$TenantId,
        [Parameter(Mandatory = $false)][string]$PrefixInDisplayName
    )
    $instanceProfile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
    $profileClient = New-Object -TypeName Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient -ArgumentList ($instanceProfile)
    $token = $profileClient.AcquireAccessToken($TenantId)
    $authNHeader = @{
        'Content-Type'  = 'application/json' 
        'Authorization' = 'Bearer ' + $token.AccessToken 
    }

    return $authNHeader
}

function CreateAnalyticRule {
    param (
        [Parameter(Mandatory = $true)][object]$AuthHeader,
        [Parameter(Mandatory = $true)][string]$BaseUri,
        [Parameter(Mandatory = $true)][object]$Template,
        [Parameter(Mandatory = $false)][bool]$SimulateOnly = $true
    )
    
    #Ref. https://learn.microsoft.com/en-us/rest/api/securityinsights/alert-rules/create-or-update?view=rest-securityinsights-2023-02-01&tabs=HTTP

    #$alertUri = "$BaseUri/providers/Microsoft.SecurityInsights/alertRules/"
    $BaseAlertUri = $BaseUri + "/providers/Microsoft.SecurityInsights/alertRules/"
    
    $kind = $Template.properties.mainTemplate.resources.kind
    $displayName = $Template.properties.mainTemplate.resources.properties[0].displayName
    $eventGroupingSettings = $Template.properties.mainTemplate.resources.properties[0].eventGroupingSettings
    if ($null -eq $eventGroupingSettings) {
        $eventGroupingSettings = [ordered]@{aggregationKind = "SingleAlert" }
    }
    $body = ""
    $properties = $Template.properties.mainTemplate.resources[0].properties
    $properties.enabled = $true
    #Add the field to link this rule with the rule template so that the rule template will show up as used
    #We had to use the "Add-Member" command since this field does not exist in the rule template that we are copying from.
    $properties | Add-Member -NotePropertyName "alertRuleTemplateName" -NotePropertyValue $Template.properties.mainTemplate.resources[0].name
    $properties | Add-Member -NotePropertyName "templateVersion" -NotePropertyValue $Template.properties.mainTemplate.resources[1].properties.version


    #Depending on the type of alert we are creating, the body has different parameters
    switch ($kind) {
        "MicrosoftSecurityIncidentCreation" {  
            $body = @{
                "kind"       = "MicrosoftSecurityIncidentCreation"
                "properties" = $properties
            }
        }
        "NRT" {
            $body = @{
                "kind"       = "NRT"
                "properties" = $properties
            }
        }
        "Scheduled" {
            $body = @{
                "kind"       = "Scheduled"
                "properties" = $properties
            }
            
        }
        Default { }
    }
    #If we have created the body...
    if ("" -ne $body) {
        #Create the GUId for the alert and create it.
        $guid = (New-Guid).Guid
        #Create the URI we need to create the alert.
        $alertUri = $BaseAlertUri + $guid + "?api-version=2022-12-01-preview"
        try {
            Write-Verbose -Message "Template: $displayName - Creating the rule...."
            
            if(-not($SimulateOnly)){
                $rule = Invoke-RestMethod -Uri $alertUri -Method Put -Headers $AuthHeader -Body ($body | ConvertTo-Json -EnumsAsStrings -Depth 50)
                Write-Host -Message "Template: $displayName - Creating the rule - Succeeded" -ForegroundColor Green  
                #This pauses for 1 second so that we don't overload the workspace.
                Start-Sleep -Seconds 1
            }
            else {
                Write-Host -Message "Template: $displayName - Creating the rule - Succeeded (SIMULATED)" -ForegroundColor Green  
            }
            
        }
        catch {
            Write-Verbose "Template: $displayName - ERROR while creating the rule:"
            Write-Verbose $_
            #Write-Host -Message "Template: $displayName - ERROR while creating the rule: $(($_).Exception.Message)" -ForegroundColor Red
            Write-Host -Message "Template: $displayName - ERROR while creating the rule" -ForegroundColor Red
            throw   
        }
    }

    return $rule
}

function LinkAnalyticRuleToSolution {
    param (
        [Parameter(Mandatory = $true)][object]$AuthHeader,
        [Parameter(Mandatory = $true)][string]$BaseUri,
        [Parameter(Mandatory = $true)][object]$Rule,
        [Parameter(Mandatory = $true)][object]$Template,
        [Parameter(Mandatory = $true)][object]$Solution,
        [Parameter(Mandatory = $false)][bool]$SimulateOnly = $true
    )

    $baseMetaURI = $BaseUri + "/providers/Microsoft.SecurityInsights/metadata/analyticsrule-"

    $metabody = @{
        "apiVersion" = "2023-02-01"
        "name"       = "analyticsrule-" + $Rule.name
        "type"       = "Microsoft.OperationalInsights/workspaces/providers/metadata"
        "id"         = $null
        "properties" = @{
            "contentId" = $Template.properties.mainTemplate.resources[0].name
            "parentId"  = $Rule.id
            "kind"      = "AnalyticsRule"
            "version"   = $Template.properties.mainTemplate.resources.properties[1].version
            "source"    = $Solution.source
            "author"    = $Solution.author
            "support"   = $Solution.support
        }
    }
    Write-Verbose -Message "Rule: $(($Rule).displayName) - Updating metadata...."
    $metaURI = $baseMetaURI + $Rule.name + "?api-version=2023-02-01"
    try {
        if(-not($SimulateOnly)){
            $metaVerdict = Invoke-RestMethod -Uri $metaURI -Method Put -Headers $AuthHeader -Body ($metabody | ConvertTo-Json -EnumsAsStrings -Depth 5)
            Write-Host -Message "Rule: $(($Rule).properties.displayName) - Updating metadata - Succeeded" -ForegroundColor Green 
            #This pauses for 1 second so that we don't overload the workspace.
            Start-Sleep -Seconds 1 
        } else {            
            Write-Host -Message "Rule: $(($Rule).properties.displayName) - Updating metadata - Succeeded (SIMULATED)" -ForegroundColor Green  
        }
              
    }
    catch {
        Write-Verbose "Rule: $(($Rule).displayName) - ERROR while updating metadata:"
        Write-Verbose $_
        #Write-Host -Message "Rule: $(($Rule).displayName) - ERROR while updating metadata: $(($_).Exception.Message)" -ForegroundColor Red
        Write-Host -Message "Rule: $(($Rule).displayName) - ERROR while updating metadata" -ForegroundColor Red
        throw
    }
    return $metaVerdict

}

function DeleteRule {
    param (
        [Parameter(Mandatory = $true)][object]$AuthHeader,
        [Parameter(Mandatory = $true)][string]$BaseUri,
        [Parameter(Mandatory = $true)][object]$Rule,
        [Parameter(Mandatory = $false)][bool]$SimulateOnly = $true
    )

    $baseMetaURI = $BaseUri + "/providers/Microsoft.SecurityInsights/alertRules/"

    Write-Verbose -Message "Rule: $(($Rule).displayName) - About to be deleted...."
    $fullURI = $baseMetaURI + $Rule.name + "?api-version=2023-02-01"
    try {
        if(-not($SimulateOnly)){
            Invoke-RestMethod -Uri $fullURI -Method Delete -Headers $AuthHeader 
            Write-Host -Message "Rule: $(($Rule).properties.displayName) - Delete - Succeeded" -ForegroundColor Green 
            #This pauses for 1 second so that we don't overload the workspace.
            Start-Sleep -Seconds 1 
        } else {            
            Write-Host -Message "Rule: $(($Rule).properties.displayName) - Delete - Succeeded (SIMULATED)" -ForegroundColor Green  
        }              
    }
    catch {
        Write-Verbose "Rule: $(($Rule).displayName) - ERROR while deleting the rule:"
        Write-Verbose $_
        #Write-Host -Message "Rule: $(($Rule).displayName) - ERROR while deleting the rule: $(($_).Exception.Message)" -ForegroundColor Red
        Write-Host -Message "Rule: $(($Rule).displayName) - ERROR while deleting the rule" -ForegroundColor Red
        throw
    }
}

function IsFirstVersionLowerThanSecondVersion {
    param (
        [Parameter(Mandatory = $true)][string]$v1,
        [Parameter(Mandatory = $true)][string]$v2
    )

    $res = $false

    $a1 = $v1.Split(".") | ForEach-Object { [int]$_ }
    $a2 = $v2.Split(".") | ForEach-Object { [int]$_ }

    # Get the length of the shortest array
    $minLength = [Math]::Min($a1.Length, $a2.Length)

    # Compare the elements of the two arrays
    for ($i = 0; $i -lt $minLength; $i++) {
        if ($a1[$i] -lt $a2[$i]) {
            $res = $true
            break;
        } 
    }

    # If all elements are equal, compare the length of the arrays
    if ($i -eq $minLength) {
        if ($a1.Length -lt $a2.Length) {
            $res = $true
        } 
    }

    return $res
}

function CheckIfAnAnalyticRuleAssociatedToTemplateExist {
    param (
        [Parameter(Mandatory = $true)][object]$AuthHeader,
        [Parameter(Mandatory = $true)][string]$BaseUri,
        [Parameter(Mandatory = $true)][object]$Template
    )

    $uri = $BaseUri + "/providers/Microsoft.SecurityInsights/alertRules?api-version=2023-02-01"
    
    $allRules = (Invoke-RestMethod -Uri $uri -Method Get -Headers $AuthHeader).value

    $found = $false
    foreach($rule in $allRules){
        if($rule.properties.alertRuleTemplateName -eq $Template.properties.mainTemplate.resources[0].name){
            $found = $true
            break
        }
    }
    
    return $found

}

function GetAnalyticRulesAssociatedToTemplate {
    param (
        [Parameter(Mandatory = $true)][object]$AuthHeader,
        [Parameter(Mandatory = $true)][string]$BaseUri,
        [Parameter(Mandatory = $true)][object]$Template
    )

    $res = $null
    $uri = $BaseUri + "/providers/Microsoft.SecurityInsights/alertRules?api-version=2023-02-01"
    
    $allRules = (Invoke-RestMethod -Uri $uri -Method Get -Headers $AuthHeader).value
    
    foreach($rule in $allRules){
        if($rule.properties.alertRuleTemplateName -eq $Template.properties.mainTemplate.resources[0].name){            
            if($null -eq $res){
                $res = New-Object System.Collections.ArrayList
            }
            $res.Add($rule)
        }
    }
    
    return $res

}

function ExportAnalyticRulesAsArmTemplate {
    param (
        [Parameter(Mandatory = $true)][object]$Rule,
        [Parameter(Mandatory = $true)][string]$filePath
    )

    $jsonRule = $Rule | ConvertTo-Json -Depth 100

    #Add the outer elements to ensure that the file can be processed in the Azure portal as valid custom template (https://portal.azure.com/#create/Microsoft.Template)
    $ruleAsJsonArmTemplate = @"
{
    `"`$schema`": `"https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#`",
    `"contentVersion`": `"1.0.0.0`",
    `"resources`": [
        RULE_PLACEHOLDER
    ]
}
"@

    $finalJson = $ruleAsJsonArmTemplate -replace "RULE_PLACEHOLDER", $jsonRule

    #Adjust to ensure that the file can be processed in the Azure portal as valid custom template (https://portal.azure.com/#create/Microsoft.Template)
    $o = $finalJson | ConvertFrom-Json
    $ruleId = $o.resources[0].name
    $o.resources[0].name = "sentinel-central/Microsoft.SecurityInsights/$ruleId"
    $o.resources[0].type = "Microsoft.OperationalInsights/workspaces/providers/alertRules"
    $o.resources[0]  | Add-Member -Type NoteProperty -Name "apiVersion" -Value "2022-11-01-preview"
    $o.resources[0].PSObject.Properties.Remove("etag")
    $o.resources[0].properties.PSObject.Properties.Remove("lastModifiedUtc")
    $finalJson = $o | ConvertTo-Json -Depth 100

    #Write to file
    $finalJson | Out-File $filePath    
     
    Write-Host -Message "Rule: $($o.resources[0].properties.displayName) - Backup - Succeeded" -ForegroundColor Green 
}

enum ExecutionMode{
    GetTemplates    
    GetRules
    NewRules
    BackupRules
    DeleteRules
    UpdateRules
}

function ExecuteRequest 
    (
        [string]$SubscriptionId,
        [string]$ResourceGroup,
        [string]$Workspace,
        [string]$Region,
        [ExecutionMode] $Mode, 
        [string]$OutputAnalyticRuleTemplatesCsvFile,
        [string]$OutputRulesCsvFile,
        [char]$CsvSeparatorChar,
        [bool]$SimulateOnly = $false,
        [int]$LimitToMaxNumberOfRules = 0,
        [string]$BackupFolder,
        [string]$InputCsvFile,
        [string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
    )
{
    ########### Check of the launch conditiona and of input parameters ########### 

    # Check installed PowerShell version 
    if($PSVersionTable.PSVersion.Major -lt 7){
        Write-Host "This cmdlet requires PowerShell 7. Exiting..." -ForegroundColor Red
        exit
    }
    
    #Check if Az.Accounts is installed
    $module = Get-Module -ListAvailable -Name Az.Accounts
    if($null -eq $module){
        Write-Host "The module 'Az.Accounts' is required and is not installed." -ForegroundColor Red
        Write-Host "To install it, open PowerShell as and Administrator and execute the following command: " -ForegroundColor Red
        Write-Host "Install-Module -Name Az.Accounts" -ForegroundColor Red
        Write-Host "Exiting..." -ForegroundColor Red
        exit
    }
    
    # Set default values for $CsvSeparatorChar if not set as parameter
    if( ([string]::IsNullOrEmpty($CsvSeparatorChar)) -or  (([byte]$CsvSeparatorChar) -eq 0) ) {
        try {
            $CsvSeparatorChar = [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.ListSeparator
        }
        catch {
            $CsvSeparatorChar = ','
        }        
    } 
    
    # Set default values for $SeveritiesToInclude if not set as parameter
    if(($Mode -ne ([ExecutionMode]::GetTemplates)) -and ($Mode -ne ([ExecutionMode]::GetRules)) -and ([string]::IsNullOrEmpty($SeveritiesToInclude))){
        # By default, all severities are included
        $SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
    } 

    # Check the coherence of the input parameters
    $askForConfirmation = $false
    
    if(($Mode -eq ([ExecutionMode]::GetTemplates)) -and ([string]::IsNullOrEmpty($OutputAnalyticRuleTemplatesCsvFile))){
        Write-Host "Missing value for the input parameter 'OutputAnalyticRuleTemplatesCsvFile'. Exiting..." -ForegroundColor Red
        exit
    }

    if(($Mode -eq ([ExecutionMode]::GetRules)) -and ([string]::IsNullOrEmpty($OutputRulesCsvFile))){
        Write-Host "Missing value for the input parameter 'OutputRulesCsvFile'. Exiting..." -ForegroundColor Red
        exit
    }

    if(($Mode -eq ([ExecutionMode]::GetTemplates)) -and (-not([string]::IsNullOrEmpty($OutputAnalyticRuleTemplatesCsvFile)))){
        if(Test-Path($OutputAnalyticRuleTemplatesCsvFile)){
            Write-Host "NOTE: The file '$OutputAnalyticRuleTemplatesCsvFile' already exists and will be overwritten." -ForegroundColor Blue -BackgroundColor Yellow
            $askForConfirmation = $true
        }
        $folder = Split-Path -Parent $OutputAnalyticRuleTemplatesCsvFile
        if(-not(Test-Path($folder))){
            Write-Host "The folder '$folder' specified in the input parameter 'OutputAnalyticRuleTemplatesCsvFile' does not exist. Exiting..." -ForegroundColor Red
            exit
        }
    }

    if(($Mode -eq ([ExecutionMode]::GetRules)) -and (-not([string]::IsNullOrEmpty($OutputRulesCsvFile)))){
        if(Test-Path($OutputRulesCsvFile)){
            Write-Host "NOTE: The file '$OutputRulesCsvFile' already exists and will be overwritten." -ForegroundColor Blue -BackgroundColor Yellow
            $askForConfirmation = $true
        }
        $folder = Split-Path -Parent $OutputRulesCsvFile
        if(-not(Test-Path($folder))){
            Write-Host "The folder '$folder' specified in the input parameter 'OutputRulesCsvFile' does not exist. Exiting..." -ForegroundColor Red
            exit
        }
    }

    if(($Mode -eq ([ExecutionMode]::UpdateRules)) -or ($Mode -eq ([ExecutionMode]::DeleteRules))  -or ($Mode -eq ([ExecutionMode]::BackupRules))){
        if(-not([string]::IsNullOrEmpty($BackupFolder))){
            if(-not(Test-Path($BackupFolder) -PathType Container)){
                Write-Host "The  folder '$BackupFolder' specified in the input parameter 'BackupFolder' does not exist. Exiting..." -ForegroundColor Red
                exit
            }
        }
    }

    if($SimulateOnly){
        if($Mode -eq ([ExecutionMode]::NewRules)){
            Write-Host "NOTE: when the input parameter 'SimulateOnly' is set to 'true', no Analytic Rule will be created but you can see - in the output messages and in the log file - what rule would be created" -ForegroundColor Blue  -BackgroundColor Yellow
        }
        if($Mode -eq ([ExecutionMode]::DeleteRules)){
            Write-Host "NOTE: when the input parameter 'SimulateOnly' is set to 'true', no Analytic Rule will be deleted but you can see - in the output messages and in the log file - what rule would be deleted" -ForegroundColor Blue  -BackgroundColor Yellow
        }
        if($Mode -eq ([ExecutionMode]::UpdateRules)){
            Write-Host "NOTE: when the input parameter 'SimulateOnly' is set to 'true', no Analytic Rule will be updated but you can see - in the output messages and in the log file - what rule would be updated" -ForegroundColor Blue  -BackgroundColor Yellow
        }
        $askForConfirmation = $true        
    }

    $inCsvContent = $null
    $filterByTemplateDisplayName = $null
    $filterByRuleID = $null
    if(-not([string]::IsNullOrEmpty($InputCsvFile))){
        if(-not(Test-Path($InputCsvFile))){
            Write-Host "The input file specified in the input parameter 'InputCsvFile' does not exist. Exiting..." -ForegroundColor Red
            exit
        } else {
            try {
                $inCsvContent = Import-Csv $InputCsvFile -Delimiter $CsvSeparatorChar
                
                if($Mode -eq ([ExecutionMode]::NewRules)){
                    if($inCsvContent | Get-Member -Name "DisplayName" -MemberType Properties){
                        $filterByTemplateDisplayName = $inCsvContent | Select-Object -ExpandProperty "DisplayName"
                    }else{
                        Write-Host "Cannot find the column 'DisplayName' in the CSV content of the file '$InputCsvFile' with separator '$CsvSeparatorChar'" -ForegroundColor Red
                        exit
                    }

                }

                if( ($Mode -eq ([ExecutionMode]::DeleteRules)) -or ($Mode -eq ([ExecutionMode]::UpdateRules)) ){
                    if($inCsvContent | Get-Member -Name "RuleID" -MemberType Properties){
                        $filterByRuleID = $inCsvContent | Select-Object -ExpandProperty "RuleID"
                    }else{
                        Write-Host "Cannot find the column 'RuleID' in the CSV content of the file '$InputCsvFile' with separator '$CsvSeparatorChar'" -ForegroundColor Red
                        exit
                    }

                }
                        
            }
            catch {
                Write-Host "Cannot read the CSV content of the file '$InputCsvFile' with separator '$CsvSeparatorChar' - ERROR: " $_.Exception.Message -ForegroundColor Red
                Write-Debug $_
                exit
            }            
        }
    }

    if($askForConfirmation){
        Write-Host " "
        if((Read-Host "Type 'y' if you want to continue...") -ne 'y'){
            Write-Host "Exiting..."
            exit
        }
        Write-Host " "
    }

    ########### Start of execution ########### 
    
    # Initialize log file
    $LogStartTime = Get-Date -Format "yyyy-MM-dd_HH.mm.ss"
    $oLogFile = "log_$LogStartTime.log"
        
    Write-Verbose "---------------------- EXECUTION STARTED - $(Get-Date)" ; "---------------------- EXECUTION STARTED - $LogStartTime" | Out-File $oLogFile 
    Write-Verbose "SubscriptionId: $SubscriptionId"; "SubscriptionId: $SubscriptionId" | Out-File $oLogFile -Append
    Write-Verbose "ResourceGroup: $ResourceGroup"; "ResourceGroup: $ResourceGroup" | Out-File $oLogFile -Append
    Write-Verbose "Workspace: $Workspace"; "Workspace: $Workspace" | Out-File $oLogFile -Append
    Write-Verbose "Region: $Region"; "Region: $Region" | Out-File $oLogFile -Append
    Write-Verbose "Mode: $Mode"; "Mode: $Mode" | Out-File $oLogFile -Append
    Write-Verbose "OutputAnalyticRuleTemplatesCsvFile: $OutputAnalyticRuleTemplatesCsvFile"; "OutputAnalyticRuleTemplatesCsvFile: $OutputAnalyticRuleTemplatesCsvFile" | Out-File $oLogFile -Append  
    Write-Verbose "OutputRulesCsvFile: $OutputRulesCsvFile"; "OutputRulesCsvFile: $OutputRulesCsvFile" | Out-File $oLogFile -Append    
    Write-Verbose "CsvSeparatorChar: $CsvSeparatorChar"; "CsvSeparatorChar: $CsvSeparatorChar" | Out-File $oLogFile -Append
    Write-Verbose "Simulate: $SimulateOnly"; "Simulate: $SimulateOnly" | Out-File $oLogFile -Append
    Write-Verbose "LimitToMaxNumberOfRules: $LimitToMaxNumberOfRules"; "LimitToMaxNumberOfRules: $LimitToMaxNumberOfRules" | Out-File $oLogFile -Append
    Write-Verbose "InputCsvFile: $InputCsvFile"; "InputCsvFile: $InputCsvFile" | Out-File $oLogFile -Append
    Write-Verbose "SeveritiesToInclude: $SeveritiesToInclude"; "SeveritiesToInclude: $SeveritiesToInclude" | Out-File $oLogFile -Append
    
    
    # Authenticate to Azure
    try {
        Connect-AzAccount -DeviceCode -ErrorAction Stop | out-null
    }
    catch {
        Write-Host "Could not connect to Azure with the provided Device Code. Please retry.... - ERROR: " $_.Exception.Message -ForegroundColor Red
        Write-Debug $_
        exit
    }
    
    Write-Verbose "Connected to Azure"
    Write-Host "Execution started. Please wait..."

    # Set the current subscription
    $context = Set-AzContext -SubscriptionId $subscriptionId 
    Write-Verbose "Azure Context set successfully"
    #Write-Debug "context: $context"

    # Get the Authentication Header for calling the REST APIs
    $authHeader = $null

    try {
        $authHeader = CreateAuthenticationHeader($context.Subscription.TenantId)
        if($null -eq $authHeader){
            throw "Authentication Header is null"
        }
        Write-Verbose "Authentication header created successfully"
        #Write-Debug "authHeader: $authHeader"
    }
    catch {
        Write-Host "Could not create the Authentication Header - ERROR: " $_.Exception.Message -ForegroundColor Red
        Write-Debug $_
        Write-Host "Exiting..."
        exit
    }
    
    if($Mode -eq ([ExecutionMode]::GetTemplates)){
        #Initialize CSV file                    
        "DisplayName","Severity","AtLeastOneRuleAlreadyExists","Package" -join $CsvSeparatorChar | Out-File $OutputAnalyticRuleTemplatesCsvFile 
    }
    
    if($Mode -eq ([ExecutionMode]::GetRules)){
        #Initialize CSV file                    
        "RuleDisplayName","RuleID","Enabled","UpdateAvailable","RuleTemplateVersion","TemplatePackage","TemplateDisplayName","TemplateSeverity","TemplateVersion" -join $CsvSeparatorChar | Out-File $OutputRulesCsvFile 
    }
    

    # List all Solutions in Content Hub
    $baseUri = "https://management.azure.com/subscriptions/${SubscriptionId}/resourceGroups/${ResourceGroup}/providers/Microsoft.OperationalInsights/workspaces/${Workspace}"
    $packagesUrl = $baseUri + "/providers/Microsoft.SecurityInsights/contentProductPackages?api-version=2023-04-01-preview"
    #Write-Debug "packagesUrl: $packagesUrl"
    $allSolutions = (Invoke-RestMethod -Method "Get" -Uri $packagesUrl -Headers $authHeader ).value
    Write-Verbose -Message "Number of Solutions found: $(($allSolutions).Count)"; "Number of Solutions found: $(($allSolutions).Count)" | Out-File $oLogFile -Append
    
    # List all Analytic Rule Templates which are part of the installed solutions
    $templatesUrl = $baseUri + "/providers/Microsoft.SecurityInsights/contentTemplates?api-version=2023-05-01-preview&%24filter=(properties%2FcontentKind%20eq%20'AnalyticsRule')"
    #Write-Debug "templatesUrl: $templatesUrl"
    $allTemplates = (Invoke-RestMethod -Uri $templatesUrl -Method Get -Headers $authHeader).value
    
    Write-Verbose -Message "Number of Templates found: $(($allTemplates).Count)"; "Number of Templates found: $(($allTemplates).Count)" | Out-File $oLogFile -Append
    
    # Iterate through all the Analytic Rule Templates
    $NumberOfConsideredTemplates = 0
    $NumberOfSkippedTemplates = 0
    $NumberOfSkippedRules = 0
    $NumberOfCreatedRules = 0
    $NumberOfDeletedRules = 0
    $NumberOfUpdatedRules = 0
    $NumberOfErrors = 0
    $loopIndex = 0

    #Initializing dictionary of rules to be updated 
    $allRulesNeedingUpdates = $null

    foreach ($template in $allTemplates ) {
        $loopIndex++ | Out-Null
        Write-Host "Processing template ($loopIndex)/$(($allTemplates).Count)..."
        $NumberOfConsideredTemplates++ | out-null

        # If the Template should be filtered by display name, do it now 
        if((-not($null -eq $filterByTemplateDisplayName)) -and (-not($filterByTemplateDisplayName.Contains($(($template).properties.displayName))))){
            Write-Verbose "Template skipped (display name not in the input CSV file): '$(($template).properties.displayName)'" 
            "Template skipped (display name not in the input CSV file): '$(($template).properties.displayName)'" | Out-File $oLogFile -Append
            $NumberOfSkippedTemplates++ | out-null
            continue #goto next Template in the foreach loop
        }

        # Make sure that the Template's severity is one we want to include
        $severity = $template.properties.mainTemplate.resources.properties[0].severity
        if ( ($SeveritiesToInclude.Contains($severity)) -or ($Mode -eq ([ExecutionMode]::GetTemplates)) -or ($Mode -eq ([ExecutionMode]::GetRules)) ) {
            try {                

                if( ($Mode -eq ([ExecutionMode]::NewRules)) -or ($Mode -eq ([ExecutionMode]::GetTemplates)) ) {
                    #Check if at least an Analytic Rule associated to this templates already exists. 
                    Write-Verbose "Template: '$(($template).properties.displayName)' - Searching for existing rules..." 
                    $found = CheckIfAnAnalyticRuleAssociatedToTemplateExist -AuthHeader $authHeader -BaseUri $baseUri -Template $template
                    if(($found) -and ($Mode -ne ([ExecutionMode]::GetTemplates))  -and ($Mode -ne ([ExecutionMode]::GetRules))   ){
                        Write-Verbose "Template '$(($template).properties.displayName)' - A rule already exists based on this template"                 
                        "Template '$(($template).properties.displayName)' - A rule already exists based on this template"  | Out-File $oLogFile -Append
                        $NumberOfSkippedTemplates++ | out-null

                        #No need to find all the rules associated to this template: the evidence that at least one exists is enough to understand that no new rules should be created for this template
                        continue #goto next Template in the foreach loop
                    }
                }

                # Search for the solution containing the Template
                Write-Verbose "Template: '$(($template).properties.displayName)' - Searching for the solution containing the template..." 
                $solution = $allSolutions.properties | Where-Object -Property "contentId" -Contains $template.properties.packageId
                #Write-Debug "solution: $solution"

                if($null -eq $solution){
                    Write-Verbose "Template '$(($template).properties.displayName)' - UNEXPECTED: solution not found"        
                    "Template '$(($template).properties.displayName)' - UNEXPECTED: solution not found" | Out-File $oLogFile -Append
                
                    $NumberOfErrors++ | out-null
                    continue #goto next Template in the foreach loop
                }

                if($Mode -eq ([ExecutionMode]::GetTemplates)){                 
                    # Write Template info in CSV file   
                    $(($template).properties.displayName),$severity,$found,$(($solution).displayName) -join $CsvSeparatorChar | Out-File $OutputAnalyticRuleTemplatesCsvFile -Append
                    continue #goto next Template in the foreach loop
                }        

                if($Mode -eq ([ExecutionMode]::GetRules)){  
                    # Search for any existing Rule associated to this Template. If the Rule require update, add it to the dictionary of Rules requiring updates               
                    $rulesAssociatedToThisTemplate = $null
                    $rulesAssociatedToThisTemplate = GetAnalyticRulesAssociatedToTemplate -AuthHeader $authHeader -BaseUri $baseUri -Template $template
                    
                    if($null -ne $rulesAssociatedToThisTemplate){
                        if($null -eq $allRulesNeedingUpdates){
                            $allRulesNeedingUpdates = New-Object 'System.Collections.Generic.Dictionary[String,System.Collections.ArrayList]'
                        }
                        $allRulesNeedingUpdates.Add(($template).properties.displayName,$rulesAssociatedToThisTemplate)

                        # Write Rules info in CSV file  
                        $rulesAssociatedToThisTemplate.ForEach({
                            if(-not([string]::IsNullOrEmpty(($_).properties.displayName))){
                                $toBeUpdated = IsFirstVersionLowerThanSecondVersion -v1 ($_).properties.templateVersion -v2 $template.properties.version
            
                                (($_).properties.displayName),(($_).name),(($_).properties.enabled),$toBeUpdated,(($_).properties.templateVersion),$(($solution).displayName),$(($template).properties.displayName),$severity,$(($template).properties.version) -join $CsvSeparatorChar | Out-File $OutputRulesCsvFile -Append
                            }                           
                        }) 
                    } 
                    continue #goto next Template in the foreach loop
                }        

                if($Mode -eq [ExecutionMode]::NewRules){                
                    # Create the Analytic Rule from the Template - NOTE: at this point it will have "Source name" = "Gallery Content"
                    Write-Verbose "Template '$(($template).properties.displayName)' - About to create rule"
                    $analyticRule = CreateAnalyticRule -AuthHeader $authHeader -BaseUri $baseUri -Template $template -SimulateOnly $SimulateOnly
                    #Write-Debug "analyticRule: $analyticRule"
                    "Template '$(($template).properties.displayName)' - Rule created sucessfully"  | Out-File $oLogFile -Append
                    
                    if($SimulateOnly){
                        # Simulate the result of the above command (it is needed in order to simulate the following command)
                        Write-Verbose "Template '$(($template).properties.displayName)' - SIMULATED - Creating a fake rule"
                        $analyticRule = New-Object -TypeName PSObject -Property @{
                            name = ""
                            id = ""
                            displayName = $template.properties.mainTemplate.resources.properties[0].displayName
                        }                    
                    }

                    # Modify the metadata of the Analytic Rule so that it is linked as "In use" in the Solution - NOTE: at this point it will have "Source name" = <Name of the solution>
                    Write-Verbose "Template '$(($template).properties.displayName)' - About to modify metadata"
                    LinkAnalyticRuleToSolution -AuthHeader $authHeader -BaseUri $baseUri -Rule $analyticRule -Template $template -Solution $solution -SimulateOnly $SimulateOnly
                    #Write-Debug "metadataChangeResult: $metadataChangeResult"
                    "Template '$(($template).properties.displayName)' - Metadata modified successfully"  | Out-File $oLogFile -Append

                    $NumberOfCreatedRules++ | out-null
                }

                if($Mode -eq [ExecutionMode]::BackupRules){   
                    # Backup the Analytic Rules
                    
                    $rulesAssociatedToThisTemplate = $null
                    $rulesAssociatedToThisTemplate = GetAnalyticRulesAssociatedToTemplate -AuthHeader $authHeader -BaseUri $baseUri -Template $template

                    if($null -eq $rulesAssociatedToThisTemplate){
                        Write-Verbose "Template skipped (no rules exist): '$(($template).properties.displayName)'" 
                        "Template skipped (no rules exist): '$(($template).properties.displayName)'" | Out-File $oLogFile -Append
                        $NumberOfSkippedTemplates++ | out-null                        
                    }
                    else{
                        $rulesAssociatedToThisTemplate.ForEach({

                            if(-not([string]::IsNullOrEmpty(($_).properties.displayName))){

                                if((-not($null -eq $filterByRuleID)) -and (-not($filterByRuleID.Contains( (($_).name) )))){
                                    Write-Verbose "Rule skipped (ID not in the input CSV file): '$(($_).properties.displayName)','$(($_).name)','$(($template).properties.displayName)'" 
                                    "Rule skipped (ID not in the input CSV file): '$(($_).properties.displayName)','$(($_).name)','$(($template).properties.displayName)'" | Out-File $oLogFile -Append
                                    $NumberOfSkippedRules++ | out-null
                                } else {
                                    
                                    if(-not([string]::IsNullOrEmpty($BackupFolder))){
                                        try {
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Backup - About to backup the rule"  | Out-File $oLogFile -Append
                                            $ruleFilePath = Join-Path -Path $BackupFolder -ChildPath "$(($_).name)_$LogStartTime.json"
                                            ExportAnalyticRulesAsArmTemplate -Rule $_ -filePath $ruleFilePath                                            
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Backup - Rule backup completed sucessfully"  | Out-File $oLogFile -Append                              
                                        }
                                        catch {
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Backup - Backup step - ERROR "  | Out-File $oLogFile -Append
                                            "-------------"  | Out-File $oLogFile -Append
                                            $_  | Out-File $oLogFile -Append
                                            "-------------"  | Out-File $oLogFile -Append
                                            $NumberOfErrors++ | out-null
                                        }
                                    }                                                                        
                                }                                                                                                                                                            
                            }
                        })
                    }                    
                }

                if($Mode -eq [ExecutionMode]::DeleteRules){   
                    # Delete the Analytic Rules
                    
                    $rulesAssociatedToThisTemplate = $null
                    $rulesAssociatedToThisTemplate = GetAnalyticRulesAssociatedToTemplate -AuthHeader $authHeader -BaseUri $baseUri -Template $template

                    if($null -eq $rulesAssociatedToThisTemplate){
                        Write-Verbose "Template skipped (no rules exist): '$(($template).properties.displayName)'" 
                        "Template skipped (no rules exist): '$(($template).properties.displayName)'" | Out-File $oLogFile -Append
                        $NumberOfSkippedTemplates++ | out-null                        
                    }
                    else{
                        $rulesAssociatedToThisTemplate.ForEach({

                            if(-not([string]::IsNullOrEmpty(($_).properties.displayName))){

                                if((-not($null -eq $filterByRuleID)) -and (-not($filterByRuleID.Contains( (($_).name) )))){
                                    Write-Verbose "Rule skipped (ID not in the input CSV file): '$(($_).properties.displayName)','$(($_).name)','$(($template).properties.displayName)'" 
                                    "Rule skipped (ID not in the input CSV file): '$(($_).properties.displayName)','$(($_).name)','$(($template).properties.displayName)'" | Out-File $oLogFile -Append
                                    $NumberOfSkippedRules++ | out-null
                                } else {
                                    $backupError = $true
                                    if([string]::IsNullOrEmpty($BackupFolder)){
                                        $backupError = $false
                                    }
                                    else{
                                        try {
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Delete - About to backup the rule"  | Out-File $oLogFile -Append
                                            $ruleFilePath = Join-Path -Path $BackupFolder -ChildPath "$(($_).name)_$LogStartTime.json"
                                            ExportAnalyticRulesAsArmTemplate -Rule $_ -filePath $ruleFilePath                                            
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Delete - Rule backup completed sucessfully"  | Out-File $oLogFile -Append
                                            $backupError = $false                                    
                                        }
                                        catch {
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Delete - Backup step - ERROR "  | Out-File $oLogFile -Append
                                            "-------------"  | Out-File $oLogFile -Append
                                            $_  | Out-File $oLogFile -Append
                                            "-------------"  | Out-File $oLogFile -Append
                                            $NumberOfErrors++ | out-null
                                        }
                                    }                                    
                                    
                                    if(-not($backupError)){
                                        Write-Verbose "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Delete - About to delete rule"
                                        try {
                                            DeleteRule -AuthHeader $authHeader -BaseUri $BaseUri -Rule ($_) -SimulateOnly $SimulateOnly
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Delete - Rule deleted sucessfully"  | Out-File $oLogFile -Append
                                            $NumberOfDeletedRules++ | Out-Null
                                        }
                                        catch {
                                            "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Delete - ERROR "  | Out-File $oLogFile -Append
                                            "-------------"  | Out-File $oLogFile -Append
                                            $_  | Out-File $oLogFile -Append
                                            "-------------"  | Out-File $oLogFile -Append
                                            $NumberOfErrors++ | out-null
                                        } 
                                    }  
                                }                                                                                                                                                            
                            }
                        })
                    }                    
                }

                if($Mode -eq [ExecutionMode]::UpdateRules){   
                    # Delete the Analytic Rules
                    
                    $rulesAssociatedToThisTemplate = $null
                    $rulesAssociatedToThisTemplate = GetAnalyticRulesAssociatedToTemplate -AuthHeader $authHeader -BaseUri $baseUri -Template $template

                    if($null -eq $rulesAssociatedToThisTemplate){
                        Write-Verbose "Template skipped (no rules exist): '$(($template).properties.displayName)'" 
                        "Template skipped (no rules exist): '$(($template).properties.displayName)'" | Out-File $oLogFile -Append
                        $NumberOfSkippedTemplates++ | out-null                        
                    }
                    else{
                        $rulesAssociatedToThisTemplate.ForEach({

                            if(-not([string]::IsNullOrEmpty(($_).name))){

                                if((-not($null -eq $filterByRuleID)) -and (-not($filterByRuleID.Contains( (($_).name) )))){
                                    Write-Verbose "Rule skipped (ID not in the input CSV file): '$(($_).properties.displayName)','$(($_).name)','$(($template).properties.displayName)'" 
                                    "Rule skipped (ID not in the input CSV file): '$(($_).properties.displayName)','$(($_).name)','$(($template).properties.displayName)'" | Out-File $oLogFile -Append
                                    $NumberOfSkippedRules++ | out-null
                                } else {
                                    $toBeUpdated = IsFirstVersionLowerThanSecondVersion -v1 ($_).properties.templateVersion -v2 $template.properties.version
                                    if(-not($toBeUpdated)){
                                        Write-Verbose "Rule skipped (update not needed): '$(($_).properties.displayName)','$(($_).name)','$(($_).properties.templateVersion)','$(($template).properties.displayName)','$($template.properties.version)'" 
                                        "Rule skipped (update not needed): '$(($_).properties.displayName)','$(($_).name)','$(($_).properties.templateVersion)','$(($template).properties.displayName)','$($template.properties.version)'" | Out-File $oLogFile -Append
                                        $NumberOfSkippedRules++ | out-null
                                    }
                                    else{
    
                                        #Update Rule section: Backup, Delete, Re-Create
                                        $backupError = $true
                                        if([string]::IsNullOrEmpty($BackupFolder)){
                                            $backupError = $false
                                        }
                                        else{
                                            try {
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - About to backup the rule"  | Out-File $oLogFile -Append
                                                $ruleFilePath = Join-Path -Path $BackupFolder -ChildPath "$(($_).name)_$LogStartTime.json"
                                                ExportAnalyticRulesAsArmTemplate -Rule $_ -filePath $ruleFilePath
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Rule backup completed sucessfully"  | Out-File $oLogFile -Append
                                                $backupError = $false                                    
                                            }
                                            catch {
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Backup step - ERROR "  | Out-File $oLogFile -Append
                                                "-------------"  | Out-File $oLogFile -Append
                                                $_  | Out-File $oLogFile -Append
                                                "-------------"  | Out-File $oLogFile -Append
                                                $NumberOfErrors++ | out-null
                                            }
                                        }                                    
                                        
                                        if(-not($backupError)){
                                            Write-Verbose "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - About to update rule in two steps: delete the old one, add the updated one"
                                            try {
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - About to delete the rule"  | Out-File $oLogFile -Append
                                                DeleteRule -AuthHeader $authHeader -BaseUri $BaseUri -Rule ($_) -SimulateOnly $SimulateOnly
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Rule deleted sucessfully"  | Out-File $oLogFile -Append                                    
                                            }
                                            catch {
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Delete step - ERROR "  | Out-File $oLogFile -Append
                                                "-------------"  | Out-File $oLogFile -Append
                                                $_  | Out-File $oLogFile -Append
                                                "-------------"  | Out-File $oLogFile -Append
                                                $NumberOfErrors++ | out-null
                                            }
                                            
                                            try {
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - About to recreate the rule"  | Out-File $oLogFile -Append
                                                # Create the Analytic Rule from the Template - NOTE: at this point it will have "Source name" = "Gallery Content"
                                                Write-Verbose "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - About to recreate the rule"
                                                $analyticRule = CreateAnalyticRule -AuthHeader $authHeader -BaseUri $baseUri -Template $template -SimulateOnly $SimulateOnly
                                                #Write-Debug "analyticRule: $analyticRule"
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Rule recreated sucessfully"  | Out-File $oLogFile -Append
                                                
                                                if($SimulateOnly){
                                                    # Simulate the result of the above command (it is needed in order to simulate the following command)
                                                    $analyticRule = ($_)
                                                }
            
                                                # Modify the metadata of the Analytic Rule so that it is linked as "In use" in the Solution - NOTE: at this point it will have "Source name" = <Name of the solution>
                                                Write-Verbose "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - About to modify metadata"
                                                LinkAnalyticRuleToSolution -AuthHeader $authHeader -BaseUri $baseUri -Rule $analyticRule -Template $template -Solution $solution -SimulateOnly $SimulateOnly
                                                #Write-Debug "metadataChangeResult: $metadataChangeResult"
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Rule metadata modified sucessfully"  | Out-File $oLogFile -Append                                    
                                            }
                                            catch {
                                                "Template '$(($template).properties.displayName)' - Rule '$(($_).name)' / '$(($_).properties.displayName)' - Update - Re-create step - ERROR "  | Out-File $oLogFile -Append
                                                "-------------"  | Out-File $oLogFile -Append
                                                $_  | Out-File $oLogFile -Append
                                                "-------------"  | Out-File $oLogFile -Append
                                                $NumberOfErrors++ | out-null
                                            }
            
                                            $NumberOfUpdatedRules++ | out-null
                                        }
                                    }
                                }
                            }
                        })
                    }                    
                }
            }
            catch {
                "Template '$(($template).properties.displayName)' - ERROR "  | Out-File $oLogFile -Append
                "-------------"  | Out-File $oLogFile -Append
                $_  | Out-File $oLogFile -Append
                "-------------"  | Out-File $oLogFile -Append
                $NumberOfErrors++ | out-null
            }
            
            if(($LimitToMaxNumberOfRules -gt 0) -and ( ($NumberOfCreatedRules -ge $LimitToMaxNumberOfRules) -or ($NumberOfDeletedRules -ge $LimitToMaxNumberOfRules)  -or ($NumberOfUpdatedRules -ge $LimitToMaxNumberOfRules))){
                break
            }
        } else {
            Write-Verbose "Template skipped (severity: '$severity'): '$(($template).properties.displayName)'" 
            "Template skipped (severity: '$severity'): '$(($template).properties.displayName)'" | Out-File $oLogFile -Append
            $NumberOfSkippedTemplates++ | out-null
        }
    }
    
    ######## Final logs and messages

    if($null -ne $allRulesNeedingUpdates){
        Write-Host (" ") ; " " | Out-File $oLogFile -Append
        Write-Host ("### Rules to be updated:") -ForegroundColor Blue
        $allRulesNeedingUpdates.Keys.ForEach({
            Write-Host " "
            Write-Host "......................................................."
            Write-Host "Template: $_"
            Write-Host "Rules:"
            $allRulesNeedingUpdates[$_].ForEach({
                if(-not([string]::IsNullOrEmpty(($_).properties.displayName))){
                    Write-Host "> " ($_).properties.displayName
                }                
            })
        })
        Write-Host "......................................................."
        Write-Host (" ") ; " " | Out-File $oLogFile -Append
    }

    Write-Host (" ") ; " " | Out-File $oLogFile -Append
    Write-Host ("### Summary:") -ForegroundColor Blue; "### Summary:"  | Out-File $oLogFile -Append
    Write-Host ("") -ForegroundColor Blue
    Write-Host ("  # of templates processed: $NumberOfConsideredTemplates")  -ForegroundColor Blue; "  # of templates processed: $NumberOfConsideredTemplates" | Out-File $oLogFile -Append
    if( ($Mode -eq ([ExecutionMode]::GetTemplates)) -or ($Mode -eq ([ExecutionMode]::GetRules)) ) {
        Write-Host ("  # of templates processed with errors: $NumberOfErrors")  -ForegroundColor Red; "  # of rules processed with errors: $NumberOfErrors" | Out-File $oLogFile -Append        
    } elseif ($Mode -eq ([ExecutionMode]::NewRules)) { 
        if(-not($SimulateOnly)){
            Write-Host ("  # of rules created: $NumberOfCreatedRules")  -ForegroundColor Green; "  # of rules created: $NumberOfCreatedRules" | Out-File $oLogFile -Append
        } else {        
            Write-Host ("  # of rules created (SIMULATED): $NumberOfCreatedRules")  -ForegroundColor Green; "  # of rules created (SIMULATED): $NumberOfCreatedRules" | Out-File $oLogFile -Append
        }
        Write-Host ("  # of rules not created because of errors: $NumberOfErrors")  -ForegroundColor Red; "  # of rules not created because of errors: $NumberOfErrors" | Out-File $oLogFile -Append
    }elseif ($Mode -eq ([ExecutionMode]::DeleteRules)) { 
        if(-not($SimulateOnly)){
            Write-Host ("  # of rules deleted: $NumberOfDeletedRules")  -ForegroundColor Green; "  # of rules deleted: $NumberOfDeletedRules" | Out-File $oLogFile -Append
        } else {        
            Write-Host ("  # of rules deleted (SIMULATED): $NumberOfDeletedRules")  -ForegroundColor Green; "  # of rules deleted (SIMULATED): $NumberOfDeletedRules" | Out-File $oLogFile -Append
        }
        Write-Host ("  # of rules not deleted because of errors: $NumberOfErrors")  -ForegroundColor Red; "  # of rules not deleted because of errors: $NumberOfErrors" | Out-File $oLogFile -Append
    }elseif ($Mode -eq ([ExecutionMode]::UpdateRules)) { 
        if(-not($SimulateOnly)){
            Write-Host ("  # of rules updated: $NumberOfUpdatedRules")  -ForegroundColor Green; "  # of rules updated: $NumberOfUpdatedRules" | Out-File $oLogFile -Append
        } else {        
            Write-Host ("  # of rules updated (SIMULATED): $NumberOfUpdatedRules")  -ForegroundColor Green; "  # of rules updated (SIMULATED): $NumberOfUpdatedRules" | Out-File $oLogFile -Append
        }
        Write-Host ("  # of rules not updated because of errors: $NumberOfErrors")  -ForegroundColor Red; "  # of rules not updated because of errors: $NumberOfErrors" | Out-File $oLogFile -Append
    }
    Write-Host ("  # of templates skipped: $NumberOfSkippedTemplates")  -ForegroundColor Gray; "  # of template skipped: $NumberOfSkippedTemplates" | Out-File $oLogFile -Append
    Write-Host ("  # of rules skipped: $NumberOfSkippedRules")  -ForegroundColor Gray; "  # of rules skipped: $NumberOfSkippedRules" | Out-File $oLogFile -Append
    Write-Host ("") -ForegroundColor Blue
    Write-Host "Please check the log file for details: '.\$oLogFile'" -ForegroundColor Blue 
    $LogEndTime = Get-Date -Format "yyyy-MM-dd_hh.mm.ss"    
    Write-Verbose "---------------------- EXECUTION COMPLETE - $(Get-Date)"; "---------------------- EXECUTION COMPLETE - $LogEndTime" | Out-File $oLogFile -Append
}




##################################################################################################
#
# >> LAUNCHING SECTION << 
#
# CONSIDER THIS SECTION AS A SET OF EXAMPLES ON HOW TO CALL THE DIFFERENT CMDLETs
# 
# BEFORE LAUNCHING, set the all the parameters according to your environment and needs! 
# 
# --> Step 1: Set the common environment parameter and chose the cmdlet to be executed
# 
# --> Step 2: Set the input parameter specific for the chosen cmdlet
# 
##################################################################################################


# --> Step 1. SET THE COMMON ENVIRONMENT PARAMETER AND THE CHOOSE THE CMDLET BY SETTING THE "EXECUTION MODE" VARIABLE 

$SubscriptionId = "<your-subscription-id>" # Mandatory (GUID as string)
$ResourceGroup = "<your-sentinel-resource-group>" # Mandatory (string)
$Workspace = "<your-sentinel-workspace>" # Mandatory (string)
$Region = "<your-sentinel-region>" # Mandatory (string) - E.g.: westeurope
$CsvSeparatorChar = $null # Optional (char) - Default: separator for the local culture - E.g. ';'

$execMode = $null # Set as "safe default" --> When launching the script without setting $execMode, nothing happens!

# IMPORTANT: uncomment (only!) one of the following five lines for setting the desired execution mode (the last one uncommented will be executed!)
#$execMode = [ExecutionMode]::GetTemplates   # Set the additional parameters for Get-SentinelTemplates (see below)
#$execMode = [ExecutionMode]::GetRules      # Set the additional parameters for Get-SentinelRules (see below)
#$execMode = [ExecutionMode]::NewRules      # Set the additional parameters for New-SentinelRules (see below)
#$execMode = [ExecutionMode]::BackupRules   # Set the additional parameters for Remove-SentinelRules (see below)
#$execMode = [ExecutionMode]::DeleteRules   # Set the additional parameters for Remove-SentinelRules (see below)
#$execMode = [ExecutionMode]::UpdateRules   # Set the additional parameters for Update-SentinelRules (see below)


# --> Step 2. SET THE SPECIFIC PARAMETER FOR THE CHOOSEN CMDLET (EXECUTION MODE)

######################## --> Execution Mode: GetTemplates
# The Get-SentinelTemplates cmdlet exports in a CSV file the details of the Analytic Rules Templates existing in the workspace. 
# NOTE: the cmdlet considers only the Templates installed by Content Hub Solutions. 
#       Templates installed directly from the gallery (old approach in Sentinel) are ignored. 
########################
$OutputAnalyticRuleTemplatesCsvFile = "<path-to-templates-csv-file>" # Mandatory (string) - File local full path 

if(($execMode) -eq ([ExecutionMode]::GetTemplates)){ 
    Get-SentinelTemplates -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region `
        -OutputAnalyticRuleTemplatesCsvFile $OutputAnalyticRuleTemplatesCsvFile -CsvSeparatorChar $CsvSeparatorChar 
}

######################## --> Execution Mode: GetRules
# The Get-SentinelRules cmdlet exports in a CSV file the details of the Analytic Rules that have been created in the workspace.
# NOTE: the script considers only the Rules created from the Templates installed by Content Hub Solutions. 
########################
$OutputRulesCsvFile = "<path-to-rules-csv-file>" # Mandatory (string) - File local full path

if(($execMode) -eq ([ExecutionMode]::GetRules)){ 

    Get-SentinelRules -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
        -OutputRulesCsvFile $OutputRulesCsvFile -CsvSeparatorChar $CsvSeparatorChar 

}

######################## --> Execution Mode: NewRules
# The New-SentinelRules cmdlet creates one Analytic Rule for each of the Templates identified by the input parameters.
# NOTES:
#  - The execution can be simulated (no Rules are created but their simulated creation is traced in the log file)
#  - No Rules are created for the Templates that have already at least a Rule associated
#  - The Templates to be considered can be filtered by Severity (one or more) and/or by DisplayNames (in an input CSV file)
#  - The (optional) input CSV file can be created starting from the result of Get-SentinelTemplates 
#  - The execution can be interrupted after a maximum number of Rules created (useful for testing purposes)
#
# IMPORTANT: before launching the New-SentinelRules cmdlet, it is recommended to update all the relevant Solutions in Content Hub.
######################## 
$SimulateOnly = $true # Optional (boolean) - Default value: $false (Pay attention!)
$LimitToMaxNumberOfRules = 1 # Optional (integer) - Use $null or a negative number for unlimited execution
$InputCsvFile = "<path-to-input-template-csv-file>" # Optional (string) - File local full path
$SeveritiesToInclude = @("Low") # Optional (array of strings) - Default: @("Informational", "Low", "Medium", "High")

if(($execMode) -eq ([ExecutionMode]::NewRules)){ 

    New-SentinelRules -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
        -Simulate $SimulateOnly -LimitToMaxNumberOfRules $LimitToMaxNumberOfRules   `
        -InputCsvFile $InputCsvFile -CsvSeparatorChar $CsvSeparatorChar   `
        -SeveritiesToInclude $SeveritiesToInclude #-verbose

}

######################## --> Execution Mode: BackupRules
# The Export-SentinelRules cmdlet saves the json files of the Rules associated to the Templates identified by one or more Severity values.
# NOTES:
#  - The Templates to be considered can be filtered by Severity (one or more). 
#    If not filtered, all the "installed Templates" will be considered (the installed Templates are the ones of the installed Content Hub Solutions)
#  - It is necessary to specify a folder where the script has to backup (as json ARM template) the Rules.
#
######################## 
$BackupFolder = "<path-to-backup-folder>" # Mandatory (string) - Full path of a local existing folder
$SeveritiesToInclude = $null # @("Low","Medium") # Optional (array of strings) - Default: @("Informational", "Low", "Medium", "High")

if(($execMode) -eq ([ExecutionMode]::BackupRules)){ 

    Export-SentinelRules -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
        -BackupFolder $BackupFolder   `
        -SeveritiesToInclude $SeveritiesToInclude #-verbose

}

######################## --> Execution Mode: DeleteRules
# The Remove-SentinelRules cmdlet deletes all or some of the Analytic Rules for each of the Templates identified by one or more Severity values.
# NOTES:
#  - The execution can be simulated (no Rules are deleted but their simulated deletion is traced in the log file)
#  - The Templates to be considered can be filtered by Severity (one or more). 
#    If not filtered, all the "installed Templates" will be considered (the installed Templates are the ones of the installed Content Hub Solutions)
#  - The Rules to be considered for each of these Templates can be filtered by their ID (in the input CSV file)
#    If not filtered, all the "existing Rules" for these Templates will be considered (the existing Rules are the ones referring to these Templates)
#  - The (optional) input CSV file can be created starting from the result of Get-SentinelRules
#  - The execution can be interrupted after a maximum number of Rules deleted (useful for testing purposes)
#  - It is possible to specify a folder where the script has to backup (as json ARM template) the Rules before their deletion.
#    In that case, if the backup of a Rule fails for any reason, the Rule is not deleted. 
#
# IMPORTANT: it is highly recommended to pass the optional input CSV file as parameter to have a better control 
#            on what will be deleted! 
######################## 
$SimulateOnly = $true # Optional (boolean) - Default value: $false (Pay attention!)
$LimitToMaxNumberOfRules = $null # Optional (integer) - Use $null or a negative number for unlimited execution
$BackupFolder = "<path-to-backup-folder>" # Mandatory (string) - Full path of a local existing folder
$InputCsvFile = "<path-to-input-rules-csv-file>" # Optional (string) - File local full path
$SeveritiesToInclude = @("Low","Medium") # Optional (array of strings) - Default: @("Informational", "Low", "Medium", "High")

if(($execMode) -eq ([ExecutionMode]::DeleteRules)){ 

    Remove-SentinelRules -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
        -Simulate $SimulateOnly -LimitToMaxNumberOfRules $LimitToMaxNumberOfRules   `
        -BackupFolder $BackupFolder   `
        -InputCsvFile $InputCsvFile -CsvSeparatorChar $CsvSeparatorChar   `
        -SeveritiesToInclude $SeveritiesToInclude #-verbose

}


######################## --> Execution Mode: UpdateRules
# The Update-SentinelRules cmdlet updates all or some of the Analytic Rules for each of the Templates identified by one or more Severity values.
# NOTES:
#  - The execution can be simulated (no Rules are updated but their simulated update is traced in the log file)
#  - The Templates to be considered can be filtered by Severity (one or more) 
#    If not filtered, all the "installed Templates" will be considered (the installed Templates are the ones of the installed Content Hub Solutions)
#  - The Rules to be considered for each of these Templates can be filtered by their ID (in the input CSV file)
#    If not filtered, all the "existing Rules" for these Templates will be considered (the existing Rules are the ones referring to these Templates)
#  - The execution can be interrupted after a maximum number of Rules updated (useful for testing purposes)
#  - The update is practically executed as a sequence of a delete of the existing Rule and a creation of the new Rule based
#    on the updated version of the same Template.
#  - It is possible to specify a folder where the script has to backup (as json ARM template) the Rules before their deletion (update).
#    In that case, if the backup of a Rule fails for any reason, the Rule is not deleted (updated). 
#
# IMPORTANT: it is highly recommended to pass the optional input CSV file as parameter to have a better control 
#            on what will be updated! 
#
# SUPER IMPORTANT: if you need to update a Rule that you have customized somehow, you should keep track of your customizations 
#                  becase you'll need to re-apply them manually. 
#                  In that case, you can specify the backup folder so that you have also a backup of the Rulesfrom the script.
#                  DO NOT UPDATE CUSTOMIZED RULES IF YOU DO NOT HAVE A BACKUP OF YOUR CUSTOMIZATION!
########################  
$SimulateOnly = $true # Optional (boolean) - Default value: $false (Pay attention!)
$LimitToMaxNumberOfRules = $null # Optional (integer) - Use $null or a negative number for unlimited execution
$BackupFolder = "<path-to-backup-folder>" # Mandatory (string) - Full path of a local existing folder
$InputCsvFile = "<path-to-input-rules-csv-file>" # Optional (string) - File local full path
$SeveritiesToInclude = @("Medium") # Optional (array of strings) - Default: @("Informational", "Low", "Medium", "High")

if(($execMode) -eq ([ExecutionMode]::UpdateRules)){ 

    Update-SentinelRules -SubscriptionId $SubscriptionId -ResourceGroup $ResourceGroup -Workspace $Workspace -Region $Region  `
        -Simulate $SimulateOnly -LimitToMaxNumberOfRules $LimitToMaxNumberOfRules   `
        -BackupFolder $BackupFolder   `
        -InputCsvFile $InputCsvFile -CsvSeparatorChar $CsvSeparatorChar   `
        -SeveritiesToInclude $SeveritiesToInclude #-verbose

}
