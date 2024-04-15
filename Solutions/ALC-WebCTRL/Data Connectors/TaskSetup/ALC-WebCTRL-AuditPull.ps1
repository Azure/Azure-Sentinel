#Requires -version 4.0
#Requires -RunAsAdministrator

<#
.SYNOPSIS
Check if WebCtrl SQL service is running and if yes then install Audit Pull Task to read the Audit Data.

.DESCRIPTION
1. Checks if the ALC WebCtrl Service is installed on the server.
2. Checks if SQL Service is installed and running on the server.
2. If Yes, Execute statement to pull data from audit table 

.NOTES
Assumptions:
    - This process is running as a scheduled task under account that has access to the db

Date Created: 2021-10-27, initial version

ToDo:
#>

##############################################################################
# Constants
#
# Below constants are editable and can be updated based on the environment
#
##############################################################################
# Replace <path_to_directory> below variable value with a valid diretory
Set-Variable -Name lastReadTimeStampFile  -Option Constant -Value "<path_to_directory>" + "\WebCtrlAuditDataLastReadTime.txt"
Set-Variable -Name webCtrlDatabaseName  -Option Constant -Value "AUDIT"
Set-Variable -Name webCtrlTimeFormat  -Option Constant -Value "yyyy-MM-dd HH:mm:ss.fff"
Set-Variable -Name vbCrLf  -Option Constant -Value ([char]13 + [char]10)
Set-Variable -Name webCtrl  -Option Constant -Value 'WebCTRL Service'
Set-Variable -Name webCtrlSql  -Option Constant -Value 'MSSQLSERVER'
# Replace Event Id's 8001, 8002 below with any unused custom valid event id's. These will be used to log operational and atual data events
Set-Variable -Name executionSummaryEventId -Option Constant -Value 8001
Set-Variable -Name auditDataEventId -Option Constant -Value 8002


##############################################################################
# Check if the WebCtrl service exists
##############################################################################
$webCtrlService = (Get-Service -Name $webCtrl -ErrorAction SilentlyContinue)
If ( $webCtrlService -eq $null )
{
  $eventMessage = 'Script exiting as WebCtrl Service is not installed.' + $vbCrLf
  Write-EventLog -logname "Application" -Source "ALCWebCTRL"  -EventId $executionSummaryEventId -EntryType Information -Message $eventMessage -Category 0
  exit
}


##############################################################################
# Check if SQL service is installed and running
##############################################################################
$webCtrlSqlService = (Get-Service -Name $webCtrlSql -ErrorAction SilentlyContinue)
if ( $webCtrlSqlService -eq $null )
{
  $eventMessage = "SQL WebCtrl is not installed on this machine" + $vbCrLf
  Write-EventLog -logname "Application" -Source "ALCWebCTRL"  -EventId $executionSummaryEventId -EntryType Information -Message $eventMessage -Category 0
  exit
}
else
{
  if ( $webCtrlSqlService.Status -eq [System.ServiceProcess.ServiceControllerStatus]"Running" )
  {
    $webCtrlSqlServiceStatus = $webCtrlSqlService.Status.ToString()
    $eventMessage = "The service $webCtrlSqlService is $webCtrlSqlServiceStatus." + $vbCrLf
    Write-EventLog -logname "Application" -Source "ALCWebCTRL"  -EventId $executionSummaryEventId -EntryType Information -Message $eventMessage -Category 0
    $currentLocalDateTime =  Get-Date (Get-Date)
    $lastReadDateTime =  $currentLocalDateTime


    #################################################################################################################
    # Read time stamp at which the script last ran
    # 
    # The time stamp is saved/logged in a file(see constant $lastReadTimeStampFile) when the script runs.
    # If file exists then value is read, else use current local time stamp minus 30 minutes is set as default
    # The schedule is editable based on the requirement.
    #################################################################################################################
    if (Test-Path -Path $lastReadTimeStampFile -PathType Leaf) {
      $lastReadDateTime = (Get-Content $lastReadTimeStampFile -First 1)
    }
    else {
      $lastReadDateTime = $currentLocalDateTime.AddMinutes(-30).ToString($webCtrlTimeFormat)
      # NOTE: The time should match the schedule of the task to avoid duplicate data being read
    }
    $currentLocalDateTimeFormatted = $currentLocalDateTime.ToString($webCtrlTimeFormat)


    #################################################################################################################
    # Execute SQL query to read audit data between current and last run time stamp.
    #################################################################################################################
    $serverName = $env:COMPUTERNAME
    $query = "SELECT * FROM [$webCtrlDatabaseName].[dbo].[AUDITLOGDATA] WITH (NOLOCK) WHERE [DATE_STAMP_] > '$lastReadDateTime' AND [DATE_STAMP_] <= '$currentLocalDateTimeFormatted'"
    try {
      # The parameters can be edited based on the requirement. Please refer the Invoke-Sqlcmd command's documentation
      $queryResultSet = Invoke-Sqlcmd -ServerInstance $serverName -Query $query -QueryTimeout 65535
    } catch {
      $eventMessage = "Error when running sql $query" + $vbCrLf
      $Error.Clear()
      Write-EventLog -logname "Application" -Source "ALCWebCTRL"  -EventId $executionSummaryEventId -EntryType Information -Message $eventMessage -Category 0
      exit
    }


    #################################################################################################################
    # Log the data as windows events
    #################################################################################################################
    $queryResultData = $queryResultSet | Select-Object * -ExcludeProperty ItemArray, Table, RowError, RowState, HasErrors
    Foreach ($eachRecord in $queryResultData) {
      $eventMessage = $eachRecord | ConvertTo-Json
      Write-EventLog -logname "Application" -Source "ALCWebCTRL"  -EventId $auditDataEventId -EntryType Information -Message $eventMessage -Category 0
    }


    #################################################################################################################
    # Save the current time stamp in a file(see constant $lastReadTimeStampFile) to be used in next run
    #################################################################################################################
    $currentLocalDateTimeFormatted > $lastReadTimeStampFile

  }
}