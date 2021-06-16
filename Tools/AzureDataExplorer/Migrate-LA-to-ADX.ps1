<#       
  	THE SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
#>

PARAM(    
    [Parameter(Mandatory=$true)] $LogAnalyticsWorkspaceName,
    [Parameter(Mandatory=$true)] $LogAnalyticsResourceGroup,
    [Parameter(Mandatory=$true)] $ADXResourceGroup,
    [Parameter(Mandatory=$true)] $ADXClusterURL,
    [Parameter(Mandatory=$true)] $ADXDBName,   
        
    $ADXEngineUrl = "$ADXClusterURL/$ADXDBName",
    $kustoToolsPackage = "microsoft.azure.kusto.tools",
    $kustoConnectionString = "$ADXEngineUrl;Fed=True",
    
    $nugetPackageLocation = "$($env:USERPROFILE)\.nuget\packages",
    $nugetIndex = "https://api.nuget.org/v3/index.json",
    $nugetDownloadUrl = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
)

Function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter()]
        [ValidateNotNullOrEmpty()]
        [string]$Message,
        [string]$LogFileName,
 
        [Parameter()]
        [ValidateNotNullOrEmpty()]
        [ValidateSet('Information','Warning','Error')]
        [string]$Severity = 'Information'
    )
    try {
        [pscustomobject]@{
            Time = (Get-Date -f g)
            Message = $Message
            Severity = $Severity
        } | Export-Csv -Path "$PSScriptRoot\$LogFileName" -Append -NoTypeInformation
    }
    catch {
        Write-Host "An error occured in Write-Log() method" -ForegroundColor Red
    }
    
}
Function CheckModules($module) {
    try{
        $installedModule = Get-InstalledModule -Name $module -ErrorAction SilentlyContinue
        if ($null -eq $installedModule) {
            Write-Warning "The $module PowerShell module is not found"
            Write-Log -Message "The $module PowerShell module is not found" -LogFileName $LogFileName -Severity Warning
            #check for Admin Privleges
            $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

            if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
                #Not an Admin, install to current user            
                Write-Warning -Message "Can not install the $module module. You are not running as Administrator"
                Write-Log -Message "Can not install the $module module. You are not running as Administrator" -LogFileName $LogFileName -Severity Warning

                Write-Warning -Message "Installing $module module to current user Scope"
                Write-Log -Message "Installing $module module to current user Scope" -LogFileName $LogFileName -Severity Warning
                
                Install-Module -Name $module -Scope CurrentUser -Force
                Import-Module -Name $module -Force
            }
            else {
                #Admin, install to all users
                Write-Warning -Message "Installing the $module module to all users"
                Write-Log -Message "Installing the $module module to all users" -LogFileName $LogFileName -Severity Warning
                Install-Module -Name $module -Force
                Import-Module -Name $module -Force
            }
        }
        #Install-Module will obtain the module from the gallery and install it on your local machine, making it available for use.
        #Import-Module will bring the module and its functions into your current powershell session, if the module is installed.  
    }
    catch{
        Write-Host "An error occured in CheckModules() method" -ForegroundColor Red
        Write-Log -Message "An error occured in CheckModules() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
}

