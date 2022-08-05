$failed=0
# The KqlFuncYaml2Arm script generates deployable ARM templates from KQL function YAML files.
# Currently, the script only runs on the Schemas listed below.
python ASIM/dev/ASimYaml2ARM/KqlFuncYaml2Arm.py -m asim -d Parsers/f000/ARM Parsers/f000/Parsers

exit $failed
