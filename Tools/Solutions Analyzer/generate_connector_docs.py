"""
Generate Microsoft Learn-style connector documentation from CSV.

Creates markdown documentation organized by solution, mimicking the structure
of https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set
import argparse
from urllib.parse import quote
import json
import re


def sanitize_anchor(text: str) -> str:
    """Convert text to URL-safe anchor."""
    return text.lower().replace(" ", "-").replace("/", "-").replace("_", "-")


def format_instruction_steps(instruction_steps: str) -> str:
    """
    Parse and format instruction steps from CSV field.
    
    The instruction_steps field contains escaped JSON representing the instructionSteps array.
    This function parses the JSON and formats it as markdown.
    """
    if not instruction_steps:
        return ""
    
    try:
        # Parse the JSON string
        steps_data = json.loads(instruction_steps)
    except (json.JSONDecodeError, TypeError):
        # Fallback for old format (already formatted string with <br> tags)
        formatted = instruction_steps.replace('<br>', '\n')
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)
        formatted = re.sub(r'/\*\s*Lines\s+\d+-\d+\s+omitted\s*\*/', '', formatted)
        return formatted.strip()
    
    # Format the instruction steps recursively
    return _format_instruction_steps_recursive(steps_data, indent_level=0)


def _format_data_connectors_grid(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format DataConnectorsGrid instruction type with clear explanation."""
    mapping = parameters.get("mapping", [])
    menu_items = parameters.get("menuItems", [])
    
    lines = [
        f"{indent}**Connector Management Interface**\n\n",
        f"{indent}This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.\n\n"
    ]
    
    if mapping:
        lines.append(f"{indent}📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:\n")
        for col in mapping:
            col_name = col.get("columnName", "")
            if col_name:
                lines.append(f"{indent}- **{col_name}**\n")
        lines.append("\n")
    
    lines.append(f"{indent}➕ **Add New Collector**: Click the \"Add new collector\" button to configure a new data collector (see configuration form below).\n\n")
    
    if "DeleteConnector" in menu_items or "EditConnector" in menu_items:
        lines.append(f"{indent}🔧 **Manage Collectors**: Use the actions menu to delete or modify existing collectors.\n\n")
    
    lines.append(f"{indent}> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.\n\n")
    
    return "".join(lines)


