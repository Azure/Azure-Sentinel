<#       
  	THE SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

    .SYNOPSIS
        This PowerShell script configures Basic or Analytics. 
        

    .DESCRIPTION
        It performs the following actions:
            1. Check if table has any configuration (Basic\Analytics)
            2. Update Table configuration either to Analytics
            3. Update Table Retention based to Analytics
         
    .NOTES
        AUTHOR: Sreedhar Ande
        Last Edit : 11/9/2023 - Sreedhar Ande - Added Support for Azure Gov        

    .EXAMPLE
        .\Configure-Long-Term-Retention.ps1 -TenantId xxxx
#>

#region UserInputs

param(
    [parameter(Mandatory = $true, HelpMessage = "Enter your Tenant Id")] [string] $TenantID    
) 

#endregion UserInputs
      
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
                
                Install-Module -Name $Module -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
                Import-Module -Name $Module -Force
            }
            else {
                #Admin, install to all users																		   
                Write-Log -Message "Installing the $Module module to all users" -LogFileName $LogFileName -Severity Warning
                Install-Module -Name $Module -Repository PSGallery -Force -AllowClobber
                Import-Module -Name $Module -Force
            }
        }
        else {
            if ($UpdateAzModules) {
                Write-Log -Message "Checking updates for module $Module" -LogFileName $LogFileName -Severity Information
                $currentVersion = [Version](Get-InstalledModule | Where-Object {$_.Name -eq $Module}).Version
                # Get latest version from gallery
                $latestVersion = [Version](Find-Module -Name $Module).Version
                if ($currentVersion -ne $latestVersion) {
                    #check for Admin Privleges
                    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

                    if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
                        #install to current user            
                        Write-Log -Message "Can not update the $Module module. You are not running as Administrator" -LogFileName $LogFileName -Severity Warning
                        Write-Log -Message "Updating $Module from [$currentVersion] to [$latestVersion] to current user Scope" -LogFileName $LogFileName -Severity Warning
                        Update-Module -Name $Module -RequiredVersion $latestVersion -Force
                    }
                    else {
                        #Admin - Install to all users																		   
                        Write-Log -Message "Updating $Module from [$currentVersion] to [$latestVersion] to all users" -LogFileName $LogFileName -Severity Warning
                        Update-Module -Name $Module -RequiredVersion $latestVersion -Force
                    }
                }
                else {
                    # Get latest version
                    $latestVersion = [Version](Get-Module -Name $Module).Version               
                    Write-Log -Message "Importing module $Module with version $latestVersion" -LogFileName $LogFileName -Severity Information
                    Import-Module -Name $Module -RequiredVersion $latestVersion -Force
                }
            }
            else {
                # Get latest version
                $latestVersion = [Version](Get-Module -Name $Module).Version               
                Write-Log -Message "Importing module $Module with version $latestVersion" -LogFileName $LogFileName -Severity Information
                Import-Module -Name $Module -RequiredVersion $latestVersion -Force
            }
        }
        # Install-Module will obtain the module from the gallery and install it on your local machine, making it available for use.
        # Import-Module will bring the module and its functions into your current powershell session, if the module is installed.  
    }
    catch {
        Write-Log -Message "An error occurred in Get-RequiredModules() method - $($_)" -LogFileName $LogFileName -Severity Error        
    }
}

#endregion

#region MainFunctions

function Get-LATables {
	[CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $RetentionMethod,
        [parameter(Mandatory = $true)] $APIEndpoint                
    )
	
	$TablesArray = New-Object System.Collections.Generic.List[System.Object]
	
	try {       
        Write-Log -Message "Retrieving tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
        $WSTables = Get-AllTables -APIEndpoint $APIEndpoint
                                         
        if ($RetentionMethod -eq "Analytics") {        
            $searchPattern = '(AzureActivity|Usage)'        
            $TablesArray = $WSTables | Where-Object {($_.TableName -notmatch $searchPattern) } | Sort-Object -Property TableName | Select-Object -Property TableName, RetentionInWorkspace, RetentionInArchive, TotalLogRetention, IngestionPlan  | Out-GridView -Title "Select Table (For Multi-Select use CTRL)" -PassThru
        }
        elseif ($RetentionMethod -eq "Basic") {  
            $searchPattern = '(ContainerLog|ContainerLogV2|ContainerInsights|AppTraces)'          
            $TablesArray = $WSTables | Where-Object {($_.TableName -match $searchPattern) } | Sort-Object -Property TableName | Select-Object -Property TableName, RetentionInWorkspace, RetentionInArchive, TotalLogRetention, IngestionPlan | Out-GridView -Title "Select Table (For Multi-Select use CTRL)" -PassThru
        }    
    }
    catch {
        Write-Log -Message $_ -LogFileName $LogFileName -Severity Error
        Write-Log -Message "An error occurred in querying table names from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error         
        exit
    }
	
	return $TablesArray	
}

