const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    const agent = vscode.chat.createChatParticipant('sentinel-data-connector-agent-builder.builder', handleChat);
    agent.iconPath = vscode.Uri.joinPath(context.extensionUri, 'media', 'icon.png');

    context.subscriptions.push(agent);
}

/**
 * @param {vscode.ChatRequest} request
 * @param {vscode.ChatContext} context
 * @param {vscode.ChatResponseStream} stream
 * @param {vscode.CancellationToken} token
 */
async function handleChat(request, context, stream, token) {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';

    // Load knowledge files for context
    const knowledgeDir = path.join(workspaceRoot, 'knowledge');
    const instructions = loadFile(path.join(workspaceRoot, '.github', 'copilot-instructions.md'));

    // Determine which phase/command is being invoked
    const command = request.command || detectPhase(request.prompt);

    // Load relevant knowledge for the phase
    let knowledgeContext = '';
    // Map each command to one or more knowledge files. Order matters — files are
    // concatenated in listed order so the primary reference appears first.
    const knowledgeMap = {
        'ideate': ['use-case-frameworks.md'],
        'onboard': ['data-lake-onboarding-guide.md'],
        'ingest': ['data-ingestion-guide.md'],
        'mcp': ['mcp-verification-guide.md'],
        'build': ['security-copilot-agent-guide.md', 'agent-authoring-guide.md'],
        'publish': ['publishing-guide.md']
    };

    if (command && knowledgeMap[command]) {
        knowledgeContext = knowledgeMap[command]
            .map(fname => loadFile(path.join(knowledgeDir, fname)))
            .filter(Boolean)
            .join('\n\n---\n\n');
    }

    // Data lake validation gate: when entering ingest phase, also load onboarding guide
    // so the agent knows how to validate and troubleshoot data lake status.
    // IMPORTANT: do NOT detect onboarding via msg-resources-<guid> RG or a single-RG
    // SentinelPlatformServices scan — those signals persist after offboarding/when
    // the linked workspace is stale. Use the combined-signal validator instead.
    if (command === 'ingest') {
        const onboardingKnowledge = loadFile(path.join(knowledgeDir, 'data-lake-onboarding-guide.md'));
        knowledgeContext += '\n\n## DATA LAKE VALIDATION (Pre-Ingestion Gate)\n\n';
        knowledgeContext += 'BEFORE providing data ingestion guidance, you MUST ask the user to validate ';
        knowledgeContext += 'their data lake status by running the combined-signal validator:\n';
        knowledgeContext += '```powershell\n./scripts/Validate-DataLake.ps1\n```\n';
        knowledgeContext += 'The validator runs a tenant-wide Azure Resource Graph scan for the Sentinel ';
        knowledgeContext += 'platform resource AND verifies at least one workspace has ';
        knowledgeContext += '`Microsoft.SecurityInsights/onboardingStates/default` (api-version 2025-09-01). ';
        knowledgeContext += 'It classifies the tenant as one of:\n';
        knowledgeContext += '- **Onboarded** (exit 0) — proceed with the existing primary workspace, or surface Issue #1 if the user wants a new one.\n';
        knowledgeContext += '- **Stale** (exit 2) — platform resource exists but no live Sentinel workspace; surface Issue #3 and guide cleanup.\n';
        knowledgeContext += '- **NotOnboarded** (exit 1) — re-run with `-Remediate` to pick an existing Sentinel workspace or auto-create one (RG + LAW + Sentinel enablement), then walk the user through the Defender portal data-lake setup.\n';
        knowledgeContext += 'Do NOT use `az resource list --resource-group msg-resources-<guid> ...` as a check — that resource persists after offboarding and is not authoritative.\n';
        knowledgeContext += 'If data lake is NOT active, do NOT proceed with ingestion. Guide user through data lake setup using the onboarding guide below.\n\n';
        knowledgeContext += onboardingKnowledge;
    }

    // Build the system prompt with agent instructions + relevant knowledge
    const systemPrompt = buildPrompt(instructions, knowledgeContext, command);

    // Use Copilot's language model to generate response
    const messages = [
        vscode.LanguageModelChatMessage.User(systemPrompt),
        ...context.history.map(h => {
            if (h instanceof vscode.ChatResponseTurn) {
                return vscode.LanguageModelChatMessage.Assistant(
                    h.response.map(r => r.value?.value || r.value || '').join('')
                );
            }
            return vscode.LanguageModelChatMessage.User(h.prompt);
        }),
        vscode.LanguageModelChatMessage.User(request.prompt)
    ];

    try {
        const models = await vscode.lm.selectChatModels({ family: 'gpt-4o' });
        if (models.length === 0) {
            stream.markdown('⚠️ No language model available. Please ensure GitHub Copilot is active.');
            return;
        }

        const response = await models[0].sendRequest(messages, {}, token);

        for await (const chunk of response.text) {
            stream.markdown(chunk);
        }
    } catch (err) {
        if (err.code === 'NoPermissions') {
            stream.markdown('⚠️ This agent requires GitHub Copilot Chat access. Please sign in.');
        } else {
            stream.markdown(`❌ Error: ${err.message}`);
        }
    }
}

/**
 * Detect which phase the user prompt maps to
 */
function detectPhase(prompt) {
    const lower = prompt.toLowerCase();
    if (/ideate|use case|get started|what can i build|brainstorm/.test(lower)) return 'ideate';
    if (/onboard|workspace|data lake|set up|log analytics/.test(lower)) return 'onboard';
    if (/ingest|data|custom table|kql import|connector/.test(lower)) return 'ingest';
    if (/mcp|verify|schema|search_tables|query_lake/.test(lower)) return 'mcp';
    if (/build|instruction|agent|test|security copilot/.test(lower)) return 'build';
    if (/publish|package|store|partner center|offer/.test(lower)) return 'publish';
    return null;
}

/**
 * Build the full system prompt with context
 */
function buildPrompt(instructions, knowledge, command) {
    let prompt = `You are the Sentinel Data Connector and Agent Builder. Follow these instructions:\n\n${instructions}\n\n`;

    if (knowledge) {
        prompt += `## Relevant Knowledge for this phase:\n\n${knowledge}\n\n`;
    }

    if (command) {
        prompt += `The user is in the "${command}" phase. Focus your guidance accordingly.\n`;
    }

    prompt += `\nIMPORTANT: Be interactive. Ask clarifying questions. Automate with az cli where possible. Validate completion of manual steps via API calls.\n`;

    return prompt;
}

/**
 * Safely load a file, returning empty string if not found
 */
function loadFile(filePath) {
    try {
        return fs.readFileSync(filePath, 'utf-8');
    } catch {
        return '';
    }
}

function deactivate() {}

module.exports = { activate, deactivate };
