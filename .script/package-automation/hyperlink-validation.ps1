param($runId, $pullRequestNumber, $instrumentationKey, $baseFolderPath)
Write-Host "Starting execution of Hyperlink Validation"
$global:counterInvalid =0
$global:counterTimeout =0
class UrlDetail {
	[string]$filePath
    [array[]]$invalidURL
    [array[]]$timeoutURL
}

try {
	$urlDetailList = New-Object 'System.Collections.Generic.List[PSObject]'
    $baseFolderPath = $baseFolderPath + "/"
    $baseFolderPath = $baseFolderPath.replace("//", "/")

	Write-Host "====Identifying Solution Name===="
  #Get Solution Name
  . $PSScriptRoot/getSolutionName.ps1 $runId $pullRequestNumber $instrumentationKey
  #outputs: solutionName

  if ($solutionName -eq '')
  {
    exit 0
  }

  Write-Host "SolutionName is $solutionName"
  function ReadFileContent($filePath) {
    try {
        if (!(Test-Path -Path "$filePath")) {
            return $null;
        }

        $stream = New-Object System.IO.StreamReader -Arg "$filePath";
        $content = $stream.ReadToEnd();
        $stream.Close();

        if ($null -eq $content) {
            Write-Host "Error in reading file $filePath"
            return $null;
        } else {
            return $content;
        }
    }
    catch {
        Write-Host "Error occured in ReadFileContent. Error details : $_"
        return $null;
    }
}

function validateLink($urlList,$filePath)
{
	$objURlDetail = [UrlDetail]::new()
	$notWorkingUrlList
	$WorkingUrlList
	$timeoutUrlList
	$statusCode
	foreach ($url in $urlList)
	{
		try {
			
			$checkConnection = Invoke-WebRequest -Uri $url -TimeoutSec 20 -ErrorAction Stop
			if ($checkConnection.StatusCode -eq 200) {
				$WorkingUrlList+=$url 
			}
		 } 
		 catch
		 {
			$StatusCode = [int]$_.Exception.Response.StatusCode
			if($StatusCode -eq 404)
			{
				$objURlDetail.filePath=$filePath
				$objURlDetail.invalidURL+=$url
				$global:counterInvalid+=1; 
			}
			if($StatusCode -eq 500)
			{
				$objURlDetail.filePath=$filePath
				 $objURlDetail.invalidURL+=$url
				 $global:counterInvalid+=1; 
			}
			if($StatusCode -eq 0)
			{
				$objURlDetail.filePath=$filePath
				$objURlDetail.timeoutURL+=$url
				$global:counterTimeout+=1
			}
		 }
	}

	if($null -ne $objURlDetail.filePath) 
	{
		$urlDetailList.Add($objURlDetail)
	}
}
$prFiles = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
$solutionFolderPath = 'Solutions/' + $solutionName + "/"
$filesList =$prFiles| Where-Object { $_ -like "$solutionFolderPath*" }
$filteredFiles = $filesList | Where-Object {$_ -match "Solutions/"} | Where-Object {$_ -notlike "Solutions/Images/*"} | Where-Object {$_ -notlike "Solutions/*.md"} | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' } | Where-Object { $_ -notmatch ('Package') }

$finalFilteredFiles = @()
# Remove the files which does not contain url
foreach($item in $filteredFiles)
{
	$temp = Select-String -Path $item -Pattern '(http|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'-AllMatches
	if ($null -ne $temp) {
		$finalFilteredFiles += $item
	}
}

# IDENTIFY EXCLUSIONS AND IF THERE ARE NO FILES AFTER EXCLUSION THEN SKIP WORKFLOW RUN
$exclusionList = @(".py$",".png$",".jpg$",".jpeg$",".conf$", ".svg$", ".html$", ".ps1$", ".psd1$", "requirements.txt$", "host.json$", "proxies.json$", "/function.json$", ".xml$", ".zip$", ".md$")
$filterOutExclusionList = $finalFilteredFiles | Where-Object { $_ -notmatch ($exclusionList -join '|')  }

$exclusionDomainList = @("&&sudo","schema.management","schemas.microsoft","twitter.com")

foreach ($currentFile in $filterOutExclusionList)
{
  $urlList = @()
		$fileContent = ReadFileContent -filePath $currentfile
        $list = $fileContent | Select-String -Pattern '(http|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?' -AllMatches 
        $urlList += $list.Matches.Value
		$urlList = $urlList | Select-Object -Unique
		$filterOutExclusionUrlList = $urlList | Where-Object { $_ -notmatch ($exclusionDomainList -join '|')  }
		If ($null -ne $filterOutExclusionUrlList) {
		validateLink $filterOutExclusionUrlList $currentFile
		}
}

if($global:counterInvalid -gt 0 -or $global:counterTimeout -gt 0)
{
	Write-Host "Below list of files for which urls are invalid or timeout. Please verify urls:"
	
	foreach($timeouturl in $urlDetailList)
	{
		Write-Host "File Path:" $timeouturl.FilePath
		
		if($timeouturl.timeoutURL.Count -gt 0)
		{
			foreach($timeout in $timeouturl.timeoutURL)
			{
				Write-Host  $timeout ": Timeout(Warning)" -ForegroundColor Yellow
			}
		}
		if($timeouturl.invalidURL.Count -gt 0)
		{
			foreach($invalid in $timeouturl.invalidURL)
			{
				Write-Host  $invalid  ": Invalid URL" -ForegroundColor Red
			}
		}
		Write-Host "`n"
	}
}
if($global:counterInvalid -gt 0)
{
	exit 1
}
} catch {
  Write-Host "Error Occured in Hyperlink Validation file!. Error Details: $_"
  exit 1
}