function Set-TableConfiguration {
	[CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $QualifiedTables,
		[parameter(Mandatory = $true)] $RetentionType,
        [parameter(Mandatory = $true)] $APIEndpoint
    )
	
	$SuccessTables = @()
    
    foreach($QTable in $QualifiedTables) {	
		$TablesApi = "https://$APIEndpoint/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$LogAnalyticsWorkspaceName/tables/$($QTable.TableName)" + "?api-version=2021-12-01-preview"								
		
		$TablesApiBody = @"
			{
				"properties": {
					"plan": "$RetentionType"
				}
			}
"@
		
		try {        
			$TablesApiResult = Invoke-RestMethod -Uri $TablesApi -Method "PUT" -Headers $LaAPIHeaders -Body $TablesApiBody           			
		} 
		catch {                    
			Write-Log -Message "Set-TableConfiguration $($_)" -LogFileName $LogFileName -Severity Error		                
		}

		If ($TablesApiResult.StatusCode -ne 200) {
            $SuccessTables += [pscustomobject] @{
                                TableName=$TablesApiResult.name.Trim();
                                IngestionPlan=$TablesApiResult.properties.Plan.Trim();
                                TotalLogRetention=$TablesApiResult.properties.totalRetentionInDays;
                                RetentionInArchive=$TablesApiResult.properties.archiveRetentionInDays;
                                RetentionInWorkspace=$TablesApiResult.properties.retentionInDays
                            }
        }
	}
    return $SuccessTables
}

function Get-AllTables {	
    [CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $APIEndpoint
    )	
	$AllTables = @()	
    $TablesApi = "https://$APIEndpoint/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$LogAnalyticsWorkspaceName/tables" + "?api-version=2021-12-01-preview"								
	    		
    try {        
        $TablesApiResult = Invoke-RestMethod -Uri $TablesApi -Method "GET" -Headers $LaAPIHeaders           			
    } 
    catch {                    
        Write-Log -Message "Get-AllTables $($_)" -LogFileName $LogFileName -Severity Error		                
    }

    If ($TablesApiResult.StatusCode -ne 200) {
        $searchPattern = '(_RST|_EXT)'                
        foreach ($ta in $TablesApiResult.value) { 
            try {
                if($ta.name.Trim() -notmatch $searchPattern) {                    
                    $AllTables += [pscustomobject]@{TableName=$ta.name.Trim();
                                IngestionPlan=$ta.properties.Plan.Trim();
                                TotalLogRetention=$ta.properties.totalRetentionInDays;
                                RetentionInArchive=$ta.properties.archiveRetentionInDays;
                                RetentionInWorkspace=$ta.properties.retentionInDays
                            }  
                }
            }
            catch {
                Write-Log -Message "Error adding $ta to collection" -LogFileName $LogFileName -Severity Error
            }            	
        }
    }	
    return $AllTables
}

function Update-TablesRetention {
	[CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $TablesForRetention,		
		[parameter(Mandatory = $true)] $TotalRetentionInDays,
        [parameter(Mandatory = $true)] $APIEndpoint
    )
	$UpdatedTablesRetention = @()
    foreach($tbl in $TablesForRetention) {
		$TablesApi = "https://$APIEndpoint/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$LogAnalyticsWorkspaceName/tables/$($tbl.TableName)" + "?api-version=2021-12-01-preview"		
        $ArchiveDays = [int]($TotalRetentionInDays)
        
        $TablesApiBody = @"
			{
				"properties": {					
					"totalRetentionInDays":$ArchiveDays
				}
			}
"@
		
		try {        
			$TablesApiResult = Invoke-RestMethod -Uri $TablesApi -Method "PUT" -Headers $LaAPIHeaders -Body $TablesApiBody			
		} 
		catch {                    
			Write-Log -Message "Update-TablesRetention $($_)" -LogFileName $LogFileName -Severity Error		                
		}

        if($TablesApiResult) {
            $UpdatedTablesRetention += [pscustomobject]@{TableName=$TablesApiResult.name.Trim();
                IngestionPlan=$TablesApiResult.properties.Plan.Trim();
                TotalLogRetention=$TablesApiResult.properties.totalRetentionInDays;
                RetentionInArchive=$TablesApiResult.properties.archiveRetentionInDays;
                RetentionInWorkspace=$TablesApiResult.properties.retentionInDays
            }
            Write-Log -Message "Table : $($TablesApiResult.name.Trim()) archive updated successfully to $ArchiveDays" -LogFileName $LogFileName -Severity Information
        }		
	}
    return $UpdatedTablesRetention
}

