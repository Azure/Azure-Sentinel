function run() {
	$repoBaseFolder = "$($PSScriptRoot)/../../.."
	Set-Location $repoBaseFolder

	$filesThatWereChanged=$(echo $(git diff --name-only))
	if ($filesThatWereChanged) {
		Write-Error "Please commit your changes or stash them before run the script. "
        break
	}

	git fetch
	git merge origin/master
	$conflicts= $(echo $(git ls-files -u))
	if ($conflicts)  {
		git merge --abort
		Write-Error "There is a merge conflict. Please fix it and run the script again. Aborting"
		break
	}

    Write-Host "Run kqlFuncYaml2Arm"
    & "$($repoBaseFolder)/.script/utils/kqlFuncYaml2Arm/kqlFuncYaml2Arm.ps1"

	$filesThatWereChanged=$(echo $(git diff --name-only))
	if ($filesThatWereChanged) {
		Write-Host "Updating ARM templates.."
		Write-Host "git add ."
		git add .
		Write-Host "git commit"
		git commit -m '[ASIM Parsers] Generate deployable ARM templates from KQL function YAML files.'
	
		Write-Host "git push"
		Write-Host "Your ARM templates were updated"
		git push
	} else {
		Write-Host "Your ARM templates are already updated"
	}
}

run
exit $global:failed