<#       
  	THE SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

    .SYNOPSIS
        This PowerShell script integrates given Log Analytics Workspace tables data into Azure Data Explorer for long term retention
    .DESCRIPTION
        It perform the following actions
            1. Queries Log Analytics Workspace Tables
            2. Performs check against Data Export supported tables json
            3. Creates target Table, Raw and Mapping in Azure Data Explorer
            4. Creates EventHub Namespaces (Standard) by diving #1 tables by 10
            5. Creates Data Export rules via REST API on Log Analytics Workspace
            6. Creates Data Connection rules in Azure Data Explorer (ADX) Database level
    .PARAMETER Log Analytics WorkSpaceName
        Enter the Log Analytics workspace name (required)
    .PARAMETER Log Analytics ResourceGroupName
        Enter the Resource Group name of Log Analytics workspace (required)
    .PARAMETER Azure Data Explorer (ADX) ResourceGroupName
        Enter the Resource Group name of Azure Data Explorer (ADX) (required)
    .PARAMETER Azure Data Explorer (ADX) Cluster URL
        Enter the Resource Group name of Azure Data Explorer (ADX) Cluster URL (required)
    .PARAMETER Azure Data Explorer (ADX) Database Name
        Enter the Resource Group name of Azure Data Explorer (ADX) Database Name (required)
    .NOTES
        AUTHOR: Sreedhar Ande
        LASTEDIT: 25 Jun 2021
    .EXAMPLE
        Migrate-LA-to-ADX -LogAnalyticsResourceGroup "LARGName" -LogAnalyticsWorkspaceName "LAWName"
                          -AdxResourceGroup "ADXRG" -AdxClusterURL "ADXClusterURL" -AdxDBName "ADXDBName"
        
#>

#region UserInputs

Param(
	[Parameter(Mandatory = $true, HelpMessage = "Enter the resource group location for the Log Analytics workspace.")]
    [string]$LogAnalyticsResourceGroup,

    [Parameter(Mandatory = $true, HelpMessage = "Enter the Log Analytics workspace name from which to export data.")]
    [string]$LogAnalyticsWorkspaceName,

    [Parameter(Mandatory = $true, HelpMessage = "Enter the resource group location for the existing Azure Data Explorer (ADX) cluster for which to export data.")]
    [string]$AdxResourceGroup,

    [Parameter(Mandatory = $true, HelpMessage = "Enter the Azure Data Explorer (ADX) cluster URL.")]
    [string]$AdxClusterURL,

    [Parameter(Mandatory = $true, HelpMessage = "Enter the Azure Data Explorer (ADX) cluster database name.")]
    [string]$AdxDBName
) 

#endregion User Input
      
#region StaticValues

[string]$AdxEngineUrl = "$AdxClusterURL/$AdxDBName"
[string]$KustoToolsPackage = "microsoft.azure.kusto.tools"
[string]$KustoConnectionString = "$AdxEngineUrl;Fed=True"
[string]$NuGetIndex = "https://api.nuget.org/v3/index.json"
[string]$NuGetDownloadUrl = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"

#endregion StaticValues

#region HelperFunctions

function Write-Log {
    <#
    .Description 
    Write-Log is used to write information to a log file.
    
    .Parameter Severity
    Parameter specifies the severity of the log message. Values can be: Information, Warning, or Error. 
    #> 
    [CmdletBinding()]
    Param(
        [Parameter()]
        [ValidateNotNullOrEmpty()]
        [string]$Message,
        [string]$LogFileName,
 
        [Parameter()]
        [ValidateNotNullOrEmpty()]
        [ValidateSet('Information','Warning','Error')]
        [string]$Severity = 'Information'
    )
	# Write the message out to the correct channel											  
	switch($Severity)
    {
        "Information" {Write-Host $Message -ForegroundColor Green}
        "Warning" {Write-Host $Message -ForegroundColor Yellow}
        "Error" {Write-Host $Message -ForegroundColor Red}
    } 											  
    try {
        [PSCustomObject]@{
            Time = (Get-Date -f g)
            Message = $Message
            Severity = $Severity
        } | Export-Csv -Path "$PSScriptRoot\$LogFileName" -Append -NoTypeInformation
    }
    catch {
        Write-Error "An error occurred in Write-Log() method" -ErrorAction Continue
		
    }    
}

