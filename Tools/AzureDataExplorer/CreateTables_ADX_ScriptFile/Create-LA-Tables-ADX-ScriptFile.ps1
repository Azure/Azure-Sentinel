
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
            2. Creates target Table, Raw and Mapping in a local text file for use in a database script.
        
        This has been written to be used in scenarios where you want to build a mapping script, rather than directly creating the tables in ADX. Consider using the generated file with
        https://learn.microsoft.com/en-us/azure/data-explorer/kusto/management/execute-database-script
    
    
    .PARAMETER LogAnalyticsWorkSpaceName
        Enter the Log Analytics workspace name (required)
    
    .PARAMETER LogAnalyticsResourceGroupName
        Enter the Resource Group name of Log Analytics workspace (required)

    .PARAMETER OnlyTablesWithData
        Create ADX Raw and Mapping tables only for tables in Log Analytics with data

    .PARAMETER TableNameList
        Enter an array of Log Analytics tables to export data from. If not provided, all tables will be exported.

    .PARAMETER OutputFolderPath
        Enter the path to the folder where the export file will be saved. Default is the script folder.

    .PARAMETER Force
        Force the script to run without user input


    .NOTES
        AUTHOR: Alistair Ross
        LASTEDIT: 25/06/2024
        Based on the original script by: Sreedhar Ande

    .EXAMPLE
       This example queries all tables using 'search *| distinct $table' and creates ADX Raw and Mapping tables for all tables with data in the Log Analytics workspace.

        .\Create-LA-Tables-ADX-ScriptFile.ps1 `
            -LogAnalyticsResourceGroup "la-resgrp1" `
            -LogAnalyticsWorkspaceName "la-workspace-1" `
            -OnlyTablesWithData `
            -OutputFolderPath "C:\Temp\ADXScript"

    .EXAMPLE
       This example queries all tables using Get-AzOperationalInsightsTable and creates ADX Raw and Mapping tables for all tables in the Log Analytics workspace.
       Using the -Force switch, it bypasses any user input, assuming that authentication has already been completed using Connect-AzAccount.

        $TablesList = @("AzureActivity", "SigninLogs")
        .\Create-LA-Tables-ADX-ScriptFile.ps1 `
            -LogAnalyticsResourceGroup "la-resgrp1" `
            -LogAnalyticsWorkspaceName "la-workspace-1" `
            -TableNameList $TablesList `
            -Force `
            -OutputFolderPath "C:\Temp\ADXScript"

    .EXAMPLE
       This example takes the tables from an array and creates ADX Raw and Mapping tables for each table in the Log Analytics workspace.
       If the table does not exist, the script does not create the ADX Raw and Mapping tables, but logs the error in the log and script file.

        $Tables = @("AzureActivity", "SigninLogs")
        .\Create-LA-Tables-ADX-ScriptFile.ps1 `
            -LogAnalyticsResourceGroup "la-resgrp1" `
            -LogAnalyticsWorkspaceName "la-workspace-1" `
            -TableNameList $Tables `
            -Force `
            -OutputFolderPath "C:\Temp\ADXScript"
#>


#region UserInputs

param(
    [parameter(Mandatory = $true, HelpMessage = "Enter the resource group location for the Log Analytics workspace.")]
    [string]$LogAnalyticsResourceGroup,

    [parameter(Mandatory = $true, HelpMessage = "Enter the Log Analytics workspace name from which to export data.")]
    [string]$LogAnalyticsWorkspaceName,

    # Only Tables with data switch
    [parameter(Mandatory = $false, HelpMessage = "Create ADX Raw and Mapping tables only for tables in Log Analytics with data")]
    [switch]$OnlyTablesWithData, 

    # Comma Seperated Tables string array
    [parameter(Mandatory = $false, HelpMessage = "Enter an array of Log Analytics tables to export data from. If not provided, all tables will be exported.")]
    [string[]]$TableNameList,

    # Output folder path. Default to script folder
    [parameter(Mandatory = $false, HelpMessage = "Enter the path to the folder where the export file will be saved. Default is the script folder.")]
    [string]$OutputFolderPath = $PSScriptRoot,

    # Force swtich
    [parameter(Mandatory = $false, HelpMessage = "Force the script to run without user input")]
    [switch]$Force
) 

#endregion UserInputs
      
#region StaticValues

$ScriptName = "Create-LA-Tables-ADX-ExportFile.ps1"
$LogDirectory = "$OutputFolderPath\Logs"
$ADXScriptDirectory = "$OutputFolderPath\ADXScripts"
$ADXCommandsScriptFileName = "adxCommandsScriptFile.txt"
$RequiredModules = @(
    "Az.Resources", 
    "Az.OperationalInsights"
)

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
        } | Export-Csv -Path "$LogDirectory\$LogFileName" -Append -NoTypeInformation -Force
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
#endregion HelperFunctions

