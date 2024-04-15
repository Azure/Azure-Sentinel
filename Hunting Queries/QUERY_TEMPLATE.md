# Hunting Query Template

### Use a short name:
				// Name: <Short Name for the query>

### Add a GUID so that we can add to the UI:
				// Id: <GUID>

### A good description of what the query does, inputs and outputs:
				// Description:  <Full description>
				
### The datasource for the query (examples):
				// DataSource: #SecurityEvent, #Syslog

### The MITRE ATT&CK Techniques that apply to the query (examples):
				// Tactics: #InitialAccess, #Execution, #Persistance
								
### Example Query:
				// Name: Cscript script daily summary breakdown
				//
				// Id: 36abe031-962d-482e-8e1e-a556ed99d5a3
				//
				// Description:  breakdown of scripts running in the environment
				//
				// DataSource: #SecurityEvent
				//
				// Tactics: #Execution
				//
				let ProcessCreationEvents=() {
				let processEvents=SecurityEvent
				| where EventID==4688
				| project EventTime=TimeGenerated, ComputerName=Computer,AccountName=SubjectUserName, AccountDomain=SubjectDomainName,
				FileName=tostring(split(NewProcessName, '\\')[-1]),
				ProcessCommandLine = CommandLine, 
				InitiatingProcessFileName=ParentProcessName,InitiatingProcessCommandLine="",InitiatingProcessParentFileName="";
				processEvents;
				};
				// Daily summary of cscript activity - extracting script name and parameters from commandline:
				ProcessCreationEvents | where FileName =~ "cscript.exe"
				| project removeSwitches = replace(@"/+[a-zA-Z0-9:]+", "", ProcessCommandLine) // remove commandline switches
				| project CommandLine = trim(@"[a-zA-Z0-9\\:""]*cscript(.exe)?("")?(\s)+", removeSwitches) // remove the leading cscript.exe process name 
				// extract the script name: 
				| project ScriptName= iff(CommandLine startswith @"""", 
				                       extract(@"([:\\a-zA-Z_\-\s0-9\.()]+)(""?)", 0, CommandLine), // handle case where script name is enclosed in " characters
				                       extract(@"([:\\a-zA-Z_\-0-9\.()]+)(""?)", 0, CommandLine))   // handle case where script name is not enclosed in quotes                    
				                       , CommandLine 
				| project ScriptName=trim(@"""", ScriptName) , ScriptNameLength=strlen(ScriptName), CommandLine 
				// extract remainder of commandline as script parameters: 
				| project ScriptName, ScriptParams = iff(ScriptNameLength < strlen(CommandLine), substring(CommandLine, ScriptNameLength +1), "")
				| summarize by ScriptName, ScriptParams 