function Get-RequiredModules {
    <#
    .Description 
    Get-Required is used to install and then import the specified PowerShell module.
    
    .Parameter Module
    Parameter specifices the PowerShell module to install. 
    #>

    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory = $true)] $Module        
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
                
                Install-Module -Name $Module -Scope CurrentUser -Force
                Import-Module -Name $Module -Force
            }
            else {
                #Admin, install to all users
																				   
                Write-Log -Message "Installing the $Module module to all users" -LogFileName $LogFileName -Severity Warning
                Install-Module -Name $Module -Force
                Import-Module -Name $Module -Force
            }
        }
        #Install-Module will obtain the module from the gallery and install it on your local machine, making it available for use.
        #Import-Module will bring the module and its functions into your current powershell session, if the module is installed.  
    }
    catch {
        Write-Log -Message "An error occurred in Get-RequiredModules() method" -LogFileName $LogFileName -Severity Error																			
        exit
    }
}

function Split-ArrayBySize {
    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory = $true)] $AdxTabsArray,
        [Parameter(Mandatory = $true)] $ArraySize
    )    
    try {     
        
        $slicedArraysResult = Split-Array -Item $AdxTabsArray -Size $ArraySize | ForEach-Object { '{0}' -f ($_ -join '","') }
    
        return $slicedArraysResult
    }
    catch {        
        
		Write-Error "An error occurred in SplitArrayBySize() method" -ErrorAction stop
        exit
    }
}

function Split-Array {

    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory=$true)] [String[]]$Item,
        [Parameter(Mandatory=$true)] [int]$Size
    )
    
    begin { $Items=@()}
    process {
        foreach ($i in $Item ) { $Items += $i }
    }
    end {
        0..[math]::Floor($Items.count/$Size) | ForEach-Object { 
            $x, $Items = $Items[0..($Size-1)], $Items[$Size..$Items.Length]; ,$x
        } 
    }  
}

function Start-SleepMessage {
    Param(
        $Seconds, 
        $WaitMessage
    )

    $DoneDT = (Get-Date).AddSeconds($seconds)
    
    while ($DoneDT -gt (Get-Date)) {
        $SecondsLeft = $doneDT.Subtract((Get-Date)).TotalSeconds
        $Percent = ($Seconds - $SecondsLeft) / $seconds * 100
        Write-Progress -Activity $WaitMessage -Status "Please wait..." -SecondsRemaining $SecondsLeft -PercentComplete $Percent
        [System.Threading.Thread]::Sleep(500)
    }
    
    Write-Progress -Activity $waitMessage -Status "Please wait..." -SecondsRemaining 0 -Completed
}

#endregion

#region MainFunctions

function Invoke-KustoCLI {
        <#
    .Description 
    Invoke-KustoCLI is used to execute the KustoCLI with the specified AdxCommandsFile.
    
    .Parameter AdxCommandsFile
    Parameter specifices the path the the file that includes the commands to execute 
    #>

    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory = $true)] $AdxCommandsFile        
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
    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory = $true)] $LaTables        
    )

    try{
        if(!(Test-Path "$PSScriptRoot\KustoQueries" -PathType Container)) { 
            New-Item -Path $PSScriptRoot -Name "KustoQueries" -ItemType "directory"
        }
        
        $supportedTables = Get-Content "$PSScriptRoot\ADXSupportedTables.json" | ConvertFrom-Json
        
        foreach ($table in $LaTables) {
            if ($decision -eq 0) {
                $TableName = $table.'$table'
            }
            else {
                $TableName = $table
            }
            if ($TableName -match '_CL$') {                
                Write-Log -Message "Custom log table : $TableName not supported" -LogFileName $LogFileName -Severity Information
            }
            elseif ($supportedTables."SupportedTables" -contains $TableName.Trim()) {        
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

                Invoke-KustoCLI -AdxCommandsFile "$scriptDir\adxCommands.txt"
                Remove-Item $ScriptDir\adxCommands.txt -Force -ErrorAction Ignore        
                
                Write-Log -Message "Successfully created Raw and Mapping tables for :$TableName in Azure Data Explorer Cluster Database" -LogFileName $LogFileName -Severity Information
            }
            else {                
                Write-Log -Message "$TableName not supported by Data Export rule" -LogFileName $LogFileName -Severity Error
            }
        }   
    }
    catch{        
		Write-Log -Message "An error occurred in CreateRawMappingTablesInADX() method" -LogFileName $LogFileName -Severity Error		
        exit
    }
} 