function Collect-AnalyticsPlanRetentionDays {
    [CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $WorkspaceLevelRetention,
        [parameter(Mandatory = $true)] $TableLevelRetentionLimit
    )
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
        
    # Create a new form
    $form = New-Object System.Windows.Forms.Form
    $form.Text = 'Table Plan:Analytics'

    # Get the primary screen
    $primaryScreen = [System.Windows.Forms.Screen]::PrimaryScreen

    # Set the form size and position
    $formWidth = $primaryScreen.WorkingArea.Width * 0.2  # Adjust the form width as desired (80% of screen width in this example)
    $formHeight = $primaryScreen.WorkingArea.Height * 0.2  # Adjust the form height as desired (80% of screen height in this example)
    $formSize = New-Object System.Drawing.Size($formWidth, $formHeight)
    $form.ClientSize = $formSize

    $form.StartPosition = 'CenterScreen'

    $okButton = New-Object System.Windows.Forms.Button
    $okButton.Location = New-Object System.Drawing.Point(90,130)
    $okButton.Size = New-Object System.Drawing.Size(75,30)
    $okButton.Text = 'OK'
    $okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $form.AcceptButton = $okButton
    $form.Controls.Add($okButton)
    $okButton.Enabled = $false    

    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Location = New-Object System.Drawing.Point(170,130)
    $cancelButton.Size = New-Object System.Drawing.Size(75,30)
    $cancelButton.Text = 'Cancel'
    $cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $form.CancelButton = $cancelButton
    $form.Controls.Add($cancelButton)

    $label = New-Object System.Windows.Forms.Label
    $label.Location = New-Object System.Drawing.Point(10,20)
    $label.Size = New-Object System.Drawing.Size(350,60)
    $label.Text = "Enter number of days to archive. The value beyond two years is restricted to full years. Allowed values are: [4-730], 1095, 1460, 1826, 2191, 2556, 2922, 3288, 3653, 4018, 4383 days"
    $form.Controls.Add($label)

    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(10,90)
    $textBox.Size = New-Object System.Drawing.Size(260,60)
    $textBox.TabIndex = 1
    $form.Controls.Add($textBox)  
        
    $textBox.Add_TextChanged({
        $days = [int]$textBox.Text.Trim()
        $AllowedDays = '(1095|1460|1826|2191|2556|2922|3288|3653|4018|4383)'
        if ($days -in 4..730 -or $days -match $AllowedDays) {         
            $okButton.Enabled = $true
            $ErrorProvider.Clear()
        }
        else {
            $ErrorProvider.SetError($textBox, "Allowed values are: [4-730], 1095, 1460, 1826, 2191, 2556, 2922, 3288, 3653, 4018, 4383 days")  
            $okButton.Enabled = $false            
        } 
    }) 

    $ErrorProvider = New-Object System.Windows.Forms.ErrorProvider
    $form.Add_Shown({$form.Activate()})
    $form.Add_Shown({$textBox.Select()})
    $form.Topmost = $true    
    $result = $form.ShowDialog()

    if ($result -eq [System.Windows.Forms.DialogResult]::OK)
    {
        $days = [int]$textBox.Text.Trim()        
        return $days  
    }
    else {
        exit
    }
}

