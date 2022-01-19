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
           
    
    .PARAMETER TenantId
        Enter Azure Tenant Id (required)  

    .NOTES
        AUTHOR: Sreedhar Ande
        LASTEDIT: 1/18/2022

    .EXAMPLE
        .\Configure-Long-Term-Retention.ps1 -TenantId xxxx
#>

#region UserInputs

param(
    [parameter(Mandatory = $true, HelpMessage = "Enter your Tenant Id")]
    [string] $TenantID    
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
            Write-Log -Message "Checking updates for module $Module" -LogFileName $LogFileName -Severity Information
            $versions = Find-Module $Module -AllVersions
            $latestVersions = ($versions | Measure-Object -Property Version -Maximum).Maximum.ToString()
            $currentVersion = (Get-InstalledModule | Where-Object {$_.Name -eq $Module}).Version.ToString()
            if ($currentVersion -ne $latestVersions) {
                #check for Admin Privleges
                $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())

                if (-not ($currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))) {
                    #Not an Admin, install to current user            
                    Write-Log -Message "Can not update the $Module module. You are not running as Administrator" -LogFileName $LogFileName -Severity Warning
                    Write-Log -Message "Updating $Module module to current user Scope" -LogFileName $LogFileName -Severity Warning
                    
                    Install-Module -Name $Module -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
                    Import-Module -Name $Module -Force
                }
                else {
                    #Admin, install to all users																		   
                    Write-Log -Message "Updating the $Module module to all users" -LogFileName $LogFileName -Severity Warning
                    Install-Module -Name $Module -Repository PSGallery -Force -AllowClobber
                    Import-Module -Name $Module -Force
                }
            }
            else {
                Write-Log -Message "Importing module $Module" -LogFileName $LogFileName -Severity Information
                Import-Module -Name $Module -Force
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
        [parameter(Mandatory = $true)] $RetentionMethod                
    )
	
	$TablesArray = New-Object System.Collections.Generic.List[System.Object]
	
	try {       
        Write-Log -Message "Retrieving tables from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Information
        $WSTables = Get-AzOperationalInsightsTable -ResourceGroupName $LogAnalyticsResourceGroup -WorkspaceName $LogAnalyticsWorkspaceName
                                         
        if ($RetentionMethod -eq "Analytics") {        
            $searchPattern = '(_CL|_SRCH|ContainerLog^|ContainerLogV2|AppTraces)'        
            $TablesArray = $WSTables.Name -notmatch $searchPattern | Out-GridView -Title "Select Table (For Multi-Select use CTRL)" -PassThru
        }
        else {
            $searchPattern = '(_CL|ContainerLog^|ContainerLogV2|AppTraces)'        
            $TablesArray = $WSTables.Name -match $searchPattern | Out-GridView -Title "Select Table (For Multi-Select use CTRL)" -PassThru
        }            
       
    }
    catch {
        Write-Log $_ -LogFileName $LogFileName -Severity Error
        Write-Log -Message "An error occurred in querying table names from $LogAnalyticsWorkspaceName" -LogFileName $LogFileName -Severity Error         
        exit
    }
	
	return $TablesArray	
}


function Get-TableConfiguration {
	[CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $LaTables        
    )
	$QualifiedTables = @{}
	
	foreach ($LaTable in $LaTables) {
		$TablesApi = "https://management.azure.com/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$LogAnalyticsWorkspaceName/tables/$LaTable" + "?api-version=2021-07-01-privatepreview"
				
		try {        
			$TablesApiResult = Invoke-RestMethod -Uri $TablesApi -Method "GET" -Headers $LaAPIHeaders		
		} 
		catch {                    
			Write-Log -Message "Get-TableConfiguration $($_)" -LogFileName $LogFileName -Severity Error		                
		}

		If ($TablesApiResult) {        
            Write-Log -Message "$LaTable configuration : $($TablesApiResult.properties)" -LogFileName $LogFileName -Severity Information   
            $QualifiedTables.Add($LaTable, $TablesApiResult.properties.retentionInDays)
		}
	}
	
	return $QualifiedTables
}


