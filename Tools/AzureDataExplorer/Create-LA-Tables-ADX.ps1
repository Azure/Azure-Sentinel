<#       
  	THE SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

    .SYNOPSIS
        This PowerShell script integrates given Log Analytics Workspace tables data into Azure Data Explorer for long term retention. 
        For more information on how to use this script please visit: https://github.com/Azure/Azure-Sentinel/tree/master/Tools/AzureDataExplorer

    .DESCRIPTION
        It performs the following actions:
            1. Queries the Log Analytics workspace tables.
            2. Validates table names against data export supported tables AdxSupportedTables.json.
            3. Creates target Table, Raw and Mapping in Azure Data Explorer.         
    
    .PARAMETER LogAnalyticsWorkSpaceName
        Enter the Log Analytics workspace name (required)
    
    .PARAMETER LogAnalyticsResourceGroupName
        Enter the Resource Group name of Log Analytics workspace (required)

    .PARAMETER AdxResourceGroupName
        Enter the Resource Group name of Azure Data Explorer (ADX) (required)

    .PARAMETER AdxClusterURL
        Enter the Resource Group name of Azure Data Explorer (ADX) Cluster URL (required)

    .PARAMETER AdxDatabaseName
        Enter the Resource Group name of Azure Data Explorer (ADX) Database Name (required)

    .NOTES
        AUTHOR: Sreedhar Ande
        LASTEDIT: 25 August 2021

    .EXAMPLE
        .\Create-LA-Tables-ADX.ps1 -LogAnalyticsResourceGroup la-resgrp1 -LogAnalyticsWorkspaceName la-workspace-1 `
        -AdxResourceGroup adx-resgrp1 -AdxClusterURL "https://adxcluster1.eastus2.kusto.windows.net" -AdxDBName AdxClusterDb1
#>

#region UserInputs

param(
    [parameter(Mandatory = $true, HelpMessage = "Enter the resource group location for the Log Analytics workspace.")]
    [string]$LogAnalyticsResourceGroup,

    [parameter(Mandatory = $true, HelpMessage = "Enter the Log Analytics workspace name from which to export data.")]
    [string]$LogAnalyticsWorkspaceName,

    [parameter(Mandatory = $true, HelpMessage = "Enter the resource group location for the existing Azure Data Explorer (ADX) cluster for which to export data.")]
    [string]$AdxResourceGroup,

    [parameter(Mandatory = $true, HelpMessage = "Enter the Azure Data Explorer (ADX) cluster URL.")]
    [string]$AdxClusterURL,

    [parameter(Mandatory = $true, HelpMessage = "Enter the Azure Data Explorer (ADX) cluster database name.")]
    [string]$AdxDBName
) 

#endregion UserInputs
      
#region StaticValues

[string]$AdxEngineUrl = "$AdxClusterURL/$AdxDBName"
[string]$KustoToolsPackage = "microsoft.azure.kusto.tools"
[string]$KustoConnectionString = "$AdxEngineUrl;Fed=True"
[string]$NuGetIndex = "https://api.nuget.org/v3/index.json"
[string]$NuGetDownloadUrl = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
[string]$nugetPackageLocation = "$($env:USERPROFILE)\.nuget\packages"

#endregion StaticValues

#region HelperFunctions

function Write-Log {
    <#
    .DESCRIPTION 
    Write-Log is used to write information to a log file and to the console.
    
    .PARAMETER Severity
    parameter specifies the severity of the log message. Values can be: Information, Warning, or Error. 
    #>

    [CmdletBinding()]
    param(
        [parameter()]
        [ValidateNotNullOrEmpty()]
        [string]$Message,
        [string]$LogFileName,
 
        [parameter()]
        [ValidateNotNullOrEmpty()]
        [ValidateSet('Information', 'Warning', 'Error')]
        [string]$Severity = 'Information'
    )
    # Write the message out to the correct channel											  
    switch ($Severity) {
        "Information" { Write-Host $Message -ForegroundColor Green }
        "Warning" { Write-Host $Message -ForegroundColor Yellow }
        "Error" { Write-Host $Message -ForegroundColor Red }
    } 											  
    try {
        [PSCustomObject]@{
            Time     = (Get-Date -f g)
            Message  = $Message
            Severity = $Severity
        } | Export-Csv -Path "$PSScriptRoot\$LogFileName" -Append -NoTypeInformation -Force
    }
    catch {
        Write-Error "An error occurred in Write-Log() method" -ErrorAction SilentlyContinue		
    }    
}

function Get-RequiredModules {
    <#
    .DESCRIPTION 
    Get-Required is used to install and then import a specified PowerShell module.
    
    .PARAMETER Module
    parameter specifices the PowerShell module to install. 
    #>

    [CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $Module        
    )
    
    try {
        $installedModule = Get-InstalledModule -Name $Module -ErrorAction SilentlyContinue
        if ($null -eq $installedModule) {
            Write-Log -Message "The $Module PowerShell module was not found" -LogFileName $LogFileName -Severity Warning
            #check for Admin Privleges
            $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

            if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
                #Not an Admin, install to current user            
                Write-Log -Message "Can not install the $Module module. You are not running as Administrator" -LogFileName $LogFileName -Severity Warning
                Write-Log -Message "Installing $Module module to current user Scope" -LogFileName $LogFileName -Severity Warning
                
                Install-Module -Name $Module -Scope CurrentUser -Force -AllowClobber
                Import-Module -Name $Module -Force
            }
            else {
                #Admin, install to all users																		   
                Write-Log -Message "Installing the $Module module to all users" -LogFileName $LogFileName -Severity Warning
                Install-Module -Name $Module -Force -ErrorAction continue
                Import-Module -Name $Module -Force -ErrorAction continue
            }
        }
        # Install-Module will obtain the module from the gallery and install it on your local machine, making it available for use.
        # Import-Module will bring the module and its functions into your current powershell session, if the module is installed.  
    }
    catch {
        Write-Log -Message "An error occurred in Get-RequiredModules() method" -LogFileName $LogFileName -Severity Error																			
        exit
    }
}

#endregion

#region MainFunctions

function Invoke-KustoCLI {
    <#
    .DESCRIPTION 
    Invoke-KustoCLI is used to execute the KustoCLI with the specified AdxCommandsFile.
    
    .PARAMETER AdxCommandsFile
    parameter specifices the path the the file that includes the commands to execute 
    #>

    [CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $AdxCommandsFile        
    )

    try {
        $KustoToolsDir = "$env:USERPROFILE\.nuget\packages\$KustoToolsPackage\"
        $CurrentDir = Get-Location
        Set-Location $ScriptDir
        

        if (!(Test-Path $KustoToolsDir)) {				 
            if (!(Test-Path nuget)) {
                Write-Log -Message "The NuGet module is not found" -LogFileName $LogFileName -Severity Warning                
                Write-Log -Message "Downloading NuGet package" -LogFileName $LogFileName -Severity Information
                (New-Object net.webclient).downloadFile($NuGetDownloadUrl, "$pwd\nuget.exe")
            }
            
            Write-Log -Message "Installing Kusto Tools Package" -LogFileName $LogFileName -Severity Information
            &.\nuget.exe install $kustoToolsPackage -Source $nugetIndex -OutputDirectory $nugetPackageLocation
        }

        $KustoExe = $KustoToolsDir + @(Get-ChildItem -Recurse -Path $KustoToolsDir -Name kusto.cli.exe)[-1]
        
        if (!(Test-Path $KustoExe)) {		 
            Write-Log -Message "Unable to find Kusto client tool $KustoExe. exiting" -LogFileName $LogFileName -Severity Warning
            Write-Warning "Unable to find Kusto client tool $KustoExe. exiting"
            return
        }    
        
        Write-Log -Message "Executing queries on Azure Data Explorer (ADX)" -LogFileName $LogFileName -Severity Information
        Invoke-Expression "$kustoExe `"$kustoConnectionString`" -script:$adxCommandsFile"
        Set-Location $CurrentDir								
    }
    catch {
        Write-Log -Message "An error occurred in Invoke-KustoCLI() method" -LogFileName $LogFileName -Severity Error																	  
        exit
    }
}

