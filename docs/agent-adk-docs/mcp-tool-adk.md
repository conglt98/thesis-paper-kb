What is Model Context Protocol (MCP)?¶
The Model Context Protocol (MCP) is an open standard designed to standardize how Large Language Models (LLMs) like Gemini and Claude communicate with external applications, data sources, and tools. Think of it as a universal connection mechanism that simplifies how LLMs obtain context, execute actions, and interact with various systems.

MCP follows a client-server architecture, defining how data (resources), interactive templates (prompts), and actionable functions (tools) are exposed by an MCP server and consumed by an MCP client (which could be an LLM host application or an AI agent).

This guide covers two primary integration patterns:

Using Existing MCP Servers within ADK: An ADK agent acts as an MCP client, leveraging tools provided by external MCP servers.
Exposing ADK Tools via an MCP Server: Building an MCP server that wraps ADK tools, making them accessible to any MCP client.
Prerequisites¶
Before you begin, ensure you have the following set up:

Set up ADK: Follow the standard ADK [setup]() instructions in the quickstart.
Install/update Python: MCP requires Python version of 3.9 or higher.
Setup Node.js and npx: Many community MCP servers are distributed as Node.js packages and run using npx. Install Node.js (which includes npx) if you haven't already. For details, see https://nodejs.org/en.
Verify Installations: Confirm adk and npx are in your PATH within the activated virtual environment:

# Both commands should print the path to the executables.
which adk
which npx
1. Using MCP servers with ADK agents (ADK as an MCP client) in adk web¶
This section shows two examples of using MCP servers with ADK agents. This is the most common integration pattern. Your ADK agent needs to use functionality provided by an existing service that exposes itself as an MCP Server.

MCPToolset class¶
The examples use the MCPToolset class in ADK which acts as the bridge to the MCP server. Your ADK agent uses MCPToolset to:

Connect: Establish a connection to an MCP server process. This can be a local server communicating over standard input/output (StdioServerParameters) or a remote server using Server-Sent Events (SseServerParams).
Discover: Query the MCP server for its available tools (list_tools MCP method).
Adapt: Convert the MCP tool schemas into ADK-compatible BaseTool instances.
Expose: Present these adapted tools to the ADK LlmAgent.
Proxy Calls: When the LlmAgent decides to use one of these tools, MCPToolset forwards the call (call_tool MCP method) to the MCP server and returns the result.
Manage Connection: Handle the lifecycle of the connection to the MCP server process, often requiring explicit cleanup.
These examples assumes you interact with MCP Tools with adk web. If you are not using adk web, see "Using MCP Tools in your own Agent out of adk web" section below.

Note: Using MCP tool requires a slightly different syntax to export the agent containing MCP Tools. A simpler interface for using MCP in ADK is currently in progress.

Example 1: File System MCP Server¶
This example demonstrates connecting to a local MCP server that provides file system operations.

Step 1: Attach the MCP Server to your ADK agent via MCPToolset¶
Create agent.py in ./adk_agent_samples/mcp_agent/ and use the following code snippet to define a function that initializes the MCPToolset.

Important: Replace "/path/to/your/folder" with the absolute path to an actual folder on your system.

# ./adk_agent_samples/mcp_agent/agent.py
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


async def create_agent():
  """Gets tools from MCP Server."""
  tools, exit_stack = await MCPToolset.from_server(
      connection_params=StdioServerParameters(
          command='npx',
          args=["-y",    # Arguments for the command
            "@modelcontextprotocol/server-filesystem",
            # TODO: IMPORTANT! Change the path below to an ABSOLUTE path on your system.
            "/path/to/your/folder",
          ],
      )
  )

  agent = LlmAgent(
      model='gemini-2.0-flash',
      name='enterprise_assistant',
      instruction=(
          'Help user accessing their file systems'
      ),
      tools=tools,
  )
  return agent, exit_stack


root_agent = create_agent()
If there are multiple MCP Servers, create a common exit stack and apply it to all MCPToolsets