Function InvokeKustoCLI($adxCommandsFile) {
    try{
        $kustoToolsDir = "$env:USERPROFILE\.nuget\packages\$kustoToolsPackage\"
        $currentDir = Get-Location
        Set-Location $scriptDir

        if (!(test-path $kustoToolsDir))
        {        
            if(!(test-path nuget))
            {
                Write-Warning "The Nuget module is not found"
                Write-Log -Message "The Nuget module is not found" -LogFileName $LogFileName -Severity Warning
            
                Write-Host "Downloading Nuget package" -ForegroundColor Green
                Write-Log -Message "Downloading Nuget package" -LogFileName $LogFileName -Severity Information
                (new-object net.webclient).downloadFile($nugetDownloadUrl, "$pwd\nuget.exe")
            }

            Write-Host "Installing Kusto Tools Package" -ForegroundColor Green
            Write-Log -Message "Installing Kusto Tools Package" -LogFileName $LogFileName -Severity Information
            &.\nuget.exe install $kustoToolsPackage -Source $nugetIndex -OutputDirectory $nugetPackageLocation
        }

        $kustoExe = $kustoToolsDir + @(get-childitem -recurse -path $kustoToolsDir -Name kusto.cli.exe)[-1]
        
        if (!(test-path $kustoExe))
        {
            Write-Warning "Unable to find kusto client tool $kustoExe. exiting"
            Write-Log -Message "Unable to find kusto client tool $kustoExe. exiting" -LogFileName $LogFileName -Severity Warning
            return
        }
        
        Write-Host "Executing queries on Azure Data Explorer (ADX)" -ForegroundColor Green
        Write-Log -Message "Executing queries on Azure Data Explorer (ADX)" -LogFileName $LogFileName -Severity Information
        invoke-expression "$kustoExe `"$kustoConnectionString`" -script:$adxCommandsFile"

        set-location $currentDir
    }
    catch{
        Write-Host "An error occured in InvokeKustoCLI() method" -ForegroundColor Red
        Write-Log -Message "An error occured in InvokeKustoCLI() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
}

Function CreateRawMappingTablesInADX() {    
    [CmdletBinding()]
    param (        
        [Parameter(Mandatory=$true)] $LATables        
    )

    try{
        if(!(Test-Path "$PSScriptRoot\KustoQueries" -PathType Container)) { 
            New-Item -Path $PSScriptRoot -Name "KustoQueries" -ItemType "directory"
        }
        
        $supportedTables = Get-Content "$PSScriptRoot\ADXSupportedTables.json" | ConvertFrom-Json
        
        foreach ($table in $LATables) {
            if ($decision -eq 0) {
                $TableName = $table.'$table'
            }
            else {
                $TableName = $table
            }
            IF ($TableName -match '_CL$'){
                Write-Host "Custom Log Table : $TableName not supported" -ForegroundColor Red
                Write-Log -Message "Custom Log Table : $TableName not supported" -LogFileName $LogFileName -Severity Information
            }
            elseif ($supportedTables."SupportedTables" -contains $TableName.Trim()) {        
                Write-Host "Getting schema and mappings for $TableName"
                Write-Log -Message "Getting schema and mappings for $TableName" -LogFileName $LogFileName -Severity Information
                $query = $TableName + ' | getschema | project ColumnName, DataType'        
                $AdxTablesArray.Add($TableName.Trim())
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
                    } else {
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

                InvokeKustoCLI -AdxCommandsFile "$scriptDir\adxCommands.txt"
                Remove-Item $scriptDir\adxCommands.txt -Force -ErrorAction Ignore        
                Write-Host "Successfully created Raw and Mapping tables for :$TableName in Azure Data Explorer Cluster Database" -ForegroundColor Green
                Write-Log -Message "Successfully created Raw and Mapping tables for :$TableName in Azure Data Explorer Cluster Database" -LogFileName $LogFileName -Severity Information
            }
            else {
                Write-Host "$TableName not supported by Data Export rule" -ForegroundColor Red
                Write-Log -Message "$TableName not supported by Data Export rule" -LogFileName $LogFileName -Severity Error
            }
        }   
    }
    catch{
        Write-Host "An error occured in CreateRawMappingTablesInADX() method" -ForegroundColor Red
        Write-Log -Message "An error occured in CreateRawMappingTablesInADX() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
} # Function close

Function SplitArrayBySize(){
    [CmdletBinding()]
    param (        
        [Parameter(Mandatory=$true)] $ADXTabsArray,
        [Parameter(Mandatory=$true)] $ArraySize
    )    
    try{
        Write-Host "Splitting Array by size 10" -ForegroundColor Green
        Write-Log -Message "Splitting Array by size 10" -LogFileName $LogFileName -Severity Information
        $slicedArraysResult = SliceArray -Item $ADXTabsArray -Size $ArraySize | ForEach-Object { '{0}' -f ($_ -join '","') }
    
        return $slicedArraysResult
    }
    catch{
        Write-Host "An error occured in SplitArrayBySize() method" -ForegroundColor Red
        Write-Log -Message "An error occured in SplitArrayBySize() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
}

Function CreateEventHubNamespace(){
    [CmdletBinding()]
    param (        
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
                try {
                    Write-Host "Create a new EventHub-Namespace:$EventHubNamespaceName under Resource Group:$LogAnalyticsResourceGroup" -ForegroundColor Green
                    Write-Log -Message "Create a new EventHub-Namespace:$EventHubNamespaceName under Resource Group:$LogAnalyticsResourceGroup" -LogFileName $LogFileName -Severity Information
                    Set-Item Env:\SuppressAzurePowerShellBreakingChangeWarnings "true"
                    $resultEventHubNS = New-AzEventHubNamespace -ResourceGroupName $LogAnalyticsResourceGroup `
                                                            -NamespaceName $EventHubNamespaceName `
                                                            -Location $LogAnalyticsLocation `
                                                            -SkuName "Standard" `
                                                            -SkuCapacity 12 `
                                                            -EnableAutoInflate `
                                                            -MaximumThroughputUnits 20 `
                                                            -Verbose
                    
                    if($resultEventHubNS.ProvisioningState.Trim().ToLower() -eq "succeeded") {
                        Write-Host "$EventHubNamespaceName created succesfully" -ForegroundColor Green
                        Write-Log -Message "$EventHubNamespaceName created succesfully" -LogFileName $LogFileName -Severity Information
                    }                
                }
                catch{
                    Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__ -ForegroundColor Red
                    Write-Log -Message "$($_.Exception.Response.StatusCode.value__)" -LogFileName $LogFileName -Severity Error
                    Write-Host "StatusDescription:" $_.Exception.Response.StatusDescription -ForegroundColor Red
                    Write-Log -Message "$($_.Exception.Response.StatusDescription)" -LogFileName $LogFileName -Severity Error
                }
            }
        } 
        return $EventHubsArray
    }
    catch{
        Write-Host "An error occured in CreateEventHubNamespace() method" -ForegroundColor Red
        Write-Log -Message "An error occured in CreateEventHubNamespace() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
}