function New-AdxRawMappingTables {   
    <#
    .DESCRIPTION 
    New-AdxRawMappingTables is used to create raw mapping tables
    
    .PARAMETER LaTables
    Parameter specifices the Log Analytics tables to create 
    #>
    [CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $LaTables,
        [parameter(Mandatory = $true)] $LaMappingDecision        
    )

    if (!(Test-Path "$PSScriptRoot\KustoQueries" -PathType Container)) { 
        New-Item -Path $PSScriptRoot -Name "KustoQueries" -ItemType "directory"
    }    
  
    foreach ($table in $LaTables) {
        if ($LaMappingDecision -eq 0) {
            $TableName = $table.'$table'
        }
        else {
            $TableName = $table
        }                
        
        try {
            Write-Log -Message "Retrieving schema and mappings for $TableName" -LogFileName $LogFileName -Severity Information
            $query = $TableName + ' | getschema | project ColumnName, DataType'        
            $AdxTablesArray.Add($TableName.Trim())
            
            Write-Verbose "Executing: (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $query).Results"																														  
            $output = (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $query).Results

            $TableExpandFunction = $TableName + 'Expand'
            $TableRaw = $TableName + 'Raw'
            $RawMapping = $TableRaw + 'Mapping'

            $FirstCommand = @()
            $ThirdCommand = @()

            foreach ($record in $output) {
                if ($record.DataType -eq 'System.DateTime') {
                    $dataType = 'datetime'
                    $ThirdCommand += $record.ColumnName + " = todatetime(events." + $record.ColumnName + "),"
                } 
                else {
                    $dataType = 'string'
                    $ThirdCommand += $record.ColumnName + " = tostring(events." + $record.ColumnName + "),"
                }
                $FirstCommand += $record.ColumnName + ":" + "$dataType" + ","    
            }

            $schema = ($FirstCommand -join '') -replace ',$'
            $function = ($ThirdCommand -join '') -replace ',$'

            $CreateRawTable = '.create table {0} (Records:dynamic)' -f $TableRaw

            $CreateRawMapping = @'
                .create table {0} ingestion json mapping '{1}' '[{{"column":"Records","Properties":{{"path":"$.records"}}}}]'
'@ -f $TableRaw, $RawMapping

            $CreateRetention = '.alter-merge table {0} policy retention softdelete = 0d' -f $TableRaw

            $CreateTable = '.create table {0} ({1})' -f $TableName, $schema

            $CreateFunction = @'
                .create-or-alter function {0} {{{1} | mv-expand events = Records | project {2} }}
'@ -f $TableExpandFunction, $TableRaw, $function

            $CreatePolicyUpdate = @'
                .alter table {0} policy update @'[{{"Source": "{1}", "Query": "{2}()", "IsEnabled": "True", "IsTransactional": true}}]'
'@ -f $TableName, $TableRaw, $TableExpandFunction

            $scriptDir = "$PSScriptRoot\KustoQueries"
            New-Item "$scriptDir\adxCommands.txt"
            Add-Content "$scriptDir\adxCommands.txt" "`n$CreateRawTable"
            Add-Content "$scriptDir\adxCommands.txt" "`n$CreateRawMapping"
            Add-Content "$scriptDir\adxCommands.txt" "`n$CreateRetention"
            Add-Content "$scriptDir\adxCommands.txt" "`n$CreateTable"
            Add-Content "$scriptDir\adxCommands.txt" "`n$CreateFunction"
            Add-Content "$scriptDir\adxCommands.txt" "`n$CreatePolicyUpdate"
            
            try {         
                Invoke-KustoCLI -AdxCommandsFile "$scriptDir\adxCommands.txt"
                Remove-Item $ScriptDir\adxCommands.txt -Force -ErrorAction Ignore        
            }
            catch {        
                Write-Log -Message "An error occurred in Invoke-KustoCLI method" -LogFileName $LogFileName -Severity Error		
                exit
            }
            Write-Log -Message "Successfully created Raw and Mapping tables for: $TableName in ADX cluster database." -LogFileName $LogFileName -Severity Information
        }
        catch {
            Write-Log -Message "An error occurred in New-AdxRawMappingTables method" -LogFileName $LogFileName -Severity Error
        }
    }
} 