# agent.py
from contextlib import AsyncExitStack
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams


async def create_agent():
  """Gets tools from MCP Server."""
  common_exit_stack = AsyncExitStack()

  local_tools, _ = await MCPToolset.from_server(
      connection_params=StdioServerParameters(
          command='npx',
          args=["-y",    # Arguments for the command
            "@modelcontextprotocol/server-filesystem",
            # TODO: IMPORTANT! Change the path below to an ABSOLUTE path on your system.
            "/path/to/your/folder",
          ],
      ),
      async_exit_stack=common_exit_stack
  )

  remote_tools, _ = await MCPToolset.from_server(
      connection_params=SseServerParams(
          # TODO: IMPORTANT! Change the path below to your remote MCP Server path
          url="https://your-mcp-server-url.com/sse"
      ),
      async_exit_stack=common_exit_stack
  )


  agent = LlmAgent(
      model='gemini-2.0-flash',
      name='enterprise_assistant',
      instruction=(
          'Help user accessing their file systems'
      ),
      tools=[
        *local_tools,
        *remote_tools,
      ],
  )
  return agent, common_exit_stack


root_agent = create_agent()
Step 2: Create an init file¶
Create an __init__.py in the same folder as the agent.py above


# ./adk_agent_samples/mcp_agent/__init__.py
from . import agent
Step 3: Observe the result¶
Run adk web from the adk_agent_samples directory (ensure your virtual environment is active):


cd ./adk_agent_samples
adk web
A successfully MCPTool interaction will yield a response by accessing your local file system, like below:

Example 2: Google Maps MCP Server¶
This follows the same pattern but targets the Google Maps MCP server.

Step 1: Get API Key and Enable APIs¶
Follow the directions at Use API keys to get a Google Maps API Key.

Enable Directions API and Routes API in your Google Cloud project. For instructions, see Getting started with Google Maps Platform topic.

Step 2: Update create_agent¶
Modify create_agent in agent.py to connect to the Maps server, passing your API key via the env parameter of StdioServerParameters.


# agent.py (modify get_tools_async and other parts as needed)

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


async def create_agent():
  """Gets tools from MCP Server."""

  tools, exit_stack = await MCPToolset.from_server(
      connection_params=StdioServerParameters(
          command='npx',
          args=["-y",
                "@modelcontextprotocol/server-google-maps",
          ],
          # Pass the API key as an environment variable to the npx process
          env={
              "GOOGLE_MAPS_API_KEY": google_maps_api_key
          }
      )
  )

  agent = LlmAgent(
      model='gemini-2.0-flash', # Adjust if needed
      name='maps_assistant',
      instruction='Help user with mapping and directions using available tools.',
      tools=tools,
  )
  return agent, exit_stack


root_agent = create_agent()
Step 3: Create an init file¶
If you have already finished this from Example 1 above, skip this step.

Create an __init__.py in the same folder as the agent.py above


# ./adk_agent_samples/mcp_agent/__init__.py
from . import agent
Step 4: Observe the Result¶
Run adk web from the adk_agent_samples directory (ensure your virtual environment is active):


cd ./adk_agent_samples
adk web
A successfully MCPTool interaction will yield a response with a route plan, like below:

Using MCP Tools in your own Agent out of adk web¶
This section is relevant to you if:

You are developing your own Agent using ADK
And, you are NOT using adk web,
And, you are exposing the agent via your own UI
Using MCP Tools requires a different setup than using regular tools, due to the fact that specs for MCP Tools are fetched asynchronously from the MCP Server running remotely, or in another process.

The following example is modified from the "Example 1: File System MCP Server" example above. The main differences are:

Your tool and agent are created asynchronously
You need to properly manage the exit stack, so that your agents and tools are destructed properly when the connection to MCP Server is closed.

# agent.py (modify get_tools_async and other parts as needed)
# ./adk_agent_samples/mcp_agent/agent.py
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters

# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys
load_dotenv('../.env')

# --- Step 1: Agent Definition ---
async def get_agent_async():
  """Creates an ADK Agent equipped with tools from the MCP Server."""
  tools, exit_stack = await MCPToolset.from_server(
      # Use StdioServerParameters for local process communication
      connection_params=StdioServerParameters(
          command='npx', # Command to run the server
          args=["-y",    # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                # TODO: IMPORTANT! Change the path below to an ABSOLUTE path on your system.
                "/path/to/your/folder"],
      )
      # For remote servers, you would use SseServerParams instead:
      # connection_params=SseServerParams(url="http://remote-server:port/path", headers={...})
  )
  print(f"Fetched {len(tools)} tools from MCP server.")
  root_agent = LlmAgent(
      model='gemini-2.0-flash', # Adjust model name if needed based on availability
      name='filesystem_assistant',
      instruction='Help user interact with the local filesystem using available tools.',
      tools=tools, # Provide the MCP tools to the ADK agent
  )
  return root_agent, exit_stack

# --- Step 2: Main Execution Logic ---
async def async_main():
  session_service = InMemorySessionService()
  # Artifact service might not be needed for this example
  artifacts_service = InMemoryArtifactService()

  session = session_service.create_session(
      state={}, app_name='mcp_filesystem_app', user_id='user_fs'
  )

  # TODO: Change the query to be relevant to YOUR specified folder.
  # e.g., "list files in the 'documents' subfolder" or "read the file 'notes.txt'"
  query = "list files in the tests folder"
  print(f"User Query: '{query}'")
  content = types.Content(role='user', parts=[types.Part(text=query)])

  root_agent, exit_stack = await get_agent_async()

  runner = Runner(
      app_name='mcp_filesystem_app',
      agent=root_agent,
      artifact_service=artifacts_service, # Optional
      session_service=session_service,
  )

  print("Running agent...")
  events_async = runner.run_async(
      session_id=session.id, user_id=session.user_id, new_message=content
  )

  async for event in events_async:
    print(f"Event received: {event}")

  # Crucial Cleanup: Ensure the MCP server process connection is closed.
  print("Closing MCP server connection...")
  await exit_stack.aclose()
  print("Cleanup complete.")

if __name__ == '__main__':
  try:
    asyncio.run(async_main())
  except Exception as e:
    print(f"An error occurred: {e}")
Key considerations¶
When working with MCP and ADK, keep these points in mind:

Protocol vs. Library: MCP is a protocol specification, defining communication rules. ADK is a Python library/framework for building agents. MCPToolset bridges these by implementing the client side of the MCP protocol within the ADK framework. Conversely, building an MCP server in Python requires using the model-context-protocol library.

ADK Tools vs. MCP Tools:

ADK Tools (BaseTool, FunctionTool, AgentTool, etc.) are Python objects designed for direct use within the ADK's LlmAgent and Runner.
MCP Tools are capabilities exposed by an MCP Server according to the protocol's schema. MCPToolset makes these look like ADK tools to an LlmAgent.
Langchain/CrewAI Tools are specific implementations within those libraries, often simple functions or classes, lacking the server/protocol structure of MCP. ADK offers wrappers (LangchainTool, CrewaiTool) for some interoperability.
Asynchronous nature: Both ADK and the MCP Python library are heavily based on the asyncio Python library. Tool implementations and server handlers should generally be async functions.

Stateful sessions (MCP): MCP establishes stateful, persistent connections between a client and server instance. This differs from typical stateless REST APIs.

Deployment: This statefulness can pose challenges for scaling and deployment, especially for remote servers handling many users. The original MCP design often assumed client and server were co-located. Managing these persistent connections requires careful infrastructure considerations (e.g., load balancing, session affinity).
ADK MCPToolset: Manages this connection lifecycle. The exit_stack pattern shown in the examples is crucial for ensuring the connection (and potentially the server process) is properly terminated when the ADK agent finishes.