def _format_context_pane(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format ContextPane instruction type with detailed form field explanation."""
    title = parameters.get("title", "Configuration Form")
    subtitle = parameters.get("subtitle", "")
    label = parameters.get("label", "Add new collector")
    instruction_steps = parameters.get("instructionSteps", [])
    
    lines = [
        f"{indent}**{title}**\n\n",
    ]
    
    if subtitle:
        lines.append(f"{indent}*{subtitle}*\n\n")
    
    lines.append(f"{indent}When you click the \"{label}\" button in the portal, a configuration form will open. You'll need to provide:\n\n")
    
    # Process instruction steps to show what fields are required
    if instruction_steps:
        for step in instruction_steps:
            step_title = step.get("title", "")
            step_instructions = step.get("instructions", [])
            
            if step_title:
                lines.append(f"{indent}*{step_title}*\n\n")
            
            for instruction in step_instructions:
                if not isinstance(instruction, dict):
                    continue
                
                instr_type = instruction.get("type", "")
                params = instruction.get("parameters", {})
                
                if instr_type == "Textbox":
                    label_text = params.get("label", "")
                    placeholder = params.get("placeholder", "")
                    required = params.get("validations", {}).get("required", False)
                    req_marker = " (required)" if required else " (optional)"
                    
                    if label_text:
                        lines.append(f"{indent}- **{label_text}**{req_marker}")
                        if placeholder:
                            lines.append(f": {placeholder}")
                        lines.append("\n")
                
                elif instr_type == "Dropdown":
                    label_text = params.get("label", "")
                    options = params.get("options", [])
                    required = params.get("required", False)
                    req_marker = " (required)" if required else " (optional)"
                    
                    if label_text:
                        lines.append(f"{indent}- **{label_text}**{req_marker}: Select from available options\n")
                        if options:
                            for opt in options[:5]:  # Show first 5 options
                                opt_text = opt.get('text', opt.get('key', ''))
                                if opt_text:
                                    lines.append(f"{indent}  - {opt_text}\n")
                            if len(options) > 5:
                                lines.append(f"{indent}  - ... and {len(options) - 5} more options\n")
                
                elif instr_type == "Markdown":
                    content = params.get("content", "")
                    if content:
                        lines.append(f"{indent}{content}\n\n")
        
        lines.append("\n")
    
    lines.append(f"{indent}> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.\n\n")
    
    return "".join(lines)


def _format_gcp_grid(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format GCPGrid instruction type."""
    lines = [
        f"{indent}**GCP Collector Management**\n\n",
        f"{indent}📊 **View GCP Collectors**: A management interface displays your configured Google Cloud Platform data collectors.\n\n",
        f"{indent}➕ **Add New Collector**: Click \"Add new collector\" to configure a new GCP data connection.\n\n",
        f"{indent}> 💡 **Portal-Only Feature**: This configuration interface is only available in the Microsoft Sentinel portal.\n\n"
    ]
    return "".join(lines)


def _format_gcp_context_pane(parameters: Dict[str, Any], indent: str = "") -> str:
    """Format GCPContextPane instruction type."""
    lines = [
        f"{indent}**GCP Connection Configuration**\n\n",
        f"{indent}When you click \"Add new collector\" in the portal, you'll be prompted to provide:\n",
        f"{indent}- **Project ID**: Your Google Cloud Platform project ID\n",
        f"{indent}- **Service Account**: GCP service account credentials with appropriate permissions\n",
        f"{indent}- **Subscription**: The Pub/Sub subscription to monitor for log data\n\n",
        f"{indent}> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.\n\n"
    ]
    return "".join(lines)


def _format_data_type_selector(instr_type: str, parameters: Dict[str, Any], indent: str = "") -> str:
    """Format data type selector instruction types (AADDataTypes, MCasDataTypes, OfficeDataTypes)."""
    data_types = parameters.get("dataTypes", [])
    
    type_names = {
        "AADDataTypes": "Microsoft Entra ID",
        "MCasDataTypes": "Microsoft Defender for Cloud Apps",
        "OfficeDataTypes": "Microsoft 365"
    }
    
    type_name = type_names.get(instr_type, "Data")
    
    lines = [
        f"{indent}**Select {type_name} Data Types**\n\n",
        f"{indent}In the Microsoft Sentinel portal, select which data types to enable:\n\n"
    ]
    
    if data_types:
        for dt in data_types:
            if isinstance(dt, dict):
                dt_name = dt.get("name", "")
                dt_title = dt.get("title", dt_name)
                if dt_title:
                    lines.append(f"{indent}- ☐ **{dt_title}**\n")
                    
                    # Add info box if available
                    info_html = dt.get("infoBoxHtmlTemplate", "")
                    if info_html and len(info_html) < 200:
                        # Strip HTML tags for simple display
                        info_text = re.sub(r'<[^>]+>', '', info_html).strip()
                        if info_text:
                            lines.append(f"{indent}  *{info_text}*\n")
        lines.append("\n")
    
    lines.append(f"{indent}Each data type may have specific licensing requirements. Review the information provided for each type in the portal before enabling.\n\n")
    lines.append(f"{indent}> 💡 **Portal-Only Feature**: Data type selection is only available in the Microsoft Sentinel portal.\n\n")
    
    return "".join(lines)


def _format_instruction_steps_recursive(instruction_steps: Any, indent_level: int = 0) -> str:
    """
    Recursively format instructionSteps array to markdown.
    
    Args:
        instruction_steps: List of instruction step objects
        indent_level: Current nesting level for indentation (0 = top level)
    
    Returns:
        Formatted markdown string
    """
    if not isinstance(instruction_steps, list):
        return ""
    
    lines = []
    step_num = 0
    indent = "  " * indent_level  # 2 spaces per level
    
    for step in instruction_steps:
        if not isinstance(step, dict):
            continue
        
        title = step.get("title", "") or ""
        description = step.get("description", "") or ""
        title = title.strip() if isinstance(title, str) else ""
        description = description.strip() if isinstance(description, str) else ""
        instructions = step.get("instructions", [])
        inner_steps = step.get("innerSteps", [])
        
        # Skip empty steps unless they have instructions or innerSteps
        if not title and not description and not instructions and not inner_steps:
            continue
        
        # Check if title already starts with a number (to avoid duplicate numbering)
        title_has_number = bool(title and re.match(r'^\d+\.', title))
        
        # Only increment step number if there's substantial content and title doesn't already have a number
        if (title or (description and not description.startswith(">"))) and not title_has_number:
            step_num += 1
        
        # Format the step with indentation
        if title and description:
            if indent_level == 0:
                if title_has_number:
                    lines.append(f"**{title}**\n\n{description}\n")
                else:
                    lines.append(f"**{step_num}. {title}**\n\n{description}\n")
            else:
                lines.append(f"{indent}**{title}**\n\n{indent}{description}\n")
        elif title:
            if indent_level == 0:
                if title_has_number:
                    lines.append(f"**{title}**\n")
                else:
                    lines.append(f"**{step_num}. {title}**\n")
            else:
                lines.append(f"{indent}**{title}**\n")
        elif description:
            # For notes without titles (usually start with >)
            lines.append(f"{indent}{description}\n")
        
        # Process instructions array if present (UI elements like CopyableLabel)
        if isinstance(instructions, list):
            for instruction in instructions:
                if not isinstance(instruction, dict):
                    continue
                
                instr_type = instruction.get("type", "")
                parameters = instruction.get("parameters", {})
                
                # Handle different instruction types
                if instr_type == "CopyableLabel" and isinstance(parameters, dict):
                    label = parameters.get("label", "")
                    # Check for both fillWith (array) and value (string) patterns
                    fill_with = parameters.get("fillWith", [])
                    value = parameters.get("value", "")
                    if label:
                        if value:
                            # Use direct value if present
                            fill_value = value
                            lines.append(f"{indent}- **{label}**: `{fill_value}`\n")
                        elif fill_with:
                            # Use first element from fillWith array
                            fill_value = fill_with[0] if isinstance(fill_with, list) and fill_with else ""
                            lines.append(f"{indent}- **{label}**: `{fill_value}`\n")
                            lines.append(f"{indent}  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*\n")
                        else:
                            lines.append(f"{indent}- **{label}**\n")
                
                elif instr_type == "InfoMessage" and isinstance(parameters, dict):
                    # InfoMessage: inline information message
                    # Parameters: text, visible, inline
                    text = parameters.get("text", "")
                    inline = parameters.get("inline", True)
                    visible = parameters.get("visible", True)
                    if text and visible:
                        lines.append(f"\n{indent}ℹ️ {text}\n")
                
                elif instr_type == "Markdown" and isinstance(parameters, dict):
                    # Markdown: displays formatted markdown text
                    # Parameters: content
                    content = parameters.get("content", "")
                    if content:
                        lines.append(f"{indent}{content}\n")
                
                elif instr_type == "MarkdownControlEnvBased" and isinstance(parameters, dict):
                    # Environment-based markdown (prod/gov scripts)
                    prod_script = parameters.get("prodScript", "")
                    gov_script = parameters.get("govScript", "")
                    if prod_script:
                        lines.append(f"{indent}{prod_script}\n")
                    if gov_script and gov_script != prod_script:
                        lines.append(f"{indent}\n**Government Cloud:**\n{indent}{gov_script}\n")
                
                elif instr_type == "Textbox" and isinstance(parameters, dict):
                    # Textbox: input field for text, password, number, or email
                    # Parameters: label, placeholder, type, name, validations
                    label = parameters.get("label", "")
                    placeholder = parameters.get("placeholder", "")
                    text_type = parameters.get("type", "text")
                    if label:
                        if text_type == "password":
                            lines.append(f"{indent}- **{label}**: (password field)\n")
                        elif placeholder:
                            lines.append(f"{indent}- **{label}**: {placeholder}\n")
                        else:
                            lines.append(f"{indent}- **{label}**\n")
                
                elif instr_type == "OAuthForm" and isinstance(parameters, dict):
                    # OAuthForm: OAuth connection form
                    # Parameters: clientIdLabel, clientSecretLabel, connectButtonLabel, disconnectButtonLabel
                    client_id_label = parameters.get("clientIdLabel", "Client ID")
                    client_secret_label = parameters.get("clientSecretLabel", "Client Secret")
                    connect_label = parameters.get("connectButtonLabel", "Connect")
                    lines.append(f"{indent}- **OAuth Configuration**:\n")
                    lines.append(f"{indent}  - {client_id_label}\n")
                    lines.append(f"{indent}  - {client_secret_label}\n")
                    lines.append(f"{indent}  - Click '{connect_label}' to authenticate\n")
                
                elif instr_type == "Dropdown" and isinstance(parameters, dict):
                    # Dropdown: dropdown selection list
                    # Parameters: label, name, options, placeholder, isMultiSelect, required, defaultAllSelected
                    label = parameters.get("label", "")
                    options = parameters.get("options", [])
                    is_multi = parameters.get("isMultiSelect", False)
                    if label:
                        select_type = "multi-select" if is_multi else "select"
                        lines.append(f"{indent}- **{label}** ({select_type})\n")
                        if options and isinstance(options, list):
                            for opt in options[:5]:  # Show first 5 options
                                if isinstance(opt, dict):
                                    opt_text = opt.get("text", opt.get("key", ""))
                                    if opt_text:
                                        lines.append(f"{indent}  - {opt_text}\n")
                            if len(options) > 5:
                                lines.append(f"{indent}  - ... and {len(options) - 5} more options\n")
                
                elif instr_type == "InstallAgent" and isinstance(parameters, dict):
                    # InstallAgent: displays link to Azure portal sections for installation
                    # Parameters: linkType, policyDefinitionGuid, assignMode, dataCollectionRuleType
                    link_type = parameters.get("linkType", "")
                    if link_type:
                        # Map technical linkType names to user-friendly descriptions
                        link_descriptions = {
                            "InstallAgentOnWindowsVirtualMachine": "Install agent on Windows Virtual Machine",
                            "InstallAgentOnWindowsNonAzure": "Install agent on Windows (Non-Azure)",
                            "InstallAgentOnLinuxVirtualMachine": "Install agent on Linux Virtual Machine",
                            "InstallAgentOnLinuxNonAzure": "Install agent on Linux (Non-Azure)",
                            "OpenSyslogSettings": "Open Syslog settings",
                            "OpenCustomLogsSettings": "Open custom logs settings",
                            "OpenWaf": "Configure Web Application Firewall",
                            "OpenAzureFirewall": "Configure Azure Firewall",
                            "OpenMicrosoftAzureMonitoring": "Open Azure Monitoring",
                            "OpenFrontDoors": "Configure Azure Front Door",
                            "OpenCdnProfile": "Configure CDN Profile",
                            "AutomaticDeploymentCEF": "Automatic CEF deployment",
                            "OpenAzureInformationProtection": "Configure Azure Information Protection",
                            "OpenAzureActivityLog": "Configure Azure Activity Log",
                            "OpenIotPricingModel": "Configure IoT pricing",
                            "OpenPolicyAssignment": "Configure policy assignment",
                            "OpenAllAssignmentsBlade": "View all assignments",
                            "OpenCreateDataCollectionRule": "Create data collection rule"
                        }
                        description = link_descriptions.get(link_type, f"Install/configure: {link_type}")
                        lines.append(f"{indent}- **{description}**\n")
                
                elif instr_type == "ConnectionToggleButton" and isinstance(parameters, dict):
                    # ConnectionToggleButton: toggle button to connect/disconnect
                    # Parameters: connectLabel, disconnectLabel, name, disabled, isPrimary
                    connect_label = parameters.get("connectLabel", "Connect")
                    disconnect_label = parameters.get("disconnectLabel", "Disconnect")
                    lines.append(f"{indent}- Click '{connect_label}' to establish connection\n")
                
                elif instr_type == "InstructionStepsGroup" and isinstance(parameters, dict):
                    # InstructionStepsGroup: collapsible group of instructions
                    # Parameters: title, description, instructionSteps, canCollapseAllSections, expanded
                    group_title = parameters.get("title", "")
                    group_description = parameters.get("description", "")
                    group_steps = parameters.get("instructionSteps", [])
                    can_collapse = parameters.get("canCollapseAllSections", False)
                    
                    if group_title:
                        collapse_indicator = " (expandable)" if can_collapse else ""
                        lines.append(f"{indent}**{group_title}{collapse_indicator}**\n\n")
                    if group_description:
                        lines.append(f"{indent}{group_description}\n\n")
                    if group_steps:
                        nested_content = _format_instruction_steps_recursive(group_steps, indent_level + 1)
                        if nested_content:
                            lines.append(nested_content + "\n")
                
                elif instr_type == "ConfigureLogSettings" and isinstance(parameters, dict):
                    link_type = parameters.get("linkType", "")
                    lines.append(f"{indent}- Configure log settings: {link_type}\n")
                
                elif instr_type == "MSG" and isinstance(parameters, dict):
                    # Microsoft Security Graph items
                    msg_description = parameters.get("description", "")
                    items = parameters.get("items", [])
                    if msg_description:
                        lines.append(f"{indent}{msg_description}\n")
                    if items:
                        for item in items:
                            if isinstance(item, dict):
                                label = item.get("label", "")
                                if label:
                                    lines.append(f"{indent}  - {label}\n")
                
                elif instr_type in ["SecurityEvents", "WindowsSecurityEvents", "WindowsForwardedEvents", 
                                   "WindowsFirewallAma", "SysLogAma", "CefAma", "CiscoAsaAma"]:
                    # Data connector configuration types
                    lines.append(f"{indent}- Configure {instr_type} data connector\n")
                
                elif instr_type == "OmsDatasource" and isinstance(parameters, dict):
                    datasource = parameters.get("datasourceName", "")
                    if datasource:
                        lines.append(f"{indent}- Configure data source: {datasource}\n")
                
                elif instr_type == "OmsSolutions" and isinstance(parameters, dict):
                    solution = parameters.get("solutionName", "")
                    if solution:
                        lines.append(f"{indent}- Install solution: {solution}\n")
                
                elif instr_type == "SentinelResourceProvider" and isinstance(parameters, dict):
                    connector_kind = parameters.get("connectorKind", "")
                    title = parameters.get("title", connector_kind)
                    if title:
                        lines.append(f"{indent}- Connect {title}\n")
                
                elif instr_type == "DeployPushConnectorButton_test" and isinstance(parameters, dict):
                    label = parameters.get("label", "Deploy connector")
                    app_name = parameters.get("applicationDisplayName", "")
                    if label:
                        lines.append(f"{indent}- {label}\n")
                    if app_name:
                        lines.append(f"{indent}  Application: {app_name}\n")
                
                # UI-centric instruction types
                elif instr_type == "DataConnectorsGrid" and isinstance(parameters, dict):
                    # DataConnectorsGrid: displays a grid of data connectors
                    # Parameters: mapping, menuItems
                    lines.append(_format_data_connectors_grid(parameters, indent))
                
                elif instr_type == "ContextPane" and isinstance(parameters, dict):
                    # ContextPane: displays a contextual information pane
                    # Parameters: title, subtitle, contextPaneType, instructionSteps, label, isPrimary
                    lines.append(_format_context_pane(parameters, indent))
                
                elif instr_type == "GCPGrid":
                    # GCP-specific grid display
                    lines.append(_format_gcp_grid(parameters if isinstance(parameters, dict) else {}, indent))
                
                elif instr_type == "GCPContextPane":
                    # GCP-specific context pane
                    lines.append(_format_gcp_context_pane(parameters if isinstance(parameters, dict) else {}, indent))
                
                elif instr_type in ["AADDataTypes", "MCasDataTypes", "OfficeDataTypes"] and isinstance(parameters, dict):
                    # Data type selector for Microsoft services
                    lines.append(_format_data_type_selector(instr_type, parameters, indent))
                
                # For any other types, show basic info if available
                elif instr_type:
                    # For types we haven't explicitly handled, try to extract useful information
                    if isinstance(parameters, dict):
                        # Try to find useful text fields in order of preference
                        useful_text = None
                        for key in ['text', 'content', 'description', 'label', 'title', 'message']:
                            if key in parameters and isinstance(parameters[key], str) and parameters[key].strip():
                                useful_text = parameters[key].strip()
                                break
                        
                        if useful_text:
                            # Found useful text, display it
                            lines.append(f"{indent}{useful_text}\n")
                        else:
                            # No useful text found, provide a generic note
                            lines.append(f"{indent}> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `{instr_type}`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.\n")
        
        # Recursively process innerSteps if present (nested sub-steps)
        if isinstance(inner_steps, list) and inner_steps:
            inner_content = _format_instruction_steps_recursive(inner_steps, indent_level + 1)
            if inner_content:
                lines.append(inner_content)
        
        lines.append("\n")
    
    return "".join(lines).strip()


def format_permissions(permissions_json: str) -> str:
    """
    Parse and format permissions from JSON-encoded CSV field.
    
    Renders permissions based on the official Microsoft Sentinel data connector UI definitions:
    https://learn.microsoft.com/en-us/azure/sentinel/data-connector-ui-definitions-reference#permissions
    
    Args:
        permissions_json: JSON-encoded permissions object from CSV
        
    Returns:
        Formatted markdown string with permissions
    """
    if not permissions_json:
        return ""
    
    try:
        permissions = json.loads(permissions_json)
    except json.JSONDecodeError:
        # If it's not JSON, return as-is (backward compatibility)
        return permissions_json.replace('<br>', '\n').strip()
    
    if not isinstance(permissions, dict):
        return ""
    
    lines = []
    
    # Resource Provider permissions
    resource_providers = permissions.get("resourceProvider", [])
    if isinstance(resource_providers, list) and resource_providers:
        lines.append("**Resource Provider Permissions:**\n")
        for rp in resource_providers:
            if not isinstance(rp, dict):
                continue
            
            provider = rp.get("provider", "")
            provider_display = rp.get("providerDisplayName", "")
            scope = rp.get("scope", "Workspace")
            perms_text = rp.get("permissionsDisplayText", "")
            required_perms = rp.get("requiredPermissions", {})
            
            # Build permission description
            display_name = provider_display or provider
            if not display_name:
                continue
                
            perm_parts = []
            if isinstance(required_perms, dict):
                if required_perms.get("read"):
                    perm_parts.append("read")
                if required_perms.get("write"):
                    perm_parts.append("write")
                if required_perms.get("delete"):
                    perm_parts.append("delete")
                if required_perms.get("action"):
                    perm_parts.append("action")
            
            # Use permissionsDisplayText if available, otherwise build from requiredPermissions
            if perms_text:
                lines.append(f"- **{display_name}** ({scope}): {perms_text}\n")
            elif perm_parts:
                perms_desc = " and ".join(perm_parts) + " permission" + ("s" if len(perm_parts) > 1 else "")
                lines.append(f"- **{display_name}** ({scope}): {perms_desc} required.\n")
            else:
                lines.append(f"- **{display_name}** ({scope})\n")
    
    # Custom permissions
    customs = permissions.get("customs", [])
    if isinstance(customs, list) and customs:
        if lines:
            lines.append("\n")
        lines.append("**Custom Permissions:**\n")
        for custom in customs:
            if not isinstance(custom, dict):
                continue
            name = custom.get("name", "")
            description = custom.get("description", "")
            
            if name:
                if description:
                    lines.append(f"- **{name}**: {description}\n")
                else:
                    lines.append(f"- **{name}**\n")
    
    # Licenses
    licenses = permissions.get("licenses", [])
    if isinstance(licenses, list) and licenses:
        if lines:
            lines.append("\n")
        lines.append("**Licenses:**\n")
        # Map license codes to friendly names
        license_names = {
            "OfficeIRM": "Office Information Rights Management",
            "OfficeATP": "Office Advanced Threat Protection",
            "Office365": "Office 365",
            "AadP1P2": "Azure AD Premium P1/P2",
            "Mcas": "Microsoft Defender for Cloud Apps",
            "Aatp": "Microsoft Defender for Identity",
            "Mdatp": "Microsoft Defender for Endpoint",
            "Mtp": "Microsoft Threat Protection",
            "IoT": "Azure IoT"
        }
        for license in licenses:
            if isinstance(license, str):
                license_name = license_names.get(license, license)
                lines.append(f"- {license_name}\n")
    
    # Tenant permissions
    tenant = permissions.get("tenant", [])
    if isinstance(tenant, list) and tenant:
        if lines:
            lines.append("\n")
        lines.append("**Tenant Permissions:**\n")
        tenant_roles = ", ".join(tenant)
        lines.append(f"Requires {tenant_roles} on the workspace's tenant\n")
    
    return "".join(lines).strip()


def generate_index_page(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate the main index page with table of all solutions."""
    
    index_path = output_dir / "solutions-index.md"
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Solutions Index\n\n")
        f.write("This reference documentation provides detailed information about data connectors ")
        f.write("available in Microsoft Sentinel Solutions.\n\n")
        
        # Add navigation to other indexes
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md) (this page)\n")
        f.write("- [Connectors](connectors-index.md)\n")
        f.write("- [Tables](tables-index.md)\n\n")
        f.write("---\n\n")
        
        f.write("## Overview\n\n")
        
        # Count solutions with connectors (solutions that have at least one row with non-empty connector_id)
        solutions_with_connectors = 0
        for connectors in solutions.values():
            # A solution has a connector if at least one of its rows has a non-empty connector_id
            has_connector = False
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                # Handle both empty strings and 'nan' string values
                if connector_id and str(connector_id).strip() and str(connector_id).strip().lower() != 'nan':
                    has_connector = True
                    break
            if has_connector:
                solutions_with_connectors += 1
        
        f.write(f"This documentation covers **{len(solutions)} solutions**, ")
        if solutions_with_connectors == len(solutions):
            f.write(f"all of which include data connectors, ")
        else:
            f.write(f"of which **{solutions_with_connectors}** include data connectors, ")
        
        # Count unique connectors across all solutions
        all_connector_ids = set()
        for connectors in solutions.values():
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                if connector_id:
                    all_connector_ids.add(connector_id)
        
        # Count unique tables across all solutions
        all_tables = set()
        for connectors in solutions.values():
            for conn in connectors:
                table = conn.get('Table', '')
                if table:
                    all_tables.add(table)
        
        f.write(f"providing access to **{len(all_connector_ids)} unique connectors** ")
        f.write(f"and **{len(all_tables)} unique tables**.\n\n")
        
        # Statistics section
        f.write("### Quick Statistics\n\n")
        f.write("| Metric | Count |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Solutions | {len(solutions)} |\n")
        f.write(f"| Solutions with Connectors | {solutions_with_connectors} ({100*solutions_with_connectors//len(solutions)}%) |\n")
        f.write(f"| Unique Connectors | {len(all_connector_ids)} |\n")
        f.write(f"| Unique Tables | {len(all_tables)} |\n\n")
        
        # Organization section
        f.write("## How This Documentation is Organized\\n\\n")
        f.write("Each solution has its own page containing:\n\n")
        f.write("- **Solution Overview**: Publisher, support information, and categories\n")
        f.write("- **Connectors**: List of all connectors in the solution\n")
        f.write("- **Tables**: Data tables ingested by the connectors\n")
        f.write("- **GitHub Links**: Direct links to connector definition files\n\n")
        
        # Generate alphabetical index
        f.write("## Solutions Index\n\n")
        f.write("Browse solutions alphabetically:\n\n")
        
        # Create alphabetical sections
        by_letter: Dict[str, List[str]] = defaultdict(list)
        for solution_name in sorted(solutions.keys()):
            first_letter = solution_name[0].upper()
            if first_letter.isalpha():
                by_letter[first_letter].append(solution_name)
            else:
                by_letter['#'].append(solution_name)
        
        # Letter navigation
        f.write("**Jump to:** ")
        letters = sorted(by_letter.keys())
        f.write(" | ".join(f"[{letter}](#{letter.lower()})" for letter in letters))
        f.write("\n\n")
        
        # Generate sections by letter
        for letter in letters:
            f.write(f"### {letter}\n\n")
            f.write("| Solution | First Published | Publisher |\n")
            f.write("|----------|----------------|----------|\n")
            
            for solution_name in sorted(by_letter[letter]):
                connectors = solutions[solution_name]
                
                support_tier = connectors[0].get('solution_support_tier', 'N/A')
                support_name = connectors[0].get('solution_support_name', 'N/A')
                first_published = connectors[0].get('solution_first_publish_date', 'N/A')
                
                solution_link = f"[{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)"
                f.write(f"| {solution_link} | {first_published} | {support_name} |\n")
            
            f.write("\n")
    
    print(f"Generated index: {index_path}")


def generate_connectors_index(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate connectors index page organized alphabetically."""
    
    index_path = output_dir / "connectors-index.md"
    
    # Collect all unique connectors with their metadata
    connectors_map: Dict[str, Dict[str, any]] = {}
    
    for solution_name, connectors in solutions.items():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if not connector_id or connector_id in connectors_map:
                continue
            
            connector_title = conn.get('connector_title', connector_id)
            connectors_map[connector_id] = {
                'title': connector_title,
                'publisher': conn.get('connector_publisher', 'N/A'),
                'solution_name': solution_name,
                'solution_folder': conn.get('solution_folder', ''),
                'tables': set(),
                'description': conn.get('connector_description', ''),
            }
        
        # Collect all tables for each connector
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if connector_id in connectors_map:
                table = conn.get('Table', '')
                if table:
                    connectors_map[connector_id]['tables'].add(table)
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Connectors Index\n\n")
        f.write("Browse all data connectors available in Microsoft Sentinel Solutions.\n\n")
        
        # Add navigation
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](connector-reference-index.md)\n")
        f.write("- [Connectors](connectors-index.md) (this page)\n")
        f.write("- [Tables](tables-index.md)\n\n")
        f.write("---\n\n")
        
        f.write(f"## Overview\n\n")
        f.write(f"This page lists **{len(connectors_map)} unique connectors** across all solutions.\n\n")
        
        # Separate deprecated and active connectors
        deprecated_connectors = {}
        active_connectors = {}
        
        for connector_id, info in connectors_map.items():
            title = info['title']
            if '[DEPRECATED]' in title.upper() or title.startswith('[Deprecated]'):
                deprecated_connectors[connector_id] = info
            else:
                active_connectors[connector_id] = info
        
        # Create alphabetical index for active connectors
        by_letter: Dict[str, List[str]] = defaultdict(list)
        for connector_id, info in active_connectors.items():
            title = info['title']
            first_letter = title[0].upper()
            if first_letter.isalpha():
                by_letter[first_letter].append(connector_id)
            else:
                by_letter['#'].append(connector_id)
        
        # Letter navigation
        f.write("**Jump to:** ")
        letters = sorted(by_letter.keys())
        f.write(" | ".join(f"[{letter}](#{letter.lower()})" for letter in letters))
        f.write("\n\n")
        
        # Generate sections by letter
        for letter in letters:
            f.write(f"## {letter}\n\n")
            
            for connector_id in sorted(by_letter[letter], key=lambda cid: connectors_map[cid]['title']):
                info = connectors_map[connector_id]
                title = info['title']
                publisher = info['publisher']
                solution_name = info['solution_name']
                tables = sorted(info['tables'])
                
                f.write(f"### [{title}](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write(f"**Publisher:** {publisher}\n\n")
                f.write(f"**Solution:** [{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)\n\n")
                
                if tables:
                    f.write(f"**Tables ({len(tables)}):** ")
                    f.write(", ".join(f"`{table}`" for table in tables))
                    f.write("\n\n")
                
                description = info['description']
                if description:
                    # Replace <br> with newline but preserve markdown links
                    description = description.replace('<br>', '\n')
                    f.write(f"{description}\n\n")
                
                f.write(f"[→ View full connector details](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write("---\n\n")
        
        # Add deprecated connectors section at the end
        if deprecated_connectors:
            f.write("## Deprecated Connectors\n\n")
            f.write(f"The following **{len(deprecated_connectors)} connector(s)** are deprecated:\n\n")
            
            for connector_id in sorted(deprecated_connectors.keys(), key=lambda cid: deprecated_connectors[cid]['title']):
                info = deprecated_connectors[connector_id]
                title = info['title']
                publisher = info['publisher']
                solution_name = info['solution_name']
                tables = sorted(info['tables'])
                
                f.write(f"### [{title}](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write(f"**Publisher:** {publisher}\n\n")
                f.write(f"**Solution:** [{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)\n\n")
                
                if tables:
                    f.write(f"**Tables ({len(tables)}):** ")
                    f.write(", ".join(f"`{table}`" for table in tables))
                    f.write("\n\n")
                
                description = info['description']
                if description:
                    # Replace <br> with newline but preserve markdown links
                    description = description.replace('<br>', '\n')
                    f.write(f"{description}\n\n")
                
                f.write(f"[→ View full connector details](connectors/{sanitize_anchor(connector_id)}.md)\n\n")
                f.write("---\n\n")
    
    print(f"Generated connectors index: {index_path}")


def generate_tables_index(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate tables index page organized alphabetically."""
    
    index_path = output_dir / "tables-index.md"
    
    # Collect all unique tables with their usage
    tables_map: Dict[str, Dict[str, any]] = defaultdict(lambda: {
        'solutions': set(),
        'connectors': set(),
        'is_unique': False,
    })
    
    for solution_name, connectors in solutions.items():
        for conn in connectors:
            table = conn.get('Table', '')
            if not table:
                continue
            
            connector_id = conn.get('connector_id', '')
            # Skip entries with empty connector_id (solutions without connectors)
            if not connector_id.strip():
                continue
            connector_title = conn.get('connector_title', connector_id)
            tables_map[table]['solutions'].add(solution_name)
            tables_map[table]['connectors'].add((connector_id, connector_title))
            
            # Check if unique
            if conn.get('is_unique', 'false') == 'true':
                tables_map[table]['is_unique'] = True
    
    with index_path.open("w", encoding="utf-8") as f:
        f.write("# Microsoft Sentinel Tables Index\n\n")
        f.write("Browse all tables ingested by Microsoft Sentinel data connectors.\n\n")
        
        # Add navigation
        f.write("**Browse by:**\n\n")
        f.write("- [Solutions](solutions-index.md)\n")
        f.write("- [Connectors](connectors-index.md)\n")
        f.write("- [Tables](tables-index.md) (this page)\n\n")
        f.write("---\n\n")
        
        f.write(f"## Overview\n\n")
        f.write(f"This page lists **{len(tables_map)} unique tables** ingested by connectors.\n\n")
        
        # Create alphabetical index
        by_letter: Dict[str, List[str]] = defaultdict(list)
        for table in tables_map.keys():
            first_letter = table[0].upper()
            if first_letter.isalpha():
                by_letter[first_letter].append(table)
            else:
                by_letter['#'].append(table)
        
        # Letter navigation
        f.write("**Jump to:** ")
        letters = sorted(by_letter.keys())
        f.write(" | ".join(f"[{letter}](#{letter.lower()})" for letter in letters))
        f.write("\n\n")
        
        # Generate sections by letter
        for letter in letters:
            f.write(f"## {letter}\n\n")
            f.write("| Table | Solutions | Connectors |\n")
            f.write("|-------|-----------|------------|\n")
            
            for table in sorted(by_letter[letter]):
                info = tables_map[table]
                num_solutions = len(info['solutions'])
                num_connectors = len(info['connectors'])
                
                # Determine if we should create individual table page
                has_table_page = num_solutions > 1 or num_connectors > 1
                
                # Table name cell with optional link
                if has_table_page:
                    table_cell = f"[`{table}`](tables/{sanitize_anchor(table)}.md)"
                else:
                    table_cell = f"`{table}`"
                
                # Solutions cell - limit to 3 items, link to table page for more
                if num_solutions == 1:
                    solution_name = list(info['solutions'])[0]
                    solutions_cell = f"[{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)"
                elif num_solutions <= 3:
                    solution_links = []
                    for solution_name in sorted(info['solutions']):
                        solution_links.append(f"[{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)")
                    solutions_cell = ", ".join(solution_links)
                else:
                    solution_links = []
                    for solution_name in sorted(info['solutions'])[:3]:
                        solution_links.append(f"[{solution_name}](solutions/{sanitize_anchor(solution_name)}.md)")
                    more_link = f"[+{num_solutions - 3} more](tables/{sanitize_anchor(table)}.md)"
                    solutions_cell = ", ".join(solution_links) + " " + more_link
                
                # Connectors cell - limit to 5 items, link to table page for more
                if num_connectors == 1:
                    connector_id, connector_title = list(info['connectors'])[0]
                    connectors_cell = f"[{connector_title}](connectors/{sanitize_anchor(connector_id)}.md)"
                elif num_connectors <= 5:
                    connector_links = []
                    for connector_id, connector_title in sorted(info['connectors']):
                        connector_links.append(f"[{connector_title}](connectors/{sanitize_anchor(connector_id)}.md)")
                    connectors_cell = ", ".join(connector_links)
                else:
                    connector_links = []
                    for connector_id, connector_title in sorted(info['connectors'])[:5]:
                        connector_links.append(f"[{connector_title}](connectors/{sanitize_anchor(connector_id)}.md)")
                    more_link = f"[+{num_connectors - 5} more](tables/{sanitize_anchor(table)}.md)"
                    connectors_cell = ", ".join(connector_links) + " " + more_link
                
                f.write(f"| {table_cell} | {solutions_cell} | {connectors_cell} |\n")
            
            f.write("\n")
    
    print(f"Generated tables index: {index_path}")
    
    # Return tables_map for use in generating table pages
    return tables_map


def generate_table_pages(tables_map: Dict[str, Dict[str, any]], output_dir: Path) -> None:
    """Generate individual table documentation pages for tables with multiple solutions or connectors."""
    
    table_dir = output_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    
    pages_created = 0
    
    for table, info in sorted(tables_map.items()):
        num_solutions = len(info['solutions'])
        num_connectors = len(info['connectors'])
        
        # Only create pages for tables with multiple solutions or connectors
        if num_solutions <= 1 and num_connectors <= 1:
            continue
        
        table_path = table_dir / f"{sanitize_anchor(table)}.md"
        
        with table_path.open("w", encoding="utf-8") as f:
            f.write(f"# {table}\n\n")
            
            # Overview
            f.write(f"**Table:** `{table}`\n\n")
            f.write(f"This table is ingested by **{num_solutions} solution(s)** using **{num_connectors} connector(s)**.\n\n")
            
            if info.get('is_unique', False):
                f.write("⚠️ **Note:** This table name is unique to specific connectors.\n\n")
            
            f.write("---\n\n")
            
            # Solutions section
            f.write(f"## Solutions ({num_solutions})\n\n")
            f.write("This table is used by the following solutions:\n\n")
            for solution_name in sorted(info['solutions']):
                f.write(f"- [{solution_name}](../solutions/{sanitize_anchor(solution_name)}.md)\n")
            f.write("\n")
            
            # Connectors section
            f.write(f"## Connectors ({num_connectors})\n\n")
            f.write("This table is ingested by the following connectors:\n\n")
            for connector_id, connector_title in sorted(info['connectors']):
                f.write(f"- [{connector_title}](../connectors/{sanitize_anchor(connector_id)}.md)\n")
            f.write("\n")
            
            # Navigation
            f.write("---\n\n")
            f.write("**Browse:**\n\n")
            f.write("- [← Back to Tables Index](../tables-index.md)\n")
            f.write("- [Solutions Index](../solutions-index.md)\n")
            f.write("- [Connectors Index](../connectors-index.md)\n")
        
        pages_created += 1
    
    print(f"Generated {pages_created} individual table pages")


def generate_connector_pages(solutions: Dict[str, List[Dict[str, str]]], output_dir: Path) -> None:
    """Generate individual connector documentation pages."""
    
    connector_dir = output_dir / "connectors"
    connector_dir.mkdir(parents=True, exist_ok=True)
    
    # Group all data by connector_id
    by_connector: Dict[str, Dict[str, any]] = defaultdict(lambda: {
        'entries': [],
        'solutions': set(),
        'tables': set()
    })
    
    for solution_name, connectors in solutions.items():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            # Skip entries with empty connector_id (solutions without connectors)
            if not connector_id.strip():
                continue
            by_connector[connector_id]['entries'].append(conn)
            by_connector[connector_id]['solutions'].add(solution_name)
            by_connector[connector_id]['tables'].add(conn.get('Table', ''))
    
    # Generate a page for each connector
    for connector_id, data in sorted(by_connector.items()):
        connector_path = connector_dir / f"{sanitize_anchor(connector_id)}.md"
        entries = data['entries']
        first_entry = entries[0]
        
        connector_title = first_entry.get('connector_title', connector_id)
        
        with connector_path.open("w", encoding="utf-8") as f:
            f.write(f"# {connector_title}\n\n")
            
            # Connector metadata table (no column headers)
            f.write("| | |\n")
            f.write("|----------|-------|\n")
            f.write(f"| **Connector ID** | `{connector_id}` |\n")
            
            publisher = first_entry.get('connector_publisher', '')
            if publisher:
                f.write(f"| **Publisher** | {publisher} |\n")
            
            # Tables
            tables_list = ", ".join([f"[`{table}`](../tables-index.md#{table.lower()})" for table in sorted(data['tables']) if table])
            f.write(f"| **Tables Ingested** | {tables_list} |\n")
            
            # Solutions
            solutions_list = ", ".join([f"[{solution_name}](../solutions/{sanitize_anchor(solution_name)}.md)" for solution_name in sorted(data['solutions'])])
            f.write(f"| **Used in Solutions** | {solutions_list} |\n")
            
            # Connector files
            connector_files = first_entry.get('connector_files', '')
            if connector_files:
                files = [f.strip() for f in connector_files.split(';') if f.strip()]
                if files:
                    files_list = ", ".join([f"[{file_url.split('/')[-1]}]({file_url})" for file_url in files])
                    f.write(f"| **Connector Definition Files** | {files_list} |\n")
            
            f.write("\n")
            
            # Description at the bottom
            description = first_entry.get('connector_description', '')
            if description:
                description = description.replace('<br>', '\n\n')
                f.write(f"{description}\n\n")
            
            # Permissions section
            permissions = first_entry.get('connector_permissions', '')
            if permissions:
                f.write("## Permissions\n\n")
                formatted_permissions = format_permissions(permissions)
                f.write(f"{formatted_permissions}\n\n")
            
            # Setup Instructions section
            instruction_steps = first_entry.get('connector_instruction_steps', '')
            if instruction_steps:
                f.write("## Setup Instructions\n\n")
                f.write("> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.\n\n")
                formatted_instructions = format_instruction_steps(instruction_steps)
                f.write(f"{formatted_instructions}\n\n")
            
            # Back navigation
            f.write("[← Back to Connectors Index](../connectors-index.md)\n")
        
        print(f"Generated connector page: {connector_path}")


def generate_solution_page(solution_name: str, connectors: List[Dict[str, str]], output_dir: Path) -> None:
    """Generate individual solution documentation page."""
    
    solution_dir = output_dir / "solutions"
    solution_dir.mkdir(parents=True, exist_ok=True)
    
    solution_path = solution_dir / f"{sanitize_anchor(solution_name)}.md"
    
    # Get solution-level metadata from first connector entry
    metadata = connectors[0]
    
    # Check if this solution has any connectors (connector_id will be empty for all entries if not)
    has_connectors = any(bool(conn.get('connector_id', '').strip()) for conn in connectors)
    
    with solution_path.open("w", encoding="utf-8") as f:
        f.write(f"# {solution_name}\n\n")
        
        # Solution metadata section
        f.write("## Solution Information\n\n")
        f.write("| | |\n")
        f.write("|------------------------|-------|\n")
        f.write(f"| **Publisher** | {metadata.get('solution_support_name', 'N/A')} |\n")
        f.write(f"| **Support Tier** | {metadata.get('solution_support_tier', 'N/A')} |\n")
        
        support_link = metadata.get('solution_support_link', '')
        if support_link:
            f.write(f"| **Support Link** | [{support_link}]({support_link}) |\n")
        
        categories = metadata.get('solution_categories', '')
        if categories:
            f.write(f"| **Categories** | {categories} |\n")
        
        version = metadata.get('solution_version', '')
        if version:
            f.write(f"| **Version** | {version} |\n")
        
        author = metadata.get('solution_author_name', '')
        if author:
            f.write(f"| **Author** | {author} |\n")
        
        first_publish = metadata.get('solution_first_publish_date', '')
        if first_publish:
            f.write(f"| **First Published** | {first_publish} |\n")
        
        last_publish = metadata.get('solution_last_publish_date', '')
        if last_publish:
            f.write(f"| **Last Updated** | {last_publish} |\n")
        
        solution_folder = metadata.get('solution_folder', '')
        if solution_folder:
            f.write(f"| **Solution Folder** | [{solution_folder}]({solution_folder}) |\n")
        
        f.write("\n")
        
        # Only include connectors section if solution has connectors
        if not has_connectors:
            f.write("## Data Connectors\n\n")
            f.write("**This solution does not include data connectors.**\n\n")
            f.write("This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.\n\n")
        else:
            # Group by connector (filter out empty connector_ids from the row added for solutions without connectors)
            by_connector: Dict[str, List[Dict[str, str]]] = defaultdict(list)
            for conn in connectors:
                connector_id = conn.get('connector_id', '')
                if connector_id.strip():  # Only include non-empty connector_ids
                    by_connector[connector_id].append(conn)
            
            # Connectors section
            f.write("## Data Connectors\n\n")
            f.write(f"This solution provides **{len(by_connector)} data connector(s)**.\n\n")
            
            for connector_id in sorted(by_connector.keys()):
                conn_entries = by_connector[connector_id]
                first_conn = conn_entries[0]
                
                connector_title = first_conn.get('connector_title', connector_id)
                connector_link = f"[{connector_title}](../connectors/{sanitize_anchor(connector_id)}.md)"
                f.write(f"### {connector_link}\n\n")
                
                # Connector metadata
                publisher = first_conn.get('connector_publisher', '')
                if publisher:
                    f.write(f"**Publisher:** {publisher}\n\n")
                
            description = first_conn.get('connector_description', '')
            if description:
                # Replace <br> with newlines but preserve markdown formatting
                description = description.replace('<br>', '\n\n')
                f.write(f"{description}\n\n")
            
            # Permissions section
            permissions = first_conn.get('connector_permissions', '')
            if permissions:
                f.write("**Permissions:**\n\n")
                formatted_permissions = format_permissions(permissions)
                f.write(f"{formatted_permissions}\n\n")
            
            # Setup Instructions section
            instruction_steps = first_conn.get('connector_instruction_steps', '')
            if instruction_steps:
                f.write("**Setup Instructions:**\n\n")
                f.write("> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.\n\n")
                formatted_instructions = format_instruction_steps(instruction_steps)
                f.write(f"{formatted_instructions}\n\n")
            
            # Combined table for Tables Ingested and Connector Definition Files
            tables = sorted(set(conn['Table'] for conn in conn_entries))
            connector_files = first_conn.get('connector_files', '')
            files = [f.strip() for f in connector_files.split(';') if f.strip()] if connector_files else []
            
            f.write("| | |\n")
            f.write("|--------------------------|---|\n")
            
            # Tables Ingested
            if len(tables) == 1:
                f.write(f"| **Tables Ingested** | `{tables[0]}` |\n")
            else:
                for i, table in enumerate(tables):
                    if i == 0:
                        f.write(f"| **Tables Ingested** | `{table}` |\n")
                    else:
                        f.write(f"| | `{table}` |\n")
            
            # Connector Definition Files
            if files:
                for i, file_url in enumerate(files):
                    file_name = file_url.split('/')[-1]
                    if i == 0:
                        f.write(f"| **Connector Definition Files** | [{file_name}]({file_url}) |\n")
                    else:
                        f.write(f"| | [{file_name}]({file_url}) |\n")
            
            f.write("\n")
            
            # Link to connector page
            f.write(f"[→ View full connector details](../connectors/{sanitize_anchor(connector_id)}.md)\n\n")
        
            # Tables summary section (only for solutions with connectors)
            all_tables = sorted(set(conn['Table'] for conn in connectors if conn.get('Table', '').strip()))
            if all_tables:
                f.write("## Tables Reference\n\n")
                f.write(f"This solution ingests data into **{len(all_tables)} table(s)**:\n\n")
                
                f.write("| Table | Used By Connectors |\n")
                f.write("|-------|-------------------|\n")
                
                for table in all_tables:
                    # Get connector info (id and title) for this table
                    table_connectors = []
                    for conn in connectors:
                        if conn.get('Table') == table:
                            connector_id = conn.get('connector_id', '')
                            connector_title = conn.get('connector_title', connector_id)
                            table_connectors.append((connector_id, connector_title))
                    
                    # Remove duplicates and sort by title
                    unique_connectors = sorted(set(table_connectors), key=lambda x: x[1])
                    
                    # Create links to connector pages
                    connector_links = [f"[{title}](../connectors/{sanitize_anchor(cid)}.md)" for cid, title in unique_connectors]
                    connector_list = ", ".join(connector_links)
                    
                    f.write(f"| `{table}` | {connector_list} |\n")
                
                f.write("\n")
        
        # Back navigation
        f.write("[← Back to Solutions Index](../solutions-index.md)\n")
    
    print(f"Generated solution page: {solution_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Microsoft Learn-style connector documentation from CSV"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent / "solutions_connectors_tables_mapping.csv",
        help="Path to input CSV file (default: solutions_connectors_tables_mapping.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "connector-docs",
        help="Output directory for generated documentation (default: connector-docs/)",
    )
    parser.add_argument(
        "--solutions",
        nargs="*",
        help="Generate docs only for specific solutions (default: all solutions)",
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read CSV
    print(f"Reading {args.input}...")
    with args.input.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    print(f"Loaded {len(rows)} rows")
    
    # Group by solution
    by_solution: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        solution_name = row.get('solution_name', 'Unknown')
        by_solution[solution_name].append(row)
    
    # Filter solutions if specified
    if args.solutions:
        by_solution = {
            name: connectors
            for name, connectors in by_solution.items()
            if name in args.solutions
        }
        print(f"Filtered to {len(by_solution)} solution(s)")
    
    print(f"Generating documentation for {len(by_solution)} solution(s)...")
    
    # Generate index pages
    generate_index_page(by_solution, args.output_dir)
    generate_connectors_index(by_solution, args.output_dir)
    tables_map = generate_tables_index(by_solution, args.output_dir)
    
    # Generate individual table pages
    generate_table_pages(tables_map, args.output_dir)
    
    # Generate individual connector pages
    generate_connector_pages(by_solution, args.output_dir)
    
    # Generate individual solution pages
    for solution_name, connectors in sorted(by_solution.items()):
        generate_solution_page(solution_name, connectors, args.output_dir)
    
    # Count unique connectors and tables
    all_connector_ids = set()
    for connectors in by_solution.values():
        for conn in connectors:
            connector_id = conn.get('connector_id', '')
            if connector_id:
                all_connector_ids.add(connector_id)
    
    # Count table pages created
    table_pages_count = sum(1 for t in tables_map.values() if len(t['solutions']) > 1 or len(t['connectors']) > 1)
    
    print(f"\nDocumentation generated successfully in: {args.output_dir}")
    print(f"  - Solutions index: {args.output_dir / 'solutions-index.md'}")
    print(f"  - Connectors index: {args.output_dir / 'connectors-index.md'}")
    print(f"  - Tables index: {args.output_dir / 'tables-index.md'}")
    print(f"  - Solutions: {args.output_dir / 'solutions'}/ ({len(by_solution)} files)")
    print(f"  - Connectors: {args.output_dir / 'connectors'}/ ({len(all_connector_ids)} files)")
    print(f"  - Tables: {args.output_dir / 'tables'}/ ({table_pages_count} files)")


if __name__ == "__main__":
    main()