#endregion

#region DriverProgram

Get-RequiredModules("Az.Resources")
Get-RequiredModules("Az.OperationalInsights")

# Check Powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Log "Supported PowerShell version for this script is 5 or above" -LogFileName $LogFileName -Severity Error    
    exit
}

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "CreateADXTables", $TimeStamp

Write-Output "`n`n Starting Create-LA-Tables-ADX.ps1 at: $(Get-Date)"
Write-Output " Creating log $LogFileName"

Write-Host "`n`n`r`If not already authenticated, you will be prompted to sign in to Azure.`nMake sure that your credentials have:" -BackgroundColor Blue
Write-Host "`n > Azure Log Analytics workspace 'Read' permissions on: $($LogAnalyticsWorkspaceName)`n > Azure Data Explorer Database 'User' permissions on: $($AdxDBName). `n`nThese permissions are required for the script to read the Log Analytics workspace tables and to create tables in Azure Data Explorer.`r`n" -BackgroundColor Blue

Read-Host -Prompt "Press enter to continue or CTRL+C to exit the script."

$Context = Get-AzContext

if (!$Context) {
    Connect-AzAccount
    $Context = Get-AzContext
}

$SubscriptionId = $Context.Subscription.Id

Write-Verbose "Executing: Get-AzOperationalInsightsWorkspace -Name $LogAnalyticsWorkspaceName -ResourceGroupName $LogAnalyticsResourceGroup -DefaultProfile $context"