function Set-TableConfiguration {
	[CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $QualifiedTables,
		[parameter(Mandatory = $true)] $RetentionType
    )
	
	$SuccessTables = @{}
	
    $QualifiedTables.GetEnumerator() | ForEach-Object {	
		$TablesApi = "https://management.azure.com/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$LogAnalyticsWorkspaceName/tables/$($_.Key)" + "?api-version=2021-07-01-privatepreview"								
		
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
            $SuccessTables.Add($($_.Key), $($_.Value))		
		}
	}
    return $SuccessTables
}


function Update-TablesRetention {
	[CmdletBinding()]
    param (        
        [parameter(Mandatory = $true)] $TablesForRetention,		
		[parameter(Mandatory = $true)] $TotalRetentionInDays
    )
	$UpdatedTablesRetention = @{}	
	$TablesForRetention.GetEnumerator() | ForEach-Object {
		$TablesApi = "https://management.azure.com/subscriptions/$SubscriptionId/resourcegroups/$LogAnalyticsResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$LogAnalyticsWorkspaceName/tables/$($_.Key)" + "?api-version=2021-07-01-privatepreview"						
		
		$TablesApiBody = @"
			{
				"properties": {
					"retentionInDays": 90,
					"totalRetentionInDays":$TotalRetentionInDays
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
            $UpdatedTablesRetention.Add($($_.Key), $TotalRetentionInDays)
            Write-Log -Message "Table : $($_.Key) retention updated successfully from $($_.Value) days to $TotalRetentionInDays" -LogFileName $LogFileName -Severity Information
        }		
	}
    return $UpdatedTablesRetention
}

function Collect-Input {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = 'Table Plan:Analytics'
    $form.Size = New-Object System.Drawing.Size(400,300)
    $form.StartPosition = 'CenterScreen'

    $okButton = New-Object System.Windows.Forms.Button
    $okButton.Location = New-Object System.Drawing.Point(75,120)
    $okButton.Size = New-Object System.Drawing.Size(75,23)
    $okButton.Text = 'OK'
    $okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $form.AcceptButton = $okButton
    $form.Controls.Add($okButton)
    $okButton.Enabled = $false    

    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Location = New-Object System.Drawing.Point(170,120)
    $cancelButton.Size = New-Object System.Drawing.Size(75,23)
    $cancelButton.Text = 'Cancel'
    $cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $form.CancelButton = $cancelButton
    $form.Controls.Add($cancelButton)

    $label = New-Object System.Windows.Forms.Label
    $label.Location = New-Object System.Drawing.Point(10,20)
    $label.Size = New-Object System.Drawing.Size(400,60)
    $label.Text = 'Enter value for total Retention In Days (between 7 and 2555)*'
    $form.Controls.Add($label)

    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(10,80)
    $textBox.Size = New-Object System.Drawing.Size(260,20)
    $textBox.TabIndex = 1
    $form.Controls.Add($textBox)  
    
    $textBox.Add_TextChanged({
        $days = [int]$textBox.Text.Trim()
        if ($days -gt 7 -and $days -lt 2556) {         
            $okButton.Enabled = $true
            $ErrorProvider.Clear()
        }
        else {
            $ErrorProvider.SetError($textBox, "Field must be between 7 and 2555 days")  
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
    $logselectform = New-Object System.Windows.Forms.Form
    $logselectform.Text = 'Table Plan'
    $logselectform.Size = New-Object System.Drawing.Size(300,300)
    $logselectform.StartPosition = 'CenterScreen'
    $okb = New-Object System.Windows.Forms.Button
    $okb.Location = New-Object System.Drawing.Point(45,130)
    $okb.Size = New-Object System.Drawing.Size(75,25)
    $okb.Text = 'Basic Logs'
    $okb.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $logselectform.AcceptButton = $okb
    $logselectform.Controls.Add($okb)
    $cb = New-Object System.Windows.Forms.Button
    $cb.Location = New-Object System.Drawing.Point(150,130)
    $cb.Size = New-Object System.Drawing.Size(105,25)
    $cb.Text = 'Analytics Logs'
    $cb.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $logselectform.CancelButton = $cb
    $logselectform.Controls.Add($cb)    
    $rs = $logselectform.ShowDialog()
    if ($rs -eq [System.Windows.Forms.DialogResult]::OK)
    {
        return "Basic"
    }
    else {
        return "Analytics"
    }
}

#endregion

#region DriverProgram
Get-RequiredModules("Az")
Get-RequiredModules("Az.SecurityInsights")
Get-RequiredModules("Az.OperationalInsights")

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "Sentinel_Long_Term_Retention", $TimeStamp

# Check Powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Log "Supported PowerShell version for this script is 5 or above" -LogFileName $LogFileName -Severity Error    
    exit
}

#disconnect exiting connections and clearing contexts.
Write-Log "Clearing existing Azure connection" -LogFileName $LogFileName -Severity Information
    
$null = Disconnect-AzAccount -ContextName 'MyAzContext' -ErrorAction SilentlyContinue
    
Write-Log "Clearing existing Azure context `n" -LogFileName $LogFileName -Severity Information
    
get-azcontext -ListAvailable | ForEach-Object{$_ | remove-azcontext -Force -Verbose | Out-Null} #remove all connected content
    
Write-Log "Clearing of existing connection and context completed." -LogFileName $LogFileName -Severity Information
Try {
    #Connect to tenant with context name and save it to variable
    Connect-AzAccount -Tenant $TenantID -ContextName 'MyAzContext' -Force -ErrorAction Stop
        
    #Select subscription to build
    $GetSubscriptions = Get-AzSubscription -TenantId $TenantID | Where-Object {($_.state -eq 'enabled') } | Out-GridView -Title "Select Subscription to Use" -PassThru       
}
catch {    
    Write-Log "Error When trying to connect to tenant : $($_)" -LogFileName $LogFileName -Severity Error
    exit    
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
                
                $tablePlan = Select-Plan
                if ($tablePlan.Trim() -eq "Analytics") {
                    #Get all the tables from the selected Azure Log Analytics Workspace
                    $WorkspaceTables = Get-LATables -RetentionMethod $tablePlan.Trim()                    
                    $QualifiedTables = Get-TableConfiguration -LaTables $WorkspaceTables
                    $QualifiedTables | Out-GridView -Title "Current Retention Values" -PassThru
                    $TotalRetentionInDays = Collect-Input 
                    $ConfiguredTables = Set-TableConfiguration -QualifiedTables $QualifiedTables -RetentionType $tablePlan.Trim()
                    $UpdatedTables = Update-TablesRetention -TablesForRetention $ConfiguredTables -TotalRetentionInDays $TotalRetentionInDays                    
                    $QualifiedTables = Get-TableConfiguration -LaTables $WorkspaceTables
                    $UpdatedTables | Out-GridView -Title "Updated Retention Values" -PassThru
                }
                else {
                    $WorkspaceTables = Get-LATables -RetentionMethod $tablePlan.Trim()
                    $QualifiedTables = Get-TableConfiguration -LaTables $WorkspaceTables
                    $ConfiguredTables = Set-TableConfiguration -QualifiedTables $QualifiedTables -RetentionType $tablePlan.Trim()
                    Write-Log -Message "Basic plan updated successfully" -LogFileName $LogFileName -Severity Information
                    $UpdatedConfigs = $ConfiguredTables.Keys.ForEach('ToString')
                    Get-TableConfiguration -LaTables $UpdatedConfigs
                }
            }                  

        } 	
    }
    catch [Exception]
    { 
        Write-Log $_ -LogFileName $LogFileName -Severity Error                         		
    }		 
}
#endregion DriverProgram 
