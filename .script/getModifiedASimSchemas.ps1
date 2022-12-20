function getModifiedAsimSchemas() {
    $schemas = ("ASimDns", "ASimWebSession", "ASimNetworkSession", "ASimProcessEvent")
    $midifiedSchemas = @()
    foreach ($schema in $schemas) {
        $filesThatWereChanged= Invoke-Expression "git diff origin/master  --name-only -- $($PSScriptRoot)/../Parsers/$($schema)/Parsers"
        if ($filesThatWereChanged) {
            Write-Host Files that were changed under Azure-Sentinel/Parsers/$schema/ARM:
			Write-Host  - $filesThatWereChanged
            Write-Host modified schema $schema
            $midifiedSchemas += $schema
        }
        else {
            Write-Host "No files were changed under Azure-Sentinel/Parsers/$schema/"
        }
    }

    Write-Host The modified schemas are- $midifiedSchemas
    return $midifiedSchemas
}

getModifiedAsimSchemas