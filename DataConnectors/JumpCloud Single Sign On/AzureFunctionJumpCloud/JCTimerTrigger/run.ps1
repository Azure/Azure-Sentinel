# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "JumpCloud timer triggered and is running late! TIME: $currentUTCtime"
}
else {
# Write an information log with the current time.
Write-Host "JumpCloud timer triggered and is running on time! TIME: $currentUTCtime"
}

#Retrieve Environment Variables
$AzureWebJobsStorage =$env:AzureWebJobsStorage 
$JCEventTypes = $env:JumpCloudEventTypes
$JCQueuename = "jcqueue"

#connect to Queue
$JCstorage =  New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$check2="all directory radius sso systems ldap mdm"

if(( Get-AzstorageQueue -context $JCStorage -Name $JCQueuename -ErrorAction SilentlyContinue ).name ){
    $JCqueue = Get-AzStorageQueue -Name $JCQueuename -Context $JCStorage
    } 

else{
    $JCqueue = New-AzStorageQueue -Name $JCQueuename -Context $JCStorage
    }
#Validate JumpCloud Event TYpes requested
$JCeventTypes = $JCEventTypes.ToLower()
$JCEventTypes = $JCEventTypes -replace ",|:| ",";"
$JCEvents = $JCEventTypes.split(';')

#Trigger via Queue Rest API call to JumpCloud
$JCEvents | ForEach-Object -Process { 
    if($check2 -like '* '+$_+' *'){
        $queueMessage = [Microsoft.Azure.Storage.Queue.CloudQueueMessage]::new($_)
        $JCqueue.CloudQueue.AddMessageAsync($QueueMessage)
    }
}
