
[CmdletBinding()]
param (
    [Parameter(Mandatory, ValueFromPipeline)]
    [ValidateScript(
        {
            (Test-Path -Path $_) -and ($_.Extension -in '.csv')
        }
    )]
    [System.IO.FileInfo]$FilesPath
)

$requiredColumns = @(
    'ColumnName',
    'ColumnType',
    'Class',
    'Schema',
    'LogicalType',
    'ListOfValues',
    'Aliased'
)

$csv = Get-ChildItem -Path $FilesPath | Import-Csv -Delimiter ','
$columns = (($csv | Select-Object -First 1).PSObject.Members | Where-Object MemberType -eq 'NoteProperty').name

if (-not(Compare-Object -ReferenceObject $requiredColumns -DifferenceObject $columns)) {
    Write-Debug "The file '$($FilesPath.FullName)' is valid"
}
else {
    Write-Warning "The file '$($FilesPath.BaseName)' is not valid"
    break
}

$schemas = $csv | Select-Object -ExpandProperty Schema -Unique
$duplicateColumns = @()

foreach ($schema in $schemas) {
    Write-Debug "Processing ASIM schema '$($schema)'"
    $schemaArray = ($csv | Where-Object schema -eq $schema)

    foreach ($item in $schemaArray) {
        $count = ($schemaArray | Where-Object ColumnName -eq $item.ColumnName).count
        if ($count -gt 1) {
            Write-Debug "Found duplicate column '$($item.ColumnName)' in schema '$($schema)'"
            $duplicateColumns += $item
        }
    }
}

if ($duplicateColumns.count -gt 0) {
    Write-Warning "Duplicate entries found for the following fields`n"
} else {
    Write-Output "`nNo duplicate entries found`n"
}
return $duplicateColumns | Sort-Object Schema, ColumnName, Class -Unique
