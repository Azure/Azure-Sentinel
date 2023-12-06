# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()
##TODO: need to move params and validations
[int]$maxMainQueuemessages=150
[int]$maxdurationminutes=10
# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}
$script_start_time=([System.DateTime]::UtcNow)
# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

<#
.SYNOPSIS
This method used for posting to queue
.DESCRIPTION
Long description

.PARAMETER message
$message from convert json from object

.EXAMPLE
An example

.NOTES
General methods
#>
function CreateQueue($queueNameParameter)
{
   
try
{
    if(-not([string]::IsNullOrWhiteSpace($carbonBlackStorage)) -and -not([string]::IsNullOrWhiteSpace($queueNameParameter)))
    {
        $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
        if ($null -ne $ctx)
        {
            
            $queue = Get-AzStorageQueue –Name $queueNameParameter –Context $ctx
            if(-not $queue)
            {
               #Creating the queue
               $queue = New-AzStorageQueue –Name $queueNameParameter -Context $ctx  
            }
            else {
                
                #Queue already present
            }         
        }
        else
        {
          Write-Host "Storage context not available"
        }
    }
    else
    {
        Write-Host "Input parameters are empty"
    }
}
catch {
    Write-Host $_
}

}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function GetStrgContext()
{
if(-not([string]::IsNullOrWhiteSpace($carbonBlackStorage)))
{
 $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
 return $ctx
}

}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.PARAMETER queueN
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function GetQCount($qNameParam)
{
    $context=GetStrgContext
    $messageCount = (Get-AzStorageQueue -Context $context | where-object{$_.name -eq $qNameParam}).ApproximateMessageCount
    return $messageCount
}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.PARAMETER messageId
Parameter description

.PARAMETER popreceipt
Parameter description

.PARAMETER queueNms
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function  DeleteMessageFrmQueue($messageId,$popreceipt,$queueNameForMsg)
{
    $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
    if ($ctx -ne $null)
    {
      $queue = Get-AzStorageQueue –Name $queueNameForMsg –Context $ctx
    }
    else
    {
      Write-Host "Storage context not available"
    }
    if ($queue -ne $null) 
    {  
       $status= $queue.CloudQueue.DeleteMessageAsync($messageId,$popreceipt).GetAwaiter().GetResult()

       if($status -ne $null)
       {
         Write-Host "Message Deleted successfully from Quque:" $queueNameForMsg "MessageId is:" $messageId
       }
       else {
        
        Write-Host "Message not Deleted successfully"
        
       }

    }
    else
    {
      Write-Host "unable to get queue details"
    }
}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.PARAMETER queueNm
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function GetMessageFromQueue($getQueueMsg)
{
    $ctx=GetStrgContext
    $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
    if ($ctx -ne $null)
    {
      $queue = Get-AzStorageQueue –Name $getQueueMsg –Context $ctx
    }
    else
    {
      Write-Host "Storage context not available"
    }
    if ($queue -ne $null) 
    {  
        $invisibleTimeout = [System.TimeSpan]::FromSeconds(10)
        $status= $queue.CloudQueue.GetMessageAsync($invisibleTimeout,$null,$null)
       if($status -ne $null)
       {
        Write-Host "Message sent from queue" $getQueueMsg $status.Result
        return $status.Result
        
       }

    }
    else
    {
      Write-Host "unable to get queue details"
    }
}
<#
.SYNOPSIS
##

.DESCRIPTION
Long description

.PARAMETER percentage
Parameter description

.PARAMETER script_start_time
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function check_if_script_run_too_long($percentage, $script_start_time)
{
 [int]$seconds=(60)
 [int]$duration = $(([System.DateTime]::UtcNow - $script_start_time).Seconds)
 [int]$temp=$maxdurationminutes * $seconds 
 [double]$maxduration= $temp * 0.8
 return $duration -gt $maxduration
}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.PARAMETER message
Parameter description

.PARAMETER queueN
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function CreateQueuePostMsgToQueue($message,$queueMsgToBePosted)
{
   
try
{
    if(-not([string]::IsNullOrWhiteSpace($message)) -and -not([string]::IsNullOrWhiteSpace($carbonBlackStorage)) -and -not([string]::IsNullOrWhiteSpace($queueMsgToBePosted)))
    {
        $ctx = New-AzStorageContext -ConnectionString $carbonBlackStorage
        if ($null -ne $ctx)
        {
            
            $queue = Get-AzStorageQueue –Name $queueMsgToBePosted –Context $ctx
            if(-not $queue)
            {
               #Creating the queue
               $queue = New-AzStorageQueue –Name $queueMsgToBePosted -Context $ctx  
            }
            else {
                
                #Queue already present
            }         
        }
        else
        {
          Write-Host "Storage context not available"
        }
        if ($null -ne $queue) 
        {  
           
           $queueMessage = [Microsoft.Azure.Storage.Queue.CloudQueueMessage]::new(($message))
           
           $status=$queue.CloudQueue.AddMessageAsync($queueMessage).GetAwaiter().GetResult()
        }
        else
        {
          Write-Host "unable to get queue details"
        }
        if($null -ne $status)
        {
          Write-Host "Queue Message added Successfully to quque:" $queueMsgToBePosted "and message is:" $message
        }
        else 
        {  
           Write-Host "Queue Message not added Successfully" $message
        }
    }
    else
    {
        Write-Host "Input parameters are empty"
    }
}
catch {
    Write-Host $_
}

}
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function ProcessBacklog()
{
  try
{
    $queueName=$env:queueName
    $backlogQueue=$env:backlogQueue
    $carbonBlackStorage=$env:AzureWebJobsStorage
    ##Creating queue if not present
    CreateQueue($queueName)
    CreateQueue($backlogQueue)
    $backlogcount=GetQCount -qNameParam $backlogQueue
    #Get backlog count
    while($backlogcount -gt 0)
    {
      try {
        
        if((GetQCount -qNameParam $queueName) -lt $maxMainQueuemessages)
        {
            $msg=GetMessageFromQueue($backlogQueue)
            if($null -ne $msg)
            {
                   CreateQueuePostMsgToQueue -message $msg.AsString -queueMsgToBePosted $queueName
                   DeleteMessageFrmQueue -messageId $msg.Id -popreceipt $msg.PopReceipt -queueNameForMsg $backlogQueue
            }
            else {
              Write-Host "There is no message in backlog queue"
            }
        }
        if((GetQCount -qNameParam $queueName) -eq $maxMainQueuemessages)
        {
             return
        }
        if((check_if_script_run_too_long -percentage 0.8 -script_start_time $script_start_time))
        {
            return
        }
        $backlogcount=GetQCount -qNameParam $backlogQueue
      }
      catch {
        postCheckpointLastFailure($msg)
        Write-Host "There are errors while processing Msg to Main queue" $msg
      }
    }
  }
  catch {
    Write-Host "Error, error message: $($Error[0].Exception.Message)"
}

}

ProcessBacklog
