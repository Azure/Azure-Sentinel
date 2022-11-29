Param([string]$fork, [string]$branch, [string]$repoBaseFolder)

function run([string] $fork, [string] $branch, [string] $repoBaseFolder) {
    if ([string]::IsNullOrEmpty($fork)) {
		$url = $(echo $(git config --get remote.origin.url))
		$fork = $url -replace "https://github.com/" -replace "/Azure-Sentinel.git"
    } 
	
	if ([string]::IsNullOrEmpty($branch)) {
		$branch = $(echo $(git branch --show-current))
    } 

	if ([string]::IsNullOrEmpty($repoBaseFolder)) {
		$repoBaseFolder = "$($PSScriptRoot)/.." 
    } 
	
	Set-Location $repoBaseFolder

	$filesThatWereChanged=$(echo $(git diff --name-only))
	if ($filesThatWereChanged) {
		Write-Error "Please commit your changes or stash them before run the script. "
        break
	}
  
    Write-Host "git remote add $($fork) https://github.com/$($fork)/Azure-Sentinel"
    git remote add $fork "https://github.com/$($fork)/Azure-Sentinel"

    Write-Host "git fetch $($fork)"
    $fetchOutput = git fetch $fork

    Write-Host "git checkout $($branch)"
    git checkout $branch

	git merge origin/master
	$conflicts= $(echo $(git ls-files -u))
	if ($conflicts)  {
		git merge --abort
		Write-Error "There is a merge conflict. Aborting"
		break
	}

    Write-Host "Run kqlFuncYaml2Arm"
    & "$($repoBaseFolder)/.script/kqlFuncYaml2Arm.ps1"

	$filesThatWereChanged=$(echo $(git diff --name-only))
	if ($filesThatWereChanged) {
		Write-Host "Updating ARM templates"
		Write-Host "git add ."
		git add .
		Write-Host "git commit"
		git commit -m '[ASIM Parsers] Generate deployable ARM templates from KQL function YAML files.'
	
		Write-Host "git push"
		git push
	} else {
		Write-Host "Your ARM templates are already updated"
	}



	if (![string]::IsNullOrEmpty($fork)) {
		Write-Host "git fetch origin"
		git fetch origin
	}

	if ([string]::IsNullOrEmpty($branch)) {
		Write-Host "git checkout master"
		git checkout master
    } 
}

run $fork $branch $repoBaseFolder
exit $global:failed