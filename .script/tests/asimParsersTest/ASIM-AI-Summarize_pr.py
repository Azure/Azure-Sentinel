import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import logging
import sys
import subprocess
import json
import requests

# Get the Github token from the environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Get the PR number from the environment variables
GITHUB_PR_NUMBER = os.getenv("GITHUB_PR_NUMBER")

# Sentinel Repo URL
SentinelRepoUrl = f"https://github.com/Azure/Azure-Sentinel.git"

# Fetch the PR diff using `gh` CLI command
def get_git_diff():
    # Get modified ASIM Parser files along with their status
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Add upstream remote if not already present
    git_remote_command = "git remote"
    remote_result = subprocess.run(git_remote_command, shell=True, text=True, capture_output=True, check=True)
    if 'upstream' not in remote_result.stdout.split():
        git_add_upstream_command = f"git remote add upstream '{SentinelRepoUrl}'"
        subprocess.run(git_add_upstream_command, shell=True, text=True, capture_output=True, check=True)
    # Fetch from upstream
    git_fetch_upstream_command = "git fetch upstream"
    subprocess.run(git_fetch_upstream_command, shell=True, text=True, capture_output=True, check=True)

    GetModifiedFiles = f"git diff upstream/master {current_directory}/../../../Parsers/'*.yaml'"
    try:
        Changes = subprocess.run(GetModifiedFiles, shell=True, text=True, capture_output=True, check=True)
        return Changes.stdout
        #print(f"Changes: {Changes.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"::error::An error occurred while executing the command: {e}")
        sys.stdout.flush()  # Explicitly flush stdout

# Fetch the git diff
git_diff = get_git_diff()

# Setup logging
try:
    logging.basicConfig(
        level=logging.ERROR,
        format='%asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
except:
    logging.error('Failed to setup logging: ', exc_info=True)

# Obtain an access token
try:
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )
except:
        logging.error('Failed to obtain access token: ', exc_info=True)

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
    api_version="2024-05-01-preview",
)

try:
    completion = client.chat.completions.create(
        model="ASIM-gpt-4o",
        messages= [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people by writing and reviewing Microsoft Sentinel ASIM parsers. You can answer queries related to ASIM normalization."
        },
            {
                "role": "user",
                "content": f"Summarize the following Microsoft ASIM github PR changes: {git_diff}"
            },
            {
                "role": "user",
                "content": "Please perform a preliminary code review before the human review, flagging potential issues like syntax errors, inefficient code, or deviations from Sentinel/ASIM best practices and suggest improvements."
            }
    ],
        max_tokens=4096,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
except Exception as e:
    logging.error('Failed to get completion from OpenAI: ', exc_info=True)
    sys.exit(1)

# Assuming completion.model_dump_json() returns the response as a string, parse it
response = json.loads(completion.model_dump_json())

# Extract the actual content from the response
content = response['choices'][0]['message']['content']

# # Print the extracted content in a clean format
# print("\n---- Formatted Summary ----\n")
# print(f"Summary:\n{content.strip()}")

# Post the summary as a comment on the PR
github_api_url = f"https://api.github.com/repos/Azure/Azure-Sentinel/issues/{GITHUB_PR_NUMBER}/comments"
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
data = {"body": f"### AI-Generated PR Summary\n\n{content.strip()}"}

try:
    response = requests.post(github_api_url, headers=headers, json=data)
    if response.status_code == 201:
        print("Successfully posted PR summary comment.")
    else:
        logging.error(f"Failed to post comment: {response.status_code}, {response.text}")
except Exception as e:
    logging.error('Failed to post comment to GitHub: ', exc_info=True)