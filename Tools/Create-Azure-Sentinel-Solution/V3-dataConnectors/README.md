<h2>Create Solution template for data Connectors</h2></br>

Please go over the following steps to generate a solution template:
- Add under "input" directory the relevant ARM resources files (dataConnectorDefinition, DataConnectors, DCR, tables).
- Update input/solutionMetadata.json file properties values according to your solution.
- Update the dataConnectors resources (under "input" directory) to use the connector definition parameters. </br>
For Example: 
   - the ConnectorDefinition has 'organization' input text
   - the "request.apiEndpoint" property value in the connection(data connector) can use this parameter </br>
   "[[concat('https://api.meraki.com/api/v1/organizations/',parameters('organization'),'/networks']" </br>
   Note: the string with a parameter reference start with double '[' and end with one ']', this is due to template spec syntax for using parameters in nestead template
- Execute the createSolutionV3.ps script, the script will generate a new file "mainTemplate.json" for the template.