#region MainFunctions

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
        [parameter(Mandatory = $true)] [bool]$CustomList        
    )

    if ((Test-Path "$ADXScriptDirectory\$ADXCommandsScriptFileName")) {
        try{
            #Get the exisitng file and rename it with the creation datetime
            Write-Log -Message "Renaming the existing export file" -LogFileName $LogFileName -Severity Information
            $ExistingFile = Get-Item "$ADXScriptDirectory\$ADXCommandsScriptFileName"
            # Get the content of the exisitng file and return the row that begins with //TimeGenerated:
            try{
                $ExistingFileTimeStamp = (Get-Content $ExistingFile | Select-String -Pattern "//TimeGenerated:").ToString().Split(":")[1].Trim()
            }
            catch {
                # Use the file creation time if the existing file does not have a timestamp
                $ExistingFileTimeStamp = $ExistingFile.CreationTime.ToString("yyyyMMdd_HHmmss")
            }

            $ExistingFile | Rename-Item -NewName { $_.Name -replace ".txt", "_$ExistingFileTimeStamp.txt" }
        }
        catch {
            Write-Log -Message "An error occurred in renaming the existing export file" -LogFileName $LogFileName -Severity Error
        }
        try{
            Write-Log -Message "Creating new export file" -LogFileName $LogFileName -Severity Information
            New-Item -Path $ADXScriptDirectory -Name $ADXCommandsScriptFileName -ItemType "file" -Force | out-null
            }
            catch {
                Write-Log -Message "An error occurred in creating the export file" -LogFileName $LogFileName -Severity Error
            }
    }
    else { 
        try{
        Write-Log -Message "Creating new export file" -LogFileName $LogFileName -Severity Information
        New-Item -Path $ADXScriptDirectory -Name $ADXCommandsScriptFileName -ItemType "file" -Force | out-null
        }
        catch {
            Write-Log -Message "An error occurred in creating the export file" -LogFileName $LogFileName -Severity Error
        }
    }     
    Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "//Log Analytics Tables to ADX Tables Mapping"
    Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "//TimeGenerated: $Timestamp"
    Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "//Log Analytics Workspace: $LogAnalyticsWorkspaceId"
    foreach ($table in $LaTables) {
        if ($CustomList -eq $false) {
            $TableName = $table.'Name'
        }
        else {
            $TableName = $table
        }                
        
        try {
            Write-Log -Message "Retrieving schema and mappings for $TableName" -LogFileName $LogFileName -Severity Information
            $query = $TableName + ' | getschema | project ColumnName, DataType'        
            $AdxTablesArray.Add($TableName.Trim())
            
            Write-Verbose "Executing: (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $query).Results"
            try{																														  
                $output = (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $query -ErrorAction Stop ).Results 
            }
            catch {
                Write-Log -Message "An error occurred in querying schema and mappings for $TableName" -LogFileName $LogFileName -Severity Error
                Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n//TableName: $TableName" 
                Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "//Failed to find table in the Log Analytics Workspace" 
                continue
            }    

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

            $CreateRawTable = '.create-merge table {0} (Records:dynamic)' -f $TableRaw

            $CreateRawMapping = @'
.create-or-alter table {0} ingestion json mapping '{1}' '[{{"column":"Records","Properties":{{"path":"$.records"}}}}]'
'@ -f $TableRaw, $RawMapping

            $CreateRetention = '.alter-merge table {0} policy retention softdelete = 0d' -f $TableRaw

            $CreateTable = '.create-merge table {0} ({1})' -f $TableName, $schema

            $CreateFunction = @'
.create-or-alter function {0} {{{1} | mv-expand events = Records | project {2} }}
'@ -f $TableExpandFunction, $TableRaw, $function

            $CreatePolicyUpdate = @'
.alter table {0} policy update @'[{{"Source": "{1}", "Query": "{2}()", "IsEnabled": "True", "IsTransactional": true}}]'
'@ -f $TableName, $TableRaw, $TableExpandFunction
    
        try {
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n//TableName: $TableName" 
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n$CreateRawTable"
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n$CreateRawMapping"
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n$CreateRetention"
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n$CreateTable"
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n$CreateFunction"
            Add-Content "$ADXScriptDirectory\$ADXCommandsScriptFileName" "`n$CreatePolicyUpdate"
        }
            catch {        
                Write-Log -Message "An error occurred in when adding the content to the export file" -LogFileName $LogFileName -Severity Error		
                exit
            }
            Write-Log -Message "Successfully added Raw and Mapping tables for: $TableName to export file." -LogFileName $LogFileName -Severity Information
        }
        catch {
            Write-Log -Message "An error occurred in New-AdxRawMappingTables method" -LogFileName $LogFileName -Severity Error
        }
    }
} 

