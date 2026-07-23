<#
.SYNOPSIS
    Converts Azure VM snapshots to VHD files and downloads them for digital forensics incident response (DFIR).

.DESCRIPTION
    Facilitates digital forensics incident response (DFIR) by converting Azure VM snapshots to VHD format in Azure Blob Storage 
    and then downloads the VHD(s) to a local VM for analysis.

    This PowerShell script is designed to be run elevated as an analyst on an Azure VM dedicated to forensics analysis.

    The following modules are required to run this script on the DFIR computer:
        Az.Accounts, Az.Resources, Az.Storage, and Az.Compute

    Run the following commands to ensure these modules are first successfully installed on the computer:
        Install-Module Az.Accounts, Az.Resources, Az.Storage, Az.Compute -Force

    DIRECTIONS:
    ----------
    1. Ensure your environment meets, or exceeds, the accompanying solution requirements for the solution.
    2. Ensure the prerequisite modules are installed.
    3. Open the script in PowerShell ISE on the DFIR VM.
    4. Update the variables in 'Variables' section to match your environment per the accompanying documentation.
    5. Open an elevated PowerShell prompt and then execute the script: .\Convert-SnapshotsToVHD.ps1
#>

###########################################################################################################
# VARIABLES: Update to match your environment and then save the script
###########################################################################################################
$AzEnvironment = "AzureCloud"                          # Adjust to match target Azure fabric: (Get-AzEnvironment).Name
$Subscription = "98765432-10fe-9876-fedc-ba0987654321" # DFIR Subscription hosting the snapshots
$RG = "SOC-DFIR-RG"                                    # DFIR Resource Group that was deployed
$StorageAccountName = "socdfir01"                      # DFIR storage account name that was deployed
$StorageContainerName = "vhd"                          # Azure blob storage container name that was deployed
$ImagesDir = "F:\Disks"                                # Drive location to copy VHDs for forensic analysis (local directory)
[Int32]$SASDurationInSeconds = "3600"                  # Shared Access Signature (SAS) duration in seconds (default = 3600)

###########################################################################################################
# FUNCTIONS
###########################################################################################################

