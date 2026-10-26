---
name: az-cli-command-runner
description: Runs Azure CLI commands in a terminal. Use this skill when you need to execute az CLI commands such as checking authentication, querying Log Analytics, managing deployments, or inspecting Azure resources.
---

# Run Azure CLI Commands

Execute the PowerShell script at `scripts/runAzCommand.ps1` (relative to this skill's directory) by passing the az CLI command as a parameter:

```
.\scripts\runAzCommand.ps1 -Command "<az command>"
```

The script validates the command against allowed prefixes and safety restrictions before executing it. If validation fails, the script exits with an error message.

If the command returns an authentication error, ask the user to run `az login` before continuing.
