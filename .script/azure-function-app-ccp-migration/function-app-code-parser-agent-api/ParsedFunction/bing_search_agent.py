import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, BingGroundingTool
from azure.identity import DefaultAzureCredential
import json

# [START create_agent_with_bing_grounding_tool]
conn_id = os.environ["AZURE_BING_CONNECTION_ID"]

# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=conn_id)

def call_agent(system_context: str, user_query: str) -> dict:
    """
    Creates an Azure AI agent with the provided system context and user query.
    Returns a dict containing the agent's response text and any URL citations.
    """
    conn_id = os.environ["AZURE_BING_CONNECTION_ID"]
    bing = BingGroundingTool(connection_id=conn_id)
    uami_client_id = os.getenv("UAMI_CLIENT_ID")
    credential = DefaultAzureCredential(managed_identity_client_id=uami_client_id)
    # use a new AIProjectClient per invocation to keep the transport open
    local_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=credential,
    )
    with local_client:
        agents_client = local_client.agents
        # create agent with provided system instructions
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="ccp-agent",
            instructions=system_context,
            tools=bing.definitions,
            temperature=0.0
        )
        # start a new thread
        thread = agents_client.threads.create()
        # send user message
        agents_client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_query,
        )
        # process the agent run
        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        if run.status == "failed":
            raise RuntimeError(f"Agent run failed: {run.last_error}")
        # retrieve the agent's response
        response_message = agents_client.messages.get_last_message_by_role(
            thread_id=thread.id, role=MessageRole.AGENT
        )
        # extract text and citations
        texts = [msg.text.value for msg in response_message.text_messages] if response_message else []
        # skip URL citation annotations; citations are embedded in the agent's JSON output
        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        if not texts:
            raise ValueError("No response text found in agent output")
        
        # print escaped to avoid encoding errors
        data = json.loads(texts[0])

        print("Bing search results:", data)
        return data