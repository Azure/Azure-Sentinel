$DownloadCenterURL = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
$Response = Invoke-WebRequest -URI $DownloadCenterURL
$DownloadLink = $Response.Links |  where {$_.href.Contains("/ServiceTags_Public")} | select href
$DownloadURL = [System.Uri]$DownloadLink[0].href
$jsonFileData = Invoke-WebRequest -Method Get -URI $DownloadURL | ConvertFrom-Json
$jsonContent = $jsonFileData | ConvertTo-Json -depth 100
$jsonFileData | ConvertTo-Json -depth 100 | Out-File ".\servicetags.json"
write-host "File Fetch completed."

#decleration
$file = ".\servicetags.json"
$text = $jsonFileData 
$wi = "#13 #14"

"Set config"
git config --global user.email "builduser@samik.local" # any values will do, if missing commit will fail
git config --global user.name "Build user"

"Select a branch"
git checkout main 2>&1 | write-host # need the stderr redirect as some git command line send none error output here

"Update the local repo"
git pull  2>&1 | write-host

"Status at start"
git status 2>&1 | write-host

"Update the file $file"
Add-Content -Path $file -Value $jsonContent 

"Status prior to stage"
git status 2>&1 | write-host

"Stage the file"
git add $file  2>&1 | write-host

"Status prior to commit"
git status 2>&1 | write-host

"Commit the file"
git commit -m "Automated Repo Update"  2>&1 | write-host

"Status prior to push"
git status 2>&1 | write-host

"Push the change"
git push  2>&1 | write-host