#endregion

#region DriverProgram

Write-Output "`n`n Starting $ScriptName at: $(Get-Date)"

# Write each parameter to host
Write-Host "`r`nScript Parameters" -ForegroundColor Blue
Write-Host " > Log Analytics Resource Group: $($LogAnalyticsResourceGroup)" -ForegroundColor Blue
Write-Host " > Log Analytics Workspace Name: $($LogAnalyticsWorkspaceName)" -ForegroundColor Blue
Write-Host " > Only Tables With Data: $($OnlyTablesWithData)" -ForegroundColor Blue
Write-Host " > Table Name List: $($TableNameList)" -ForegroundColor Blue
Write-Host " > Output Folder Path: $($OutputFolderPath)" -ForegroundColor Blue
Write-Host " > Force: $($Force)" -ForegroundColor Blue

# Check Powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Log "Supported PowerShell version for this script is 5 or above" -LogFileName $LogFileName -Severity Error    
    exit
}

# Load required modules
$RequiredModules | ForEach-Object { Get-RequiredModules -Module $_ }

Write-Output " Creating log $LogFileName"

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "CreateADXTables", $TimeStamp

$OutputFolderPath, $ADXScriptDirectory, $LogDirectory | ForEach-Object {
    if (!(Test-Path "$_")) { 
        Write-host "Creating Folder Path: $_" 
        try{
            New-Item -Path $_ -ItemType "directory" -Force | out-null
            Write-Host "Folder Path created successfully" -ForegroundColor Green
        }
        catch {
            Write-Error -Message "An error occurred in creating the folder" 
            exit
        }
    }
}

if (!$Force){
    Write-Host "`n`r`If not already authenticated, you will be prompted to sign in to Azure.`nMake sure that your credentials have:" -BackgroundColor Blue
    Write-Host "`n > Azure Log Analytics workspace 'Read' permissions on: $($LogAnalyticsWorkspaceName)`r`n" -BackgroundColor Blue

    Read-Host -Prompt "Press enter to continue or CTRL+C to exit the script."
}
else{
    Write-Host "`n`r`nForce is enabled. Script will run without user input.`n" -ForegroundColor Yellow
}

$Context = Get-AzContext

if (!$Context) {
    Write-Warning "No Azure context found. Please sign in to Azure. If using a service principal, please cancel the script and run 'Connect-AzAccount' first." 
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
        Write-Log -Message "Log Analytics workspace: $LogAnalyticsWorkspaceName in region: $LogAnalyticsLocation exists." -LogFileName $LogFileName -Severity Information
    }
    else {            
        Write-Log -Message "Log Analytics workspace: $LogAnalyticsWorkspaceName not found" -LogFileName $LogFileName -Severity Error       
    } 
}
catch {    
    Write-Log -Message "Error occurred in retreiving Log Analytics workspace: $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error
}

#region ADXTableCreation


if ($TableNameList.count -eq 0) {    
    Write-Verbose "Executing: Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $QueryAllTables" 
    
    try {       
        if ($OnlyTablesWithData){
            Write-Log -Message "Retrieving all tables with data from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
            $QueryAllTables = 'search *| distinct $table| sort by $table asc nulls last | project Name = $table'
            $ResultsAllTables = (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $QueryAllTables).Results
            $ResultCount = $ResultsAllTables.name.count
            Write-Log -Message "Retrieved $ResultCount tables with data from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
        }
        else{
            Write-Log -Message "Retrieving all tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
            $ResultsAllTables = Get-AzOperationalInsightsTable -ResourceGroupName $LogAnalyticsResourceGroup -WorkspaceName $LogAnalyticsWorkspaceName | Select-Object -unique Name | Sort-Object -Property Name 
            $ResultCount = $ResultsAllTables.count
            Write-Log -Message "Retrieved $ResultCount tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
        }
    }
    catch {            
        Write-Log -Message "An error occurred in querying table names from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error         
        exit
    }
}
else {
    try {
        Write-Host "`nUsing TablesNameList Parameter" -ForegroundColor Blue
        $ResultsAllTables = $TableNameList
    }
    catch {
        Write-Log -Message "Unknown error with TableNameList parameter" -LogFileName $LogFileName -Severity Error       
        exit
    }    
}

$AdxTablesArray = New-Object System.Collections.Generic.List[System.Object]    
if ($TableNameList.count -eq 0) {
    $CustomList = $false
}
else {
    $CustomList = $true
}
New-AdxRawMappingTables -LaTables $ResultsAllTables -CustomList $CustomList

#endregion
