# ASIM Parser Skills

Copilot skills for creating, validating, deploying, and packaging ASIM parsers locally.

## Prerequisites

- VS Code with GitHub Copilot Chat (agent mode)
- Azure CLI installed and signed in (`az login`)
- Git configured with push access to Azure-Sentinel
- Clone of this repository

## Quick start (VS Code)

1. Verify your environment:
   ```powershell
   az account show
   git remote -v
   ```
2. Prompt Copilot:
   > Use the `asim-parser-creator-orchestrator` skill to create a new ASIM parser.
3. Provide when asked: source documentation URL, source table name, Log Analytics workspace ID, target ASIM schema.

## Quick start (GitHub Copilot CLI)

1. Install the GitHub CLI Copilot extension if you haven't already:
   ```powershell
   npm install -g @github/copilot
   ```

   For other installation instructions, refer to [official documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli).
2. Clone the repo and navigate to the skills folder:
   ```powershell
   git clone https://github.com/Azure/Azure-Sentinel.git
   cd Azure-Sentinel
   ```
3. Start an interactive Copilot session on Powershell:
   ```powershell
   copilot
   ```
4. Load the relevant ASIM skills (or any individual skill) with `/skills`:
   ```
   /skills add ASIM/skills/
   ```
5. Prompt Copilot within the session:
   ```
   Create a new ASIM parser for my source table.
   ```

## Skills

| Skill | Purpose | Azure required? |
|---|---|---|
| `asim-parser-creator-orchestrator` | End-to-end parser creation workflow | Yes |
| `asim-parser-user-prompter` | Gather and validate user inputs | Yes (workspace check) |
| `asim-parser-create-parser` | Generate parameter-less parser (`ASim*.kql`) | Yes (data sampling) |
| `asim-parser-create-parameter-parser` | Generate parameterized parser (`vim*.kql`) | No (file only) |
| `asim-parser-validator` | Run schema and data validation | Yes |
| `asim-parser-la-deployer` | Deploy parsers to Log Analytics | Yes |
| `asim-parser-github-pr-packager` | Package parsers into a PR | No |
| `log-analytics-workspace-queryer` | Run KQL queries against workspace | Yes |

## Outputs

- `ASim<Schema><Vendor><Product>.kql` — parameter-less parser
- `vim<Schema><Vendor><Product>.kql` — parameterized parser
- YAML definitions, changelogs, and ARM templates (during PR packaging or deployment)

## Troubleshooting

| Problem | Fix |
|---|---|
| `az account show` fails | Run `az login` |
| Workspace not found | Confirm workspace ID exists in your Azure subscription |
| ARM deployment escaping errors | Re-escape `\`, `"`, newlines, and tabs in embedded KQL |
| Validation errors persist after 5 cycles | Verify schema selection and field mappings manually |
| Git push rejected | Check remote permissions and rebase on target branch |
| Query returns no rows after deploy | Confirm source table has data and `disabled` defaults to `false` |

## Security notes

- Never paste tokens, passwords, or keys into Copilot Chat — enter secrets directly in the terminal.
- Prefer anonymized or redacted log samples over production data.
- Remove temporary ARM templates containing embedded queries after deployment.

## Limitations

- Schema auto-selection can be ambiguous when source logs span multiple schemas.
- Validation and deployment steps require Azure connectivity; only file authoring works offline.
- These skills accelerate authoring but do not replace security review or production governance.
