param($runId, $pullRequestNumber, $instrumentationKey, $baseFolderPath, $SolutionPath)
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
    $contentRoot = if ($baseFolderPath) {
      [System.IO.Path]::GetFullPath($baseFolderPath)
    } else {
      [System.IO.Path]::GetFullPath((Get-Location).Path)
    }

  function Test-PrivateSolutionContentPath([string]$filePath) {
    $segments = $filePath -split '[\\/]'
    if ($segments.Count -lt 3 -or -not $segments[0].Equals("Solutions", [System.StringComparison]::OrdinalIgnoreCase)) {
      return $false
    }
    foreach ($segment in $segments | Select-Object -Skip 2) {
      if ($segment.Equals("Logs", [System.StringComparison]::OrdinalIgnoreCase) -or
          $segment.Equals("Reports", [System.StringComparison]::OrdinalIgnoreCase) -or
          $segment.Equals("Evidence", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
      }
    }
    return $false
  }

  if ($SolutionPath) {
    $solutionsRoot = [System.IO.Path]::GetFullPath((Join-Path $contentRoot "Solutions")).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $resolvedSolutionPath = [System.IO.Path]::GetFullPath($SolutionPath)
    if ([System.IO.Path]::GetDirectoryName($resolvedSolutionPath) -ne $solutionsRoot -or
        -not (Test-Path $resolvedSolutionPath -PathType Container) -or
        ((Get-Item $resolvedSolutionPath).Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
      throw "Invalid solution folder '$SolutionPath'. Expected an existing direct child of '$solutionsRoot'."
    }
    $filesList = @(Get-ChildItem $resolvedSolutionPath -Recurse -File |
      ForEach-Object { [System.IO.Path]::GetRelativePath($contentRoot, $_.FullName).Replace('\', '/') } |
      Where-Object {
        $_ -notlike 'Solutions/Images/*' -and
        $_ -notlike 'Solutions/*.md' -and
        $_ -notlike '*/Package/*' -and
        $_ -notlike '*system_generated_metadata.json' -and
        $_ -notlike '*testParameters.json'
      })
    Write-Host "Hyperlink validation scoped to current files under $resolvedSolutionPath"
  }
  else {
    Write-Host "====Identifying Solution Name===="
    # Preserve CI's commit-diff based solution discovery when no folder scope is supplied.
    . $PSScriptRoot/getSolutionName.ps1 $runId $pullRequestNumber $instrumentationKey
    if ($solutionName -eq '') {
      exit 0
    }
    Write-Host "SolutionName is $solutionName"
    $prFiles = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
    $solutionFolderPath = 'Solutions/' + $solutionName + "/"
    $filesList = $prFiles | Where-Object { $_ -like "$solutionFolderPath*" }
  }
  $filesList = @($filesList | Where-Object { -not (Test-PrivateSolutionContentPath $_) })
  function Resolve-ContentFilePath($filePath) {
    $resolvedPath = if ([System.IO.Path]::IsPathRooted($filePath)) {
      [System.IO.Path]::GetFullPath($filePath)
    } else {
      [System.IO.Path]::GetFullPath((Join-Path $contentRoot $filePath))
    }
    $relativePath = [System.IO.Path]::GetRelativePath($contentRoot, $resolvedPath)
    if ($relativePath -eq ".." -or $relativePath.StartsWith(".." + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::Ordinal)) {
      throw "Content file path escapes the selected content root: '$filePath'."
    }
    if (-not (Test-Path -LiteralPath $resolvedPath -PathType Leaf)) {
      throw "Content file does not exist under the selected content root: '$resolvedPath'."
    }
    return $resolvedPath
  }
  function ReadFileContent($filePath) {
    $resolvedPath = Resolve-ContentFilePath $filePath
    return [System.IO.File]::ReadAllText($resolvedPath)
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
$filteredFiles = $filesList | Where-Object {$_ -match "Solutions/"} | Where-Object {$_ -notlike "Solutions/Images/*"} | Where-Object {$_ -notlike "Solutions/*.md"} | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' } | Where-Object { $_ -notmatch ('Package') }

$finalFilteredFiles = @()
# Remove the files which does not contain url
foreach($item in $filteredFiles)
{
	$resolvedItem = Resolve-ContentFilePath $item
	$temp = Select-String -LiteralPath $resolvedItem -Pattern '(http|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'-AllMatches -ErrorAction Stop
	if ($null -ne $temp) {
		$finalFilteredFiles += $item
	}
}

# IDENTIFY EXCLUSIONS AND IF THERE ARE NO FILES AFTER EXCLUSION THEN SKIP WORKFLOW RUN
$exclusionList = @(".py$",".png$",".jpg$",".jpeg$",".conf$", ".svg$", ".html$", ".ps1$", ".psd1$", "requirements.txt$", "host.json$", "proxies.json$", "/function.json$", ".xml$", ".zip$", ".md$")
$filterOutExclusionList = $finalFilteredFiles | Where-Object { $_ -notmatch ($exclusionList -join '|')  }

$exclusionDomainList = @("&&sudo","schema.management","schemas.microsoft","twitter.com", "s-platform.api.opendns.com", "github.com", "azure.microsoft.com", "sts.windows.net", "oauth2.googleapis.com", "monitoring.googleapis.com","api2.eu.prismacloud.io","api.lookout.com","accounts.google.com","crowdstrike.com")

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
  Write-Host "Error Occurred in Hyperlink Validation file!. Error Details: $_"
  exit 1
}