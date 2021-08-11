# ASIM Yaml to ARM template converter

Use this tool to convert an ASIM parser YAML template to an ARM template that can easily be deployed.

To use:

`python ASimYaml2ARM.py -p <full path to YAML file>`

Notes:
- The template is generated in the same folder as the original YAML file. 
- `Template.json` has to be in the same folder as the script. 
- Only the YAML `ParserName` and `ParserQuery` fields are important for the generated template. The `Title` is also used as part of the template but is information only. 