function New-EventHubNamespace {
    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory=$true)] $ArraysObject        
    )
    try{
        $EventHubsArray = @()
        
        foreach ($slicedArray in $ArraysObject) {
            if ($slicedArray.Length -gt 0){
                #Create EventHub NameSpace
                $randomNumber = Get-Random
                $EventHubNamespaceName = "$($LogAnalyticsWorkspaceName)-$($randomNumber)"        
                $EventHubsArray += $EventHubNamespaceName
				Write-Verbose "Executing: New-AzEventHubNamespace -ResourceGroupName $LogAnalyticsResourceGroup -NamespaceName $EventHubNamespaceName `
                -Location $LogAnalyticsLocation -SkuName Standard -SkuCapacity 12 -EnableAutoInflate -MaximumThroughputUnits 20"																																	   
                try {                    
                    Write-Log -Message "Create a new EventHub-Namespace:$EventHubNamespaceName under Resource Group:$LogAnalyticsResourceGroup" -LogFileName $LogFileName -Severity Information
                    Set-Item Env:\SuppressAzurePowerShellBreakingChangeWarnings "true"
                    $ResultEventHubNS = New-AzEventHubNamespace -ResourceGroupName $LogAnalyticsResourceGroup `
                                                            -NamespaceName $EventHubNamespaceName `
                                                            -Location $LogAnalyticsLocation `
                                                            -SkuName "Standard" `
                                                            -SkuCapacity 12 `
                                                            -EnableAutoInflate `
                                                            -MaximumThroughputUnits 20                                                            
                    
                    if($ResultEventHubNS.ProvisioningState.Trim().ToLower() -eq "succeeded") {                        
                        Write-Log -Message "$EventHubNamespaceName created successfully" -LogFileName $LogFileName -Severity Information
                    }                
                }
                catch {
                    
                    Write-Log -Message "$($_.Exception.Response.StatusCode.value__)" -LogFileName $LogFileName -Severity Error
                    
                    Write-Log -Message "$($_.Exception.Response.StatusDescription)" -LogFileName $LogFileName -Severity Error
                }
            }
        } 
        return $EventHubsArray
    }
    catch{        
        Write-Log -Message "An error occurred in Create-EventHubNamespace() method" -LogFileName $LogFileName -Severity Error        
		
        exit
    }
}

function New-LaDataExportRule {
    [CmdletBinding()]
    param (        
        [Parameter(Mandatory=$true, Position=0)] $AdxEventHubs,
        [Parameter(Mandatory=$true, Position=1)] $TablesArrayCollection     
    )
	Write-Log -Message "Creating Log Analytics Data Export rules" -LogFileName $LogFileName -Severity Information																											 
    try{        
        $Count=0        
        foreach ($AdxEventHub in $AdxEventHubs) {        
            $EventHubNameSpace = Get-AzEventHubNamespace -ResourceGroupName $LogAnalyticsResourceGroup -NamespaceName $AdxEventHub    
            
            if ($AdxEventHubs.Count -gt 1){
                $ExportRuleTables = '"{0}"' -f ($TablesArrayCollection[$count] -join '","')
            }
            else {
                $ExportRuleTables = '"{0}"' -f ($TablesArrayCollection -join '","')
            }

            if ($EventHubNameSpace.ProvisioningState -eq "Succeeded") {
                $RandomNumber = Get-Random
                $LaDataExportRuleName = "$($LogAnalyticsWorkspaceName)-$($RandomNumber)"
                $DataExportAPI = "https://management.azure.com/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.operationalInsights/workspaces/$LogAnalyticsWorkspaceName/dataexports/$laDataExportRuleName" + "?api-version=2020-08-01"
            
                $AzureAccessToken = (Get-AzAccessToken).Token            
                $LaAPIHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
                $LaAPIHeaders.Add("Content-Type", "application/json")
                $LaAPIHeaders.Add("Authorization", "Bearer $AzureAccessToken")
                
                $DataExportBody = @"
                {
                    "properties": {
                        "destination": {
                        "resourceId": "$($EventHubNameSpace.Id)"
                        },
                        "tablenames": [$ExportRuleTables],
                        "enable": true
                    }
                }
"@
				Write-Verbose "Executing: Invoke-RestMethod -Uri $DataExportAPI -Method 'PUT' -Headers $LaAPIHeaders -Body $DataExportBody"																														   
                try {        
                    $CreateDataExportRule = Invoke-RestMethod -Uri $DataExportAPI -Method "PUT" -Headers $LaAPIHeaders -Body $DataExportBody
                    
                    Write-Log -Message $CreateDataExportRule -LogFileName $LogFileName -Severity Information
                } 
				catch {    
                    
                    Write-Log -Message $($_.Exception.Response.StatusCode.value__) -LogFileName $LogFileName -Severity Error
                    
                    Write-Log -Message $($_.Exception.Response.StatusDescription) -LogFileName $LogFileName -Severity Error
                }   
                $Count++
            }
            ELSE {
                Start-SleepMessage 300
            }
        }
    }
    catch{        
		Write-Error "An error occurred in Create-LaDataExportRule() method" -ErrorAction stop
        exit
    }
}

