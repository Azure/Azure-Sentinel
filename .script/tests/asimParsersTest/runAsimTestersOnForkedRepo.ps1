Param([string]$fork, [string]$branch, [string]$subscriptionId = "", [string]$workspaceId = "")

$global:failed=0

function run([string] $fork, [string] $branch, [string]$subscriptionId, [string]$workspaceId) {
    $repoBaseFolder = "$($PSScriptRoot)/../../../"

	$filesThatWereChanged=$(echo $(git diff --name-only))
	if($filesThatWereChanged) {
		Write-Error "Please commit your changes or stash them before run the script. "
	}
	else {   
        Write-Host "git remote add $($fork) https://github.com/$($fork)/Azure-Sentinel"
		git remote add $fork "https://github.com/$($fork)/Azure-Sentinel"

        Write-Host "git fetch $($fork)"
		git fetch $fork

        Write-Host "git checkout $($branch)"
		git checkout $branch

        Write-Host "runAsimTesters"
        & "$($repoBaseFolder)/.script/tests/asimParsersTest/runAsimTesters.ps1" -subscriptionId $subscriptionId -workspaceId $workspaceId
	}
}

run $fork $branch $subscriptionId $workspaceId
exit $global:failed
