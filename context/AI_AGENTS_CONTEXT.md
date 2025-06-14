# Strands SDK

Python Strands SDK is installed using:
`uv pip install strands-agents strands-agents-tools`

Here is an example Strands SDK starting code:

```python
import boto3
import os

from botocore.config import Config
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import agent_graph, batch, calculator, current_time, cron, \
    editor, file_read, file_write, \
    http_request, journal, python_repl, retrieve, shell, \
    speak, stop, swarm, think, use_aws, use_llm, workflow
# Where tools and descriptions can be found here: https://github.com/strands-agents/tools

# Bedrock cross-region inference profiles from https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html
BEDROCK_MODELS = [
    'us.amazon.nova-micro-v1:0',
    'us.amazon.nova-lite-v1:0',
    'us.amazon.nova-pro-v1:0',
    'us.anthropic.claude-3-5-haiku-20241022-v1:0',
    'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    'us.anthropic.claude-3-7-sonnet-20250219-v1:0',
    'us.anthropic.claude-sonnet-4-20250514-v1:0',
]
SYSTEM_PROMPT = "You are a helpful assistant."

# Load AWS Credentials from the environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', None)
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-lite-v1:0')

if AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN:
    session = boto3.Session(
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        aws_session_token = AWS_SESSION_TOKEN,
        region_name = AWS_DEFAULT_REGION
        # profile_name = 'your-profile'
    )
else:
    session = boto3.Session()

@tool
def token_count(text: str) -> int:
    """Approximates tokens in a text string.using word count (1 token ≈ 0.75 words)
    This docstring is used by the LLM to understand the tool's purpose.
    """
    return int(len(text.split()) * 1.33)

model = BedrockModel(
    model_id = BEDROCK_MODEL_ID,
    max_tokens = 2048,
    boto_client_config = Config(
        read_timeout = 120,
        connect_timeout = 120,
        retries = dict(max_attempts=3, mode="adaptive"),
    ),
    boto_session=session
)

agent = Agent(
    model = model,
    system_prompt = SYSTEM_PROMPT,
    tools = [word_count, calculator]
)
EXAMPLE_PROMPTS = [
    "How many words are in this sentence?",
    "What is the square root of 1764"
]
prompt = EXAMPLE_PROMPTS[0]
response = agent(prompt)
```


# FastMCP v2 MCP Servers

Fast MCP can be installed using `uv pip install fastmcp`

An example MCP server, `mcp-server.py`, would look like the following:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="My Math MCP Server 🚀")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

# Static resource
@mcp.resource("config://version")
def get_version(): 
    return "1.0"

# Dynamic resource template
@mcp.resource("users://{user_id}/profile")
def get_profile(user_id: int):
    # Fetch profile for user_id...
    return {"name": f"User {user_id}", "status": "active"}

# Prompt template (reusable message templates to guide LLM interactions) 
@mcp.prompt()
def summarize_request(text: str) -> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\n\n{text}"

if __name__ == "__main__":
    mcp.run()
```

An example MCP client, `mcp-client.py`, using FastMCP v2, would look like the following:

```python
from fastmcp import Client

async def main():
    # Connect via stdio to a local script
    async with Client("mcp-server.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.text}")

    # Connect via SSE
    async with Client("http://localhost:8000/sse") as client:
        # ... use the client
        pass
```
