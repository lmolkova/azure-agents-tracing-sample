from time import sleep
from chat.settings import MODEL, PROJECT_CLIENT

from azure.ai.projects.models import ToolSet, FunctionTool, CodeInterpreterTool, FileSearchTool
from opentelemetry.trace import get_current_span, SpanKind, get_tracer

#conn_list = project_client.connections.list()
#conn_id = ""
#for conn in conn_list:
#    if conn.connection_type == ConnectionType.AZURE_AI_SEARCH:
#        conn_id = conn.id
#        break

#ai_search = AzureAISearchTool(index_connection_id=conn_id, index_name="hotels-vector-quickstart")

def get_user_input():
    return "just some random input"

def get_user_location():
    return "Seattle, WA"

CODE_TOOLSET = ToolSet()
CODE_TOOLSET.add(CodeInterpreterTool())
CODE_TOOLSET.add(FunctionTool([get_user_input]))

tracer = get_tracer(__name__)
@tracer.start_as_current_span("execute_tool get_user_location")
def get_user_location():
    get_current_span().set_attribute("gen_ai.tool.name", "get_user_location")
    with tracer.start_as_current_span("get location", kind=SpanKind.CLIENT) as span:
        sleep(0.01)
    return "Seattle, WA"

@tracer.start_as_current_span("execute_tool get_user_input")
def get_user_input():
    get_current_span().set_attribute("gen_ai.tool.name", "get_user_input")
    return "just some random input"

def create_code_agent():
    agent = PROJECT_CLIENT.agents.create_agent(
        model=MODEL,
        name="code-agent",
        instructions="You are a friendly assistant that helps users write and execute code.",
        tools=CODE_TOOLSET.definitions,
        tool_resources=CODE_TOOLSET.resources,
        headers={"x-ms-enable-preview": "true"},
    )

    return agent

SEARCH_TOOLSET = ToolSet()
SEARCH_TOOLSET.add(FunctionTool([get_user_location]))

def create_file_search_agent():
    file = PROJECT_CLIENT.agents.upload_file_and_poll(file_path="hotels-small.json", purpose="assistants")
    vector_store = PROJECT_CLIENT.agents.create_vector_store_and_poll(file_ids=[file.id], name="vectorstore")
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    toolset = ToolSet()
    toolset.add(file_search)
    toolset.add(FunctionTool([get_user_location]))

    agent = PROJECT_CLIENT.agents.create_agent(
        model=MODEL,
        name="file-search-agent",
        instructions="You are a friendly assistant that helps users find hotels.",
        toolset=toolset,
    )

    return agent