try {
    $WorkspaceObject = Get-AzOperationalInsightsWorkspace -Name $LogAnalyticsWorkspaceName -ResourceGroupName $LogAnalyticsResourceGroup -DefaultProfile $Context 
    $LogAnalyticsLocation = $WorkspaceObject.Location
    $LogAnalyticsWorkspaceId = $WorkspaceObject.CustomerId
    if ($null -ne $LogAnalyticsWorkspaceId) {
        Write-Log -Message "Workspace named $LogAnalyticsWorkspaceName in region $LogAnalyticsLocation exists." -LogFileName $LogFileName -Severity Information
    }
    else {            
        Write-Log -Message "$LogAnalyticsWorkspaceName not found" -LogFileName $LogFileName -Severity Error       
    } 
}
catch {    
    Write-Log -Message "Error occurred in retreiving Log Analytics workspace: $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error
}

#region ADXTableCreation

$LaTablesQuestion = "Do you want to create ADX Raw and Mapping tables for all tables in Log Analytics workspace: $($LogAnalyticsWorkspaceName)?"
$LaTablesQuestionChoices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
$LaTablesQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
$LaTablesQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

$LaTablesQuestionDecision = $Host.UI.PromptForChoice($title, $LaTablesQuestion, $LaTablesQuestionChoices, 1)

if ($LaTablesQuestionDecision -eq 0) {    
    Write-Verbose "Executing: Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $QueryAllTables" 
    
    try {       
        Write-Log -Message "Retrieving tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
        $QueryAllTables = 'search *| distinct $table| sort by $table asc nulls last'
        $ResultsAllTables = (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $QueryAllTables).Results
    }
    catch {            
        Write-Log -Message "An error occurred in querying table names from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error         
        exit
    }
} 
else {
    try {
        Write-Host "`nEnter selected Log Analytics workspace table names separated by comma (,) (Case-Sensitive)" -ForegroundColor Blue
        $UserInputTables = Read-Host 
        $ResultsAllTables = $UserInputTables.Split(',')
    }
    catch {
        Write-Log -Message "Incorrect user input! Table names must be separated by comma (,)" -LogFileName $LogFileName -Severity Error       
        exit
    }    
}

$AdxTablesArray = New-Object System.Collections.Generic.List[System.Object]    
New-AdxRawMappingTables -LaTables $ResultsAllTables -LaMappingDecision $LaTablesQuestionDecision

#endregion