Function Show-SnapshotsMenu {
    param (
        [Parameter(Mandatory = $true)]
        $AzSnapshots
    )

    Add-Type -AssemblyName System.Windows.Forms

    # Create a new form
    $Form = New-Object System.Windows.Forms.Form
    $Form.Text = "Select Snapshot(s) to Convert to VHD(s)"
    $Form.Size = New-Object System.Drawing.Size(800, 400)

    # Create a DataGridView
    $DataGridView = New-Object System.Windows.Forms.DataGridView
    $DataGridView.Size = New-Object System.Drawing.Size(740, 300)
    $DataGridView.Location = New-Object System.Drawing.Point(20, 20)
    $DataGridView.AutoGenerateColumns = $false
    $DataGridView.AllowUserToAddRows = $false
    $DataGridView.AllowUserToDeleteRows = $false
    $DataGridView.AllowUserToResizeRows = $false
    $DataGridView.AllowUserToResizeColumns = $true
    $DataGridView.ColumnHeadersDefaultCellStyle.BackColor = [System.Drawing.Color]::LightBlue
    $DataGridView.EnableHeadersVisualStyles = $false

    # Add columns to the DataGridView
    $CheckboxColumn = New-Object System.Windows.Forms.DataGridViewCheckBoxColumn
    $CheckboxColumn.HeaderText = "Select"
    $CheckboxColumn.Width = 50
    $DataGridView.Columns.Add($CheckboxColumn) | Out-Null

    $SnapshotNameColumn = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
    $SnapshotNameColumn.HeaderText = "SnapshotName"
    $SnapshotNameColumn.Width = 300
    $DataGridView.Columns.Add($SnapshotNameColumn) | Out-Null

    $TimeCreatedColumn = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
    $TimeCreatedColumn.HeaderText = "TimeCreated"
    $TimeCreatedColumn.Width = 150
    $DataGridView.Columns.Add($TimeCreatedColumn) | Out-Null

    $DiskSizeGBColumn = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
    $DiskSizeGBColumn.HeaderText = "DiskSizeGB"
    $DiskSizeGBColumn.Width = 80
    $DataGridView.Columns.Add($DiskSizeGBColumn) | Out-Null

    $SourceResourceIdColumn = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
    $SourceResourceIdColumn.HeaderText = "SourceDisk"
    $SourceResourceIdColumn.Width = 100
    $DataGridView.Columns.Add($SourceResourceIdColumn) | Out-Null

    # Add rows to the DataGridView
    foreach ($AzSnapshot in $AzSnapshots) {
        $Row = $DataGridView.Rows.Add()
        $DataGridView.Rows[$Row].Cells[1].Value = $AzSnapshot.Name
        $DataGridView.Rows[$Row].Cells[2].Value = $AzSnapshot.TimeCreated
        $DataGridView.Rows[$Row].Cells[3].Value = $AzSnapshot.DiskSizeGB
        $DataGridView.Rows[$Row].Cells[4].Value = $AzSnapshot.CreationData.SourceResourceId
    }

    # Add the DataGridView to the form
    $Form.Controls.Add($DataGridView)

    # Set background color of every other row
    $RowRGB = [System.Drawing.Color]::FromArgb(224, 248, 231)
    $DataGridView.add_RowPrePaint({
        param ($sender, $e)
        If ($e.RowIndex % 2 -eq 1) {
            $DataGridView.Rows[$e.RowIndex].DefaultCellStyle.BackColor = $RowRGB
        }
    })

    # Add an OK button to the form
    $OkButton = New-Object System.Windows.Forms.Button
    $OkButton.Text = "OK"
    $OkButton.Location = New-Object System.Drawing.Point(340, 330)
    $OkButton.Add_Click({
        $SelectedItems = @()
        foreach ($Row in $DataGridView.Rows) {
            If ($Row.Cells[0].Value -eq $true) {
                $SelectedItems += [PSCustomObject]@{
                    Name = $Row.Cells[1].Value
                    TimeCreated = $Row.Cells[2].Value
                    DiskSizeGB = $Row.Cells[3].Value
                    SourceResourceId = $Row.Cells[4].Value
                }
            }
        }
        $Form.Tag = $SelectedItems
        $Form.Close()
    })
    $Form.Controls.Add($OkButton)

    # Display the form
    [System.Windows.Forms.Application]::Run($Form)
    #$Form.ShowDialog()

    # Get the selected snapshots
    $SelectedSnapshots = $Form.Tag
    $Form.Dispose()
    return ,$SelectedSnapshots
}