Function CreateLADataExportRule() {
    [CmdletBinding()]
    param (        
        [Parameter(Mandatory=$true)] $adxEventHubs,
        [Parameter(Mandatory=$true)] $tablesArrayCollection     
    )
    try{
        Write-Host "Creating Log Analytics Data Export rules" -ForegroundColor Blue
        Write-Log -Message "Creating Log Analytics Data Export rules" -LogFileName $LogFileName -Severity Information
        $count=0
        
        
        foreach ($adxEventHub in $adxEventHubs) {        
            $eventHubNameSpace = Get-AzEventHubNamespace -ResourceGroupName $LogAnalyticsResourceGroup -NamespaceName $adxEventHub    
            
            if ($adxEventHubs.Count -gt 1){
                $exportRuleTables = '"{0}"' -f ($tablesArrayCollection[$count] -join '","')
            }
            else {
                $exportRuleTables = '"{0}"' -f ($tablesArrayCollection -join '","')
            }

            IF ($eventHubNameSpace.ProvisioningState -eq "Succeeded") {
                $randomNumber = Get-Random
                $laDataExportRuleName = "$($LogAnalyticsWorkspaceName)-$($randomNumber)"
                $dataExportAPI = "https://management.azure.com/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.operationalInsights/workspaces/$LogAnalyticsWorkspaceName/dataexports/$laDataExportRuleName" + "?api-version=2020-08-01"
            
                $LAAccessToken = (Get-AzAccessToken).Token            
                $LAAPIHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
                $LAAPIHeaders.Add("Content-Type", "application/json")
                $LAAPIHeaders.Add("Authorization", "Bearer $LAAccessToken")
                
                $dataExportBody = @"
                {
                    "properties": {
                        "destination": {
                        "resourceId": "$($eventHubNameSpace.Id)"
                        },
                        "tablenames": [$exportRuleTables],
                        "enable": true
                    }
                }
"@
                try {        
                    $createDataExportRule = Invoke-RestMethod -Uri $dataExportAPI -Method "PUT" -Headers $LAAPIHeaders -Body $dataExportBody
                    Write-Host $createDataExportRule -ForegroundColor Green
                    Write-Log -Message $createDataExportRule -LogFileName $LogFileName -Severity Information
                } catch {    
                    Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__ -ForegroundColor Red
                    Write-Log -Message $($_.Exception.Response.StatusCode.value__) -LogFileName $LogFileName -Severity Error
                    Write-Host "StatusDescription:" $_.Exception.Response.StatusDescription -ForegroundColor Red
                    Write-Log -Message $($_.Exception.Response.StatusDescription) -LogFileName $LogFileName -Severity Error
                }   
                $count++
            }
            ELSE {
                Start-Sleep 300
            }
        }
    }
    catch{
        Write-Host "An error occured in CreateLADataExportRule() method" -ForegroundColor Red
        Write-Log -Message "An error occured in CreateLADataExportRule() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
}

Function CreateADXDataConnection(){
    [CmdletBinding()]
    param (        
        [Parameter(Mandatory=$true)] $adxEventHubs        
    )
    
    try{   
        Register-AzResourceProvider -ProviderNamespace Microsoft.Kusto
        Write-Host "Creating Azure Data Explorer Data Connection" -ForegroundColor Blue
        Write-Log -Message "Creating Azure Data Explorer Data Connection" -LogFileName $LogFileName -Severity Information
        $ADXClusterName = $ADXClusterURL.split('.')[0].split('//')[1].Trim()
        foreach ($adxEH in $adxEventHubs)
        {
            try{
                $eventHubTopics = Get-AzEventHub -ResourceGroup $LogAnalyticsResourceGroup `
                                                 -NamespaceName $adxEH `
                                                 -Verbose        
                if ($null -ne $eventHubTopics) {
                    foreach($eventHubTopic in $eventHubTopics)
                    {
                        $tableEventHubTopic = $eventHubTopic.Name.split('-')[1]
                        # The above statement will return Table name in lower case
                        # When sending lower case table to Azure Kusto Data connection, its throwing error
                        # It is expecting the table name in title case (Case Sensitive)
                        # In order to get exact same case table name, getting it from Source array                        
                        $adxTables = $AdxTablesArray.ToArray()                        
                        $arrIndex = $adxTables.ForEach{$_.ToLower()}.IndexOf($tableEventHubTopic)                        
                        $eventHubResourceId = $eventHubTopic.Id
                        $adxTableRealName = $adxTables[$arrIndex].Trim().ToString()
                        $adxTableRaw = "$($adxTableRealName)HistoricRaw"
                        $adxTableRawMapping = "$($adxTableRealName)HistoricMapping"
                        $dataConnName = "$($tableEventHubTopic)dataconnection"

                        $dataConnAPI = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ADXResourceGroup/providers/Microsoft.Kusto/clusters/$ADXClusterName/databases/$ADXDBName/dataConnections/$dataConnName" + "?api-version=2021-01-01"
            
                        $LAAccessToken = (Get-AzAccessToken).Token            
                        $LAAPIHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
                        $LAAPIHeaders.Add("Content-Type", "application/json")
                        $LAAPIHeaders.Add("Authorization", "Bearer $LAAccessToken")
                                                                        
                        $dataConnBody = @"
                        {
                            "location": "$LogAnalyticsLocation",
                            "kind": "EventHub",
                            "properties": {
                              "eventHubResourceId": "$eventHubResourceId",                              
                              "consumerGroup": "$('$Default')",
                              "dataFormat":"MULTILINE JSON",
                              "tableName":"$adxTableRaw",
                              "mappingRuleName":"$adxTableRawMapping",
                              "compression":"None"
                            }
                        }
"@
                        
                        try {        
                            $createDataConnRule = Invoke-RestMethod -Uri $dataConnAPI -Method "PUT" -Headers $LAAPIHeaders -Body $dataConnBody
                            Write-Host $createDataConnRule -ForegroundColor Green
                            Write-Log -Message $createDataConnRule -LogFileName $LogFileName -Severity Information
                        } catch {
                            Write-Host "An error occured in creating Data Connection for $($eventHubTopic.Name)" -ForegroundColor Red
                            Write-Log -Message "An error occured in creating Data Connection for $($eventHubTopic.Name)" -LogFileName $LogFileName -Severity Error            
                            Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__ -ForegroundColor Red
                            Write-Log -Message $($_.Exception.Response.StatusCode.value__) -LogFileName $LogFileName -Severity Error
                            Write-Host "StatusDescription:" $_.Exception.Response.StatusDescription -ForegroundColor Red
                            Write-Log -Message $($_.Exception.Response.StatusDescription) -LogFileName $LogFileName -Severity Error
                        }                      
                                                                                                
                    }
                }
                else {                    
                    Write-Host "EventHubTopics not available in $adxEH" -ForegroundColor Red
                    Write-Log -Message "EventHubTopics not available in $adxEH" -LogFileName $LogFileName -Severity Error        
                }
                
            } catch {
                Write-Host "An error occured in retreiving EventHub Topics from $adxEH" -ForegroundColor Red
                Write-Log -Message "An error occured in retreiving EventHub Topics from $adxEH" -LogFileName $LogFileName -Severity Error        
            }
        }
    }
    catch{
        Write-Host "An error occured in CreateADXDataConnection() method" -ForegroundColor Red
        Write-Log -Message "An error occured in CreateADXDataConnection() method" -LogFileName $LogFileName -Severity Error        
        exit
    }
}

Function SliceArray {

    [CmdletBinding()]
    param (        
        [Parameter(Mandatory=$true)] [String[]]$Item,
        [Parameter(Mandatory=$true)] [int]$Size
    )
    
    BEGIN { $Items=@()}
    PROCESS {
        foreach ($i in $Item ) { $Items += $i }
    }
    END {
        0..[math]::Floor($Items.count/$Size) | ForEach-Object { 
            $x, $Items = $Items[0..($Size-1)], $Items[$Size..$Items.Length]; ,$x
        } 
    }  
}

Function Start-Sleep($seconds, $waitMessage) {
    $doneDT = (Get-Date).AddSeconds($seconds)
    while($doneDT -gt (Get-Date)) {
        $secondsLeft = $doneDT.Subtract((Get-Date)).TotalSeconds
        $percent = ($seconds - $secondsLeft) / $seconds * 100
        Write-Progress -Activity $waitMessage -Status "Please wait..." -SecondsRemaining $secondsLeft -PercentComplete $percent
        [System.Threading.Thread]::Sleep(500)
    }
    Write-Progress -Activity $waitMessage -Status "Please wait..." -SecondsRemaining 0 -Completed
}



CheckModules("Az.Resources")
CheckModules("Az.OperationalInsights")

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "ADXMigration", $TimeStamp

Write-Host "`r`nIf not logged in to Azure already, you will now be asked to log in to your Azure environment. `nFor this script to work correctly, you need to provide credentials `nAzure Log Analytics Workspace Read Permissions `nAzure Data Explorer Database User Permission. `nThis will allow the script to read all the Tables from Log Analytics Workspace `nand create tables in Azure Data Explorer.`r`n" -BackgroundColor Blue

Read-Host -Prompt "Press enter to continue or CTRL+C to quit the script"

$context = Get-AzContext

if(!$context){
    Connect-AzAccount
    $context = Get-AzContext
}

$SubscriptionId = $context.Subscription.Id

try {
    $WorkspaceObject = Get-AzOperationalInsightsWorkspace -Name $LogAnalyticsWorkspaceName -ResourceGroupName $LogAnalyticsResourceGroup -DefaultProfile $context 
    $LogAnalyticsLocation = $WorkspaceObject.Location
    $LogAnalyticsWorkspaceId = $WorkspaceObject.CustomerId
    Write-Host "Workspace named $LogAnalyticsWorkspaceName in region $LogAnalyticsLocation exists."  -ForegroundColor Green
    Write-Log -Message "Workspace named $LogAnalyticsWorkspaceName in region $LogAnalyticsLocation exists." -LogFileName $LogFileName -Severity Information
    $question = 'Do you want to create Raw and Mapping Tables in Azure Data Explorer(ADX) for all the tables in your LA?'

    $choices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
    $choices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
    $choices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

    $decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
    if ($decision -eq 0) {
        TRY{        
            Write-Host "Getting all the tables from $LogAnalyticsWorkspaceName"  -ForegroundColor Green
            Write-Log -Message "Getting all the tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
            $queryAllTables = 'search *| distinct $table| sort by $table asc nulls last'
            $resultsAllTables = (Invoke-AzOperationalInsightsQuery -WorkspaceId $LogAnalyticsWorkspaceId -Query $queryAllTables).Results
        }
        CATCH{
            Write-Host "An error occured in querying all the Table names from $LogAnalyticsWorkspaceName" -ForegroundColor Red
            Write-Log -Message "An error occured in querying all the Table names from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error        
            exit
        }
    } else {
        try {
            Write-Host "Enter selected Log Analytics Table names separated by comma (,) (Case-Sensitive)" -ForegroundColor Blue
            $userInputTables = Read-Host 
            $resultsAllTables = $userInputTables.Split(',')
        }
        catch {
            Write-Host "In-correct user input - table names should be separated with comma(,)" -ForegroundColor Red
            Write-Log -Message "In-correct user input - table names should be separated with comma(,)" -LogFileName $LogFileName -Severity Error        
            exit
        }
        
    }
    $AdxTablesArray = New-Object System.Collections.Generic.List[System.Object]    
    CreateRawMappingTablesInADX -LATables $resultsAllTables

    $dataExportQuestion = 'Do you want to continue creating Data Export rule and Data Ingestion rules for Tables in Azure Data Explorer(ADX)?'

    $choices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
    $choices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
    $choices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

    $dataExportDecision = $Host.UI.PromptForChoice($title, $dataExportQuestion, $choices, 0)
    if ($dataExportDecision -eq 0) {        
        $AdxMappedTables = SplitArrayBySize -ADXTabsArray $AdxTablesArray.ToArray() -ArraySize 10        
        $eventHubsForADX = CreateEventHubNamespace -ArraysObject $AdxMappedTables        
        CreateLADataExportRule -AdxEventHubs $eventHubsForADX -TablesArrayCollection $AdxMappedTables
        
        

        $dataConnectionQuestionChoices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
        $dataConnectionQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
        $dataConnectionQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

        $dataConnectionDecision = $Host.UI.PromptForChoice($title, $dataConnectionQuestion, $dataConnectionQuestionChoices, 0)
        if ($dataConnectionDecision -eq 0) {
            Start-Sleep -seconds 1800 -waitMessage "EventHubTopics for LA Tables are provisioning"                    
            CreateADXDataConnection -AdxEventHubs $eventHubsForADX
        }
        else {
            Write-Host "Create Dataconnection rules manually for $ADXDBName under $ADXEngineUrl"
            Write-Log -Message "Create Dataconnection rules manually for $ADXDBName under $ADXEngineUrl" -LogFileName $LogFileName -Severity Warning
            exit
        }
    } 
    else {
        Write-Host "Create Data Export & Dataconnection rules manually for $ADXDBName under $ADXEngineUrl"
        Write-Log -Message "Create Data Export & Dataconnection rules manually for $ADXDBName under $ADXEngineUrl" -LogFileName $LogFileName -Severity Warning
        exit
    }    

} catch {
    Write-Host "$LogAnalyticsWorkspaceName not found"
    Write-Log -Message "$LogAnalyticsWorkspaceName not found" -LogFileName $LogFileName -Severity Error
}