function Select-Plan {    
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
   

    # Create a new form
    $logselectform = New-Object System.Windows.Forms.Form
    $logselectform.Text = 'Table Plan'

    # Get the primary screen
    $primaryScreen = [System.Windows.Forms.Screen]::PrimaryScreen

    # Set the form size and position
    $formWidth = $primaryScreen.WorkingArea.Width * 0.2  # Adjust the form width as desired (80% of screen width in this example)
    $formHeight = $primaryScreen.WorkingArea.Height * 0.2  # Adjust the form height as desired (80% of screen height in this example)
    $formSize = New-Object System.Drawing.Size($formWidth, $formHeight)
    $logselectform.ClientSize = $formSize

    $logselectform.StartPosition = 'CenterScreen'
    
    $okb = New-Object System.Windows.Forms.Button
    $okb.Location = New-Object System.Drawing.Point(75,50)
    $okb.Size = New-Object System.Drawing.Size(105,30)
    $okb.Text = 'Basic Logs'
    $okb.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $logselectform.AcceptButton = $okb
    $logselectform.Controls.Add($okb)
    
    $cb = New-Object System.Windows.Forms.Button
    $cb.Location = New-Object System.Drawing.Point(195,50)
    $cb.Size = New-Object System.Drawing.Size(105,30)
    $cb.Text = 'Analytics Logs'
    $cb.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $logselectform.CancelButton = $cb
    $logselectform.Controls.Add($cb)    

    $rs = $logselectform.ShowDialog()
    if ($rs -eq [System.Windows.Forms.DialogResult]::OK) {
        return "Basic"
    }
    elseif ($rs -eq [System.Windows.Forms.DialogResult]::Cancel) {
        return "Analytics"
    }
}

function Get-Confirmation {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
     # Create a new form
     $logselectform = New-Object System.Windows.Forms.Form
     $logselectform.Text = 'Table Plan'
 
     # Get the primary screen
     $primaryScreen = [System.Windows.Forms.Screen]::PrimaryScreen
 
     # Set the form size and position
     $formWidth = $primaryScreen.WorkingArea.Width * 0.2  # Adjust the form width as desired (80% of screen width in this example)
     $formHeight = $primaryScreen.WorkingArea.Height * 0.2  # Adjust the form height as desired (80% of screen height in this example)
     $formSize = New-Object System.Drawing.Size($formWidth, $formHeight)
     $logselectform.ClientSize = $formSize
 
     $logselectform.StartPosition = 'CenterScreen'

    $label = New-Object System.Windows.Forms.Label
    $label.Location = New-Object System.Drawing.Point(40,40)
    $label.Size = New-Object System.Drawing.Size(250,20)
    $label.Text = 'Do you want to continue?'
    $logselectform.Controls.Add($label)

    $okb = New-Object System.Windows.Forms.Button
    $okb.Location = New-Object System.Drawing.Point(45,75)
    $okb.Size = New-Object System.Drawing.Size(75,25)
    $okb.Text = 'Continue'
    $okb.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $logselectform.AcceptButton = $okb
    $logselectform.Controls.Add($okb)

    $cb = New-Object System.Windows.Forms.Button
    $cb.Location = New-Object System.Drawing.Point(135,75)
    $cb.Size = New-Object System.Drawing.Size(75,25)
    $cb.Text = 'Exit'
    $cb.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $logselectform.CancelButton = $cb
    $logselectform.Controls.Add($cb)    

    
    $rs = $logselectform.ShowDialog()
    if ($rs -eq [System.Windows.Forms.DialogResult]::OK) {
        return $true
    }
    elseif ($rs -eq [System.Windows.Forms.DialogResult]::Cancel) {
        return $false
    }
}

#endregion

#region DriverProgram

# Check Powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Log "Supported PowerShell version for this script is 5 or above" -LogFileName $LogFileName -Severity Error    
    exit
}

$AzModulesQuestion = "Do you want to update required Az Modules to latest version?"
$AzModulesQuestionChoices = New-Object Collections.ObjectModel.Collection[Management.Automation.Host.ChoiceDescription]
$AzModulesQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&Yes'))
$AzModulesQuestionChoices.Add((New-Object Management.Automation.Host.ChoiceDescription -ArgumentList '&No'))

$AzModulesQuestionDecision = $Host.UI.PromptForChoice($title, $AzModulesQuestion, $AzModulesQuestionChoices, 1)

if ($AzModulesQuestionDecision -eq 0) {
    $UpdateAzModules = $true
}
else {
    $UpdateAzModules = $false
}

Get-RequiredModules("Az.Accounts")
Get-RequiredModules("Az.OperationalInsights")

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "Sentinel_Long_Term_Retention", $TimeStamp


#disconnect exiting connections and clearing contexts.
Write-Log "Clearing existing Azure connection" -LogFileName $LogFileName -Severity Information
    
$null = Disconnect-AzAccount -ContextName 'MyAzContext' -ErrorAction SilentlyContinue
    
Write-Log "Clearing existing Azure context `n" -LogFileName $LogFileName -Severity Information
    
get-azcontext -ListAvailable | ForEach-Object{$_ | remove-azcontext -Force -Verbose | Out-Null} #remove all connected content
    
