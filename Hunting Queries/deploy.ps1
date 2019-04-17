# Use this script to convert the DeployedQueries.txt file with list of queries IDs
# to DeployedQueries.json which is consumed by Sentinel Portal

$QueriesInputFilePath = "DeployedQueries.txt"
$QueriesOutputFilePath = "DeployedQueries.json"

Write-Host -ForegroundColor Cyan "Reading $QueriesInputFilePath"
$reader = new-object System.IO.StreamReader("$PSScriptRoot\\$QueriesInputFilePath")

$deployedIDs = @()
$queries = @{}
while($null -ne ($line = $reader.ReadLine()))
{
    $id = $line.Substring(0,36).ToLower()
    $deployedIDs += $id
}
$reader.Close()

$pathLength = ${pwd}.Path.Length+1
$queriesFiles = Get-ChildItem -Filter *.txt -Recurse | Select-Object -ExpandProperty FullName
$queriesFiles += Get-ChildItem -Path '../Detections' -Filter *.txt -Recurse | Select-Object -ExpandProperty FullName

$env:TZ="UTC"
foreach ($query in $queriesFiles) {
    if ($query -like "*Detections*") {
        $shortName = "..\" + $query.Substring($pathLength-16)
    } else {
        $shortName = $query.Substring($pathLength)
    }
    Write-Host -NoNewline "    Processing ${shortName} ... "
    $content = [System.IO.File]::ReadAllText($query)
    if ($content -imatch "Id: ([a-z0-9-]+)")
    {
        $id = $matches[1]
        $name = ""
        $description = ""
        $tactics = @()
        $queryText = ($content.Split([Environment]::NewLine, [System.StringSplitOptions]::RemoveEmptyEntries) | Where-Object { $_ -notmatch "^\/\/" }) -join "`n"
        $createdTimeUtc = (git log --format=%aI ''$query'')[-1]

        if ($content -match "(?m)Name: (.*)\r\n") {
            $name = $matches[1]
        }
        if ($content -match "(?sm)Description: (.*?)\/\/\r\n") {
            $description = $matches[1]  -replace '(?m)^//', '' -replace '[\r\n]', ''
        }
        if ($content -match "(?m)Tactics: (.*)\r\n") {
            $tactics = @(($matches[1].split(',#', [System.StringSplitOptions]::RemoveEmptyEntries).Trim() | Where-Object {$_}).Replace(' ', ''))
        }
        
        $queries[$id] = @{
            id = $id;
            name = $name;
            description = $description;
            tactics = $tactics;
            query = $queryText;
            createdTimeUtc = $createdTimeUtc;
        }
        Write-Host $id $name
    }
    else
    {
        Write-Host "Skip"
    }

}

$allQueries = @()
foreach ($id in $deployedIDs) {
    Write-Host -NoNewline -ForegroundColor Magenta "    Processing $id ... "
    $query = $queries[$id]
    if ($query)
    {
        $allQueries += $query
        Write-Host -ForegroundColor Green $query.name
    }
    else
    {
        Write-Host -ForegroundColor Red  "Not found"
    }
}

Write-Host -ForegroundColor Cyan "Saving: $QueriesOutputFilePath"
$allQueries | ConvertTo-Json | Out-File $QueriesOutputFilePath -Encoding utf8

Write-Host -ForegroundColor Green "Done"