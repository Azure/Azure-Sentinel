import sys
import os
import json
import requests
import openai
from azure.identity import DefaultAzureCredential

def get_azure_openai_token():
    """Get Azure AD token for Azure OpenAI"""
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return token.token

def get_pr_changes(pr_number):
    """Fetch PR changes using GitHub API"""
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get PR details
    pr_url = f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/pulls/{pr_number}'
    pr_response = requests.get(pr_url, headers=headers)
    pr_data = pr_response.json()
    
    # Get PR files
    files_url = f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/pulls/{pr_number}/files'
    files_response = requests.get(files_url, headers=headers)
    files_data = files_response.json()
    
    return pr_data, files_data

def analyze_changes(files_data):
    """Analyze the changes and categorize them"""
    categories = {
        'detections': [],
        'playbooks': [],
        'workbooks': [],
        'parsers': [],
        'data_connectors': [],
        'documentation': [],
        'other': []
    }
    
    for file in files_data:
        filename = file['filename'].lower()
        filepath = file['filename']  # Keep original case for path checking
        
        # Check for Data Connectors folder (various naming patterns)
        if any(pattern in filepath.lower() for pattern in [
            'dataconnectors/',
            'data connectors/',
            'data-connectors/',
            'dataconnector/'
        ]):
            categories['data_connectors'].append(file)
        # Check for CCP suffix in folder names
        elif '_ccp/' in filepath.lower():
            categories['data_connectors'].append(file)
        # Check for CEF/CCF files
        elif any(term in filename for term in ['_ccf', '_ccp']):
            categories['data_connectors'].append(file)
        # Check for detection rules
        elif 'detection' in filename or filename.endswith('.yaml') or filename.endswith('.yml'):
            categories['detections'].append(file)
        elif 'playbook' in filename:
            categories['playbooks'].append(file)
        elif 'workbook' in filename:
            categories['workbooks'].append(file)
        elif 'parser' in filename or 'asim' in filename:
            categories['parsers'].append(file)
        elif filename.endswith(('.md', '.txt', '.rst')):
            categories['documentation'].append(file)
        else:
            categories['other'].append(file)
    
    return categories

def generate_pr_description(pr_data, changes_summary):
    """Generate PR description using Azure OpenAI"""
    # Configure OpenAI for Azure
    openai.api_type = "azure_ad"
    openai.api_base = os.getenv("ENDPOINT_URL")
    openai.api_version = "2023-12-01-preview"
    openai.api_key = get_azure_openai_token()
    
    prompt = f"""
Generate a comprehensive PR description for this Azure Sentinel contribution:

PR Title: {pr_data.get('title', '')}
Changes Summary: {json.dumps(changes_summary, indent=2)}

Create a description that includes:
1. **Purpose**: What this PR accomplishes
2. **Changes**: Categorized list of modifications
3. **Type**: Detection Rule/Playbook/Workbook/Parser/Documentation
4. **Testing**: Any testing considerations
5. **Impact**: What users/environments this affects

Keep it professional, clear, and helpful for reviewers.
"""

    response = openai.chat.completions.create(
        model=os.getenv("DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.3
    )
    
    return response.choices[0].message.content

def update_pr_description(pr_number, description):
    """Update PR description using GitHub API"""
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/pulls/{pr_number}'
    data = {'body': description}
    
    response = requests.patch(url, headers=headers, json=data)
    return response.status_code == 200

def main():
    if len(sys.argv) != 2:
        print("Usage: python pr_description_generator.py <pr_number>")
        sys.exit(1)
    
    pr_number = sys.argv[1]
    
    try:
        # Get PR data and changes
        pr_data, files_data = get_pr_changes(pr_number)
        
        # Analyze changes
        changes_summary = analyze_changes(files_data)
        
        # Generate description
        description = generate_pr_description(pr_data, changes_summary)
        
        # Update PR
        if update_pr_description(pr_number, description):
            print(f"✅ Successfully updated PR #{pr_number} description")
        else:
            print(f"❌ Failed to update PR #{pr_number} description")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()