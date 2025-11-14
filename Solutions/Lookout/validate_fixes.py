#!/usr/bin/env python3
"""Quick validation script for Lookout analytic rules"""
import yaml
import json
import sys
from pathlib import Path

MOBILE_TECHNIQUES = {
    'T1417': ('Input Capture', ['CredentialAccess', 'Collection']),
    'T1418': ('Software Discovery', ['Discovery']),
    'T1423': ('Network Service Scanning', ['Discovery']),
    'T1424': ('Process Discovery', ['Discovery']),
    'T1626': ('Abuse Elevation Control Mechanism', ['PrivilegeEscalation']),
    'T1629': ('Impair Defenses', ['DefenseEvasion']),
    'T1630': ('Indicator Removal on Host', ['DefenseEvasion']),
    'T1655': ('Masquerading', ['DefenseEvasion']),
    'T1660': ('Phishing', ['InitialAccess']),
}

MOBILE_TACTICS = [
    'InitialAccess', 'Execution', 'Persistence', 'PrivilegeEscalation',
    'DefenseEvasion', 'CredentialAccess', 'Discovery', 'LateralMovement',
    'Collection', 'CommandAndControl', 'Exfiltration', 'Impact'
]

VALID_ENTITY_IDENTIFIERS = {
    'Account': ['Name', 'FullName', 'NTDomain', 'DnsDomain', 'UPNSuffix', 'Sid', 'AadTenantId', 'AadUserId', 'PUID', 'IsDomainJoined', 'DisplayName', 'ObjectGuid'],
    'Host': ['DnsDomain', 'NTDomain', 'HostName', 'FullName', 'NetBiosName', 'AzureID', 'OMSAgentID', 'OSFamily', 'OSVersion', 'IsDomainJoined'],
    'FileHash': ['Algorithm', 'Value'],
    'URL': ['Url'],
}

def load_valid_connector_ids():
    """Load valid connector IDs from ValidConnectorIds.json"""
    json_path = Path(__file__).parents[2] / '.script' / 'tests' / 'detectionTemplateSchemaValidation' / 'ValidConnectorIds.json'
    with open(json_path, 'r') as f:
        return json.load(f)

def validate_rule(yaml_file):
    """Validate a single YAML rule file"""
    errors = []
    warnings = []
    
    with open(yaml_file, 'r') as f:
        rule = yaml.safe_load(f)
    
    rule_name = yaml_file.name
    
    # Check connector ID
    if 'requiredDataConnectors' in rule:
        for connector in rule['requiredDataConnectors']:
            conn_id = connector.get('connectorId')
            if 'V2' in rule_name and conn_id != 'Lookout-Mobile-Threat-Defense':
                errors.append(f"V2 rule should use 'Lookout-Mobile-Threat-Defense', found '{conn_id}'")
            
            # Check if connector ID is in valid list
            valid_ids = load_valid_connector_ids()
            if conn_id not in valid_ids:
                errors.append(f"Connector ID '{conn_id}' not in ValidConnectorIds.json")
    
    # Check techniques are Mobile-compatible
    if 'relevantTechniques' in rule:
        for technique in rule['relevantTechniques']:
            if technique not in MOBILE_TECHNIQUES:
                errors.append(f"Technique '{technique}' is not a valid Mobile ATT&CK technique")
    
    # Check tactics are Mobile-compatible
    if 'tactics' in rule:
        for tactic in rule['tactics']:
            if tactic not in MOBILE_TACTICS:
                errors.append(f"Tactic '{tactic}' is not a valid Mobile tactic")
    
    # Validate entity mappings
    if 'entityMappings' in rule:
        for entity in rule['entityMappings']:
            entity_type = entity.get('entityType')
            if entity_type in VALID_ENTITY_IDENTIFIERS:
                for field_mapping in entity.get('fieldMappings', []):
                    identifier = field_mapping.get('identifier')
                    if identifier not in VALID_ENTITY_IDENTIFIERS[entity_type]:
                        errors.append(f"Invalid identifier '{identifier}' for entity type '{entity_type}'")
    
    # Verify tactics match techniques
    if 'tactics' in rule and 'relevantTechniques' in rule:
        rule_tactics = set(rule['tactics'])
        for technique in rule['relevantTechniques']:
            if technique in MOBILE_TECHNIQUES:
                tech_tactics = set(MOBILE_TECHNIQUES[technique][1])
                if not tech_tactics.intersection(rule_tactics):
                    warnings.append(f"Technique {technique} tactics {tech_tactics} don't match rule tactics {rule_tactics}")
    
    return errors, warnings

def main():
    rules_dir = Path(__file__).parent / 'Analytic Rules'
    v2_rules = list(rules_dir.glob('*V2.yaml'))
    
    print("=" * 70)
    print("LOOKOUT ANALYTIC RULES VALIDATION")
    print("=" * 70)
    
    total_errors = 0
    total_warnings = 0
    
    for rule_file in sorted(v2_rules):
        errors, warnings = validate_rule(rule_file)
        
        if errors or warnings:
            print(f"\n{rule_file.name}:")
            if errors:
                for error in errors:
                    print(f"  ❌ ERROR: {error}")
                    total_errors += 1
            if warnings:
                for warning in warnings:
                    print(f"  ⚠️  WARNING: {warning}")
                    total_warnings += 1
        else:
            print(f"\n✅ {rule_file.name}: All checks passed")
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_errors} errors, {total_warnings} warnings")
    print("=" * 70)
    
    return 0 if total_errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