Write-Log "Clearing of existing connection and context completed." -LogFileName $LogFileName -Severity Information
Try {
    #Connect to tenant with context name and save it to variable
    $AzContext = Connect-AzAccount -Tenant $TenantID -ContextName 'MyAzContext' -Force -ErrorAction Stop
        
    #Select subscription to build
    $GetSubscriptions = Get-AzSubscription -TenantId $TenantID | Where-Object {($_.state -eq 'enabled') } | Out-GridView -Title "Select Subscription to Use" -PassThru       
}
catch {    
    Write-Log "Error When trying to connect to tenant : $($_)" -LogFileName $LogFileName -Severity Error
    exit    
}

#Set API endpoints
if ($AzContext.Context.Environment.Name.Trim() -eq "AzureUSGovernment") {
    $APIEndpoint = "management.usgovcloudapi.net"
}
else {
    $APIEndpoint = "management.azure.com"    
}

$AzureAccessToken = (Get-AzAccessToken).Token            
$LaAPIHeaders = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$LaAPIHeaders.Add("Content-Type", "application/json")
$LaAPIHeaders.Add("Authorization", "Bearer $AzureAccessToken")

#loop through each selected subscription.. 
foreach($CurrentSubscription in $GetSubscriptions)
{
    Try 
    {
        #Set context for subscription being built
        $null = Set-AzContext -Subscription $CurrentSubscription.id
        $SubscriptionId = $CurrentSubscription.id
        Write-Log "Working in Subscription: $($CurrentSubscription.Name)" -LogFileName $LogFileName -Severity Information

        $LAWs = Get-AzOperationalInsightsWorkspace | Where-Object { $_.ProvisioningState -eq "Succeeded" } | Select-Object -Property Name, ResourceGroupName, Location | Out-GridView -Title "Select Log Analytics workspace" -PassThru 
        if($null -eq $LAWs) {
            Write-Log "No Log Analytics workspace found..." -LogFileName $LogFileName -Severity Error 
        }
        else {
            Write-Log "Listing Log Analytics workspace" -LogFileName $LogFileName -Severity Information
                        
            foreach($LAW in $LAWs) {
                
                $LogAnalyticsWorkspaceName = $LAW.Name
                $LogAnalyticsResourceGroup = $LAW.ResourceGroupName                            
                DO {
                    $tablePlan = Select-Plan
                    if ($tablePlan.Trim() -eq "Analytics") {
                        #Get all the tables from the selected Azure Log Analytics Workspace
                        $SelectedTables = Get-LATables -RetentionMethod $tablePlan.Trim() -APIEndpoint $APIEndpoint
                        if($SelectedTables) {
                            $WorkspaceRetention = $SelectedTables[0].RetentionInWorkspace
                            $TotalRetentionInDays = Collect-AnalyticsPlanRetentionDays -WorkspaceLevelRetention $WorkspaceRetention -TableLevelRetentionLimit 2555
                            $AnalyticsPlanTables = Set-TableConfiguration -QualifiedTables $SelectedTables -RetentionType $tablePlan.Trim() -APIEndpoint $APIEndpoint
                            $UpdatedTables = Update-TablesRetention -TablesForRetention $AnalyticsPlanTables -TotalRetentionInDays $TotalRetentionInDays -APIEndpoint $APIEndpoint                   
                            $UpdatedTables | Sort-Object -Property TableName | Select-Object -Property TableName, RetentionInWorkspace, RetentionInArchive, TotalLogRetention, IngestionPlan | Out-GridView -Title "$($tablePlan.Trim()) Plan updated Tables" -PassThru
                        }
                        else {
                            exit
                        }
                    }
                    elseif ($tablePlan.Trim() -eq "Basic") {
                        $SelectedTables = Get-LATables -RetentionMethod $tablePlan.Trim() -APIEndpoint $APIEndpoint                   
                        $BasicPlanTables = Set-TableConfiguration -QualifiedTables $SelectedTables -RetentionType $tablePlan.Trim() -APIEndpoint $APIEndpoint                                      
                        $BasicPlanTables | Sort-Object -Property TableName | Select-Object -Property TableName, RetentionInWorkspace, RetentionInArchive, TotalLogRetention, IngestionPlan | Out-GridView -Title "$($tablePlan.Trim()) Plan updated Tables" -PassThru                    
                    }
                    
                    $GetConfirmation = Get-Confirmation
                } While ($GetConfirmation -eq $true)
            }                  

        } 	
    }
    catch [Exception]
    { 
        Write-Log -Message $_ -LogFileName $LogFileName -Severity Error                         		
    }		 
}
#endregion DriverProgram 
