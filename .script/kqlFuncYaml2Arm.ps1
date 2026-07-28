$failed=0
# The KqlFuncYaml2Arm script generates deployable ARM templates from KQL function YAML files.
# Currently, the script only runs on the Schemas listed below.
$modifiedSchemas = & "$($PSScriptRoot)/getModifiedASimSchemas.ps1"
foreach($schema in $modifiedSchemas) {
	Remove-Item "$($PSScriptRoot)/../Parsers/$schema/ARM" -Recurse
	python ASIM/dev/ASimYaml2ARM/KqlFuncYaml2Arm.py -m asim -d Parsers/$schema/ARM Parsers/$schema/Parsers
}

exit $failed