function New-ADXDataConnectionRules {
    [CmdletBinding()]
    Param (        
        [Parameter(Mandatory=$true, Position=0)] $AdxEventHubs        
    )
    
    try{   
        Register-AzResourceProvider -ProviderNamespace Microsoft.Kusto
        
        Write-Log -Message "Creating Azure Data Explorer Data Connection" -LogFileName $LogFileName -Severity Information
        $ADXClusterName = $ADXClusterURL.split('.')[0].replace("https://","").Trim()
        foreach ($AdxEH in $AdxEventHubs)
        {
			Write-Verbose "Executing: Get-AzEventHub -ResourceGroup $LogAnalyticsResourceGroup -NamespaceName $AdxEH"
            try{
                $EventHubTopics = Get-AzEventHub -ResourceGroup $LogAnalyticsResourceGroup -NamespaceName $AdxEH `
                                                        
                if ($null -ne $EventHubTopics) {
                    foreach($EventHubTopic in $EventHubTopics)
                    {
                        $TableEventHubTopic = $EventHubTopic.Name.split('-')[1]
                        # The above statement will return Table name in lower case
                        # Azure Kusto Data connection is expecting the table name in title case (Case Sensitive)
                        # In order to get exact same case table name, getting it from Source array                                               
                        $AdxTables = $AdxTablesArray.ToArray()                        
                        $ArrIndex = $AdxTables.ForEach{$_.ToLower()}.IndexOf($tableEventHubTopic)                        
                        $EventHubResourceId = $EventHubTopic.Id
                        $AdxTableRealName = $AdxTables[$ArrIndex].Trim().ToString()
                        $AdxTableRaw = "$($AdxTableRealName)Raw"
                        $AdxTableRawMapping = "$($AdxTableRealName)RawMapping"
                        $DataConnName = "dc-$($TableEventHubTopic)"

                        $DataConnAPI = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ADXResourceGroup/providers/Microsoft.Kusto/clusters/$ADXClusterName/databases/$ADXDBName/dataConnections/$dataConnName" + "?api-version=2021-01-01"
            
                        $AzureAccessToken = (Get-AzAccessToken).Token            
                        $DataConnAPIHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
                        $DataConnAPIHeaders.Add("Content-Type", "application/json")
                        $DataConnAPIHeaders.Add("Authorization", "Bearer $AzureAccessToken")
                                                                        
                        $DataConnBody = @"
                        {
                            "location": "$LogAnalyticsLocation",
                            "kind": "EventHub",
                            "properties": {
                              "eventHubResourceId": "$EventHubResourceId",                              
                              "consumerGroup": "$('$Default')",
                              "dataFormat":"JSON",
                              "tableName":"$AdxTableRaw",
                              "mappingRuleName":"$AdxTableRawMapping",
                              "compression":"None"
                            }
                        }
"@
						Write-Verbose "Executing: Invoke-RestMethod -Uri $DataConnAPI -Method 'PUT' -Headers $LaAPIHeaders -Body $DataConnBody"																													   
                        
                        try {        
                            $CreateDataConnRule = Invoke-RestMethod -Uri $DataConnAPI -Method "PUT" -Headers $DataConnAPIHeaders -Body $DataConnBody
                            Write-Log -Message $CreateDataConnRule -LogFileName $LogFileName -Severity Information
                        } 
						catch {
                            
                            Write-Log -Message "An error occurred in creating Data Connection for $($eventHubTopic.Name)" -LogFileName $LogFileName -Severity Error            
                            Write-Log -Message $($_.Exception.Response.StatusCode.value__) -LogFileName $LogFileName -Severity Error                            
                            Write-Log -Message $($_.Exception.Response.StatusDescription) -LogFileName $LogFileName -Severity Error
                        }                      
                                                                                                
                    }
                }
                else {                                        
                    Write-Log -Message "EventHubTopics not available in $AdxEH" -LogFileName $LogFileName -Severity Error        
                }
                
            } 
			catch {
                
                Write-Log -Message "An error occurred in retrieving EventHub Topics from $AdxEH" -LogFileName $LogFileName -Severity Error        
            }
        }
    }
    catch{
        Write-Log -Message "An error occurred in Create-ADXDataConnectionRules() method" -LogFileName $LogFileName -Severity Error		
        exit
    }
}

#endregion

#region DriverProgram

Get-RequiredModules("Az.Resources")
Get-RequiredModules("Az.OperationalInsights")

# Check powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Log "Supported PowerShell version for this script is 5 or above" -LogFileName $LogFileName -Severity Error    
    exit
}

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "ADXMigration", $TimeStamp

Write-Host "`r`nIf not logged in to Azure already, you will now be asked to log in to your Azure environment. `nFor this script to work correctly, you need to provide credentials `nAzure Log Analytics Workspace Read Permissions `nAzure Data Explorer Database User Permission. `nThis will allow the script to read all the Tables from Log Analytics Workspace `nand create tables in Azure Data Explorer.`r`n" -BackgroundColor Blue

Read-Host -Prompt "Press enter to continue or CTRL+C to exit the script"

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
    Write-Log -Message "Error occurred in retreiving given Log Analytics Workspace $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error
}

#region ADXTableCreation
$LaTablesQuestion = "Do you want to create Raw and Mapping Tables in Azure Data Explorer(ADX) for all the tables in your Log Analytics Workspace $LogAnalyticsWorkspaceName"
$LaTablesQuestionChoices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
$LaTablesQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
$LaTablesQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

$LaTablesQuestionDecision = $Host.UI.PromptForChoice($title, $LaTablesQuestion, $LaTablesQuestionChoices, 1)

if ($LaTablesQuestionDecision -eq 0) {
    Write-Verbose "Executing: Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $QueryAllTables" 
    try{       
        Write-Log -Message "Retrieving tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
        $QueryAllTables = 'search *| distinct $table| sort by $table asc nulls last'
        $ResultsAllTables = (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $QueryAllTables).Results
    }
    catch {            
        Write-Log -Message "An error occurred in querying all the Table names from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error         
        exit
    }
} 
else {
    try {
        Write-Host "`nEnter selected Log Analytics Table names separated by comma (,) (Case-Sensitive)" -ForegroundColor Blue
        $UserInputTables = Read-Host 
        $ResultsAllTables = $UserInputTables.Split(',')
    }
    catch {
        Write-Log -Message "In-correct user input - table names should be separated with comma(,)" -LogFileName $LogFileName -Severity Error       
        exit
    }    
}

$AdxTablesArray = New-Object System.Collections.Generic.List[System.Object]    
New-AdxRawMappingTables -LaTables $ResultsAllTables
#endregion

#region EventHubsCreation      
$AdxMappedTables = Split-ArrayBySize -AdxTabsArray $AdxTablesArray.ToArray() -ArraySize 10        
Write-Verbose "Executing: New-EventHubNamespace -ArraysObject $AdxMappedTables" 
$EventHubsForADX =  New-EventHubNamespace -ArraysObject $AdxMappedTables
#endregion

#region LogAnalyticsDataExportRule
New-LaDataExportRule -AdxEventHubs $EventHubsForADX -TablesArrayCollection $AdxMappedTables
#endregion

#region ADXDataConnectionRule
$DataConnectionQuestion = "Do you want to create Data Connection rules on Database $AdxDBName for each table by selecting appropriate EventHub Topic, TableRaw and TableRawMappings. `
                           If Yes, Script will sleep for 30 min, If No, you need to create Data Connection rules Manually"
$DataConnectionQuestionChoices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
$DataConnectionQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
$DataConnectionQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

$DataConnectionQuestionDecision = $Host.UI.PromptForChoice($title, $DataConnectionQuestion, $DataConnectionQuestionChoices, 0)
if ($DataConnectionQuestionDecision -eq 0) {
    Start-SleepMessage -Seconds 1800 -waitMessage "Provisioning EventHubTopics for Log Analytics tables"                    
    New-ADXDataConnectionRules -AdxEventHubs $EventHubsForADX
}
else {            
    Write-Log -Message "Create data connection rules manually for $AdxDBName in $AdxEngineUrl" -LogFileName $LogFileName -Severity Warning    
}
#endregion

#endregion