Function Get-ConvertedSnapshotToVHD {
    param (
        [Parameter(Mandatory = $true)]
        $Snapshot
    )

    [string]$SnapshotName = $Snapshot.Name
    [string]$VHDFileName = "$SnapshotName.vhd"

    Write-Host "`nConverting Snapshot: $SnapshotName" -ForegroundColor Yellow

    # Generate a SAS URI for the snapshot
    Write-Host "Generating SAS URI for: $SnapshotName"
    $SAS = Grant-AzSnapshotAccess -ResourceGroupName $RG -SnapshotName $SnapshotName -Access Read -DurationInSecond $SASDurationInSeconds
    $StorageAccountKey = (Get-AzStorageAccountKey -ResourceGroupName $RG -Name $StorageAccountName | Where-Object {$_.Permissions -eq "Full"} | Sort-Object KeyName)[0].Value

    # Create the destination context for the storage account which will be used to copy snapshot to the storage account
    $StorageContext = New-AzStorageContext -StorageAccountName $StorageAccountName -StorageAccountKey $StorageAccountKey

    # Copy snapshot to a VHD in Azure Blob storage and wait for completion
    Write-Host "Copying snapshot to VHD: $VHDFileName"
    $CopyJob = Start-AzStorageBlobCopy -AbsoluteUri $SAS.AccessSAS -DestContainer $StorageContainerName -DestContext $StorageContext -DestBlob $VHDFileName
    $CopyStatus = $CopyJob | Get-AzStorageBlobCopyState
    While ($CopyStatus.Status -eq "Pending")
    {
        $CopyStatus = $CopyJob | Get-AzStorageBlobCopyState 
        $Calc = ($CopyStatus.BytesCopied / $CopyStatus.TotalBytes) * 100
        $Percent = "{0:N2}" -f $Calc
        Write-Progress -Activity "Waiting for snapshot copy to $VHDFileName to complete..." -Status "Percent : $Percent%.." -PercentComplete "$Percent"
        Start-Sleep 10
    }

    # Download the VHD
    If ((Get-AzStorageBlobCopyState -Container $StorageContainerName -Context $StorageContext -Blob $VHDFileName).Status -eq "Success") 
    {
        Write-Host "Downloading to: $ImagesDir\$VHDFileName"
        Get-AzStorageBlobContent -Container $StorageContainerName -Context $StorageContext -Blob $VHDFileName -Destination "$ImagesDir\$VHDFileName"
    }
    Get-Item "$ImagesDir\$VHDFileName" | Unblock-File
}

###########################################################################################################
# MAIN ROUTINE
###########################################################################################################

# 1. Set Prereqs
# ---------------------------------------------------------------------------------------------------------
Write-Host "`nSetting prerequisites..."
If ((Get-MpPreference).ExclusionExtension -notcontains ".vhd") {Add-MpPreference -ExclusionExtension ".vhd" -Force}

$Modules = "Az.Accounts", "Az.Resources", "Az.Storage", "Az.Compute"
foreach ($Module in $Modules) {
    If (!(Get-Module -ListAvailable -Name $Module)) {
        Write-Host "$Module is not installed. Installing now..."
        Install-Module -Name $Module -Force -AllowClobber
    }
}

Import-Module Az.Accounts, Az.Resources, Az.Storage, Az.Compute

# 2. Connect to Azure
# ---------------------------------------------------------------------------------------------------------
Write-Host "`nAttempting to connect to Azure fabric: $AzEnvironment" -ForegroundColor Yellow
Get-AzEnvironment
Connect-AzAccount -Environment $AzEnvironment
Set-AzContext -Subscription $Subscription

# 3. Get snapshot(s)
# ---------------------------------------------------------------------------------------------------------
$AzSnapshots = Get-AzSnapshot -ResourceGroupName $RG | Select-Object Name, TimeCreated, DiskSizeGB, CreationData | Sort-Object Name, TimeCreated
$Snapshots = Show-SnapshotsMenu ($AzSnapshots)

# 4. Convert snapshot(s) to VHD(s) in Azure blob storage and then download to local drive
# ---------------------------------------------------------------------------------------------------------
If ($Snapshots.Count -gt 0) {
    Write-Host "`nSelected Snapshot(s):" -ForegroundColor Yellow
    $Snapshots | Format-Table -AutoSize
    foreach ($Snapshot in $Snapshots) {Get-ConvertedSnapshotToVHD ($Snapshot)}
}
Else {
    Write-Host "No snapshot(s) were selected. Exiting..." -ForegroundColor White -BackgroundColor Red
}

# 5. List VHD(s) in $ImagesDir
# ---------------------------------------------------------------------------------------------------------
If ($Snapshots.Count -gt 0) {
    Write-Host "`nDownloaded VHD(s):" -ForegroundColor Yellow
    Get-ChildItem -Path $ImagesDir -Filter "*.vhd" | Select-Object FullName, LastWriteTime, Length | Sort-Object FullName, LastWriteTime | Format-Table -AutoSize
}
