import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Initialize Azure OpenAI client with Entra ID authentication
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
    api_version="2024-05-01-preview",
)

# Get the PR diff from the environment
pr_diff = os.getenv("PR_DIFF")

completion = client.chat.completions.create(
    model="GPT-4o",  # Replace with your deployment model
    messages= [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people by writing and reviewing Microsoft Sentinel ASIM parsers. You can answer queries related to ASIM normalization."
        },
        {
            "role": "user",
            "content": f"Summarize the following PR changes: {pr_diff}"
        }
    ],
    max_tokens=4096,
    temperature=0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    extra_body={
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": os.environ["AZURE_AI_SEARCH_ENDPOINT"],
                    "index_name": os.environ["AZURE_AI_SEARCH_INDEX"],
                    "authentication": {
                        "type": "azure_ad"
                    }
                }
            }
        ]
    }
)

# Print the result to the console
result = completion.model_dump_json(indent=2)
print("PR Summary:\n", result)
