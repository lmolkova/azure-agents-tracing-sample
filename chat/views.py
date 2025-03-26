import json
from typing import Any
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from chat.settings import EVENT_LOGGER as logger, PROJECT_CLIENT as project, AGENT_IDS
from chat.create_agents import CODE_TOOLSET, FILE_SEARCH_TOOLSET, create_ai_search_agent, create_code_agent, create_file_search_agent
from opentelemetry.trace import get_current_span
from opentelemetry._events import Event
from opentelemetry.trace import get_tracer
from azure.ai.projects.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

tracer = get_tracer(__name__)

def index(request):
    return render(request, 'index.html')

def code_agent(request):
    return render(request, 'code_agent.html')

def file_search_agent(request):
    return render(request, 'file_search_agent.html')

def ai_search_agent(request):
    return render(request, 'ai_search_agent.html')

class MyEventHandler(AgentEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.last_message = None

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        pass

    def on_thread_message(self, message: "ThreadMessage") -> None:
        if len(message.content):
            self.last_message = message

    def on_thread_run(self, run: "ThreadRun") -> None:
        #if run.last_error:
        print(f"ThreadRun status: {run.status} {run.last_error}]")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep: {step}")
        pass

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        pass

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

def get_or_create_agent(name: str):
    agent_id = AGENT_IDS[name]
    if agent_id:
        return agent_id

    if not agent_id:
        agents = project.agents.list_agents(order="desc", limit=10)
        for agent in agents.data:
            print(f"Agent: {agent.name}, ID: {agent.id}")
            if agent.name == name:
                AGENT_IDS[name] = agent.id
                return agent.id
    if not agent_id:
        if name == "code-agent":
            agent = create_code_agent()
            AGENT_IDS[name] = agent.id
            return agent.id
        elif name == "file-search-agent":
            agent = create_file_search_agent()
            AGENT_IDS[name] = agent.id
            return agent.id
        elif name == "ai-search-agent":
            agent = create_ai_search_agent()
            AGENT_IDS[name] = agent.id
            return agent.id

    raise ValueError(f"Unknown agent name: {name}")

def get_toolset(name: str):
    if name == "code-agent":
        return CODE_TOOLSET
    elif name == "file-search-agent":
        return FILE_SEARCH_TOOLSET

    return None

@csrf_exempt
def results_page(request):
    query = request.POST.get('query')
    thread_id = request.POST.get('thread-id', None)
    agent_name = request.POST.get('agent-name', None)
    agent_id = get_or_create_agent(agent_name)
    response = run_agent(query, thread_id, agent_id, get_toolset(agent_name))

    return render(request, 'results_page.html', response)

def run_agent(query, thread_id, agent_id, toolset):
    if not thread_id:
        thread = project.agents.create_thread()
        thread_id = thread.id

    project.agents._toolset[agent_id] = toolset
    message = project.agents.create_message(
        thread_id=thread_id, role="user", content=query
    )

    event_handler=MyEventHandler()
    with project.agents.create_stream(thread_id=thread_id, agent_id=agent_id, event_handler=event_handler) as stream:
        stream.until_done()

    if event_handler.last_message:
        response_id = event_handler.last_message.id
        content = event_handler.last_message.content[0] if event_handler.last_message.content else None
    else:
        response_id = None
        content = None

    current_ctx = get_current_span().get_span_context()
    response = {}
    response["metadata"] = {
        "response_id": response_id,
        "trace_id": current_ctx.trace_id,
        "span_id": current_ctx.span_id,
        "trace_flags": current_ctx.trace_flags,
    }
    response["query"] = query
    response["thread_id"] = thread_id
    response["completion"] = content

    return response

@csrf_exempt
def feedback_page(request):
    (score, response_id) = _record_feedback(request.POST.get('feedback'),
                    request.POST.get('response_id'),
                    int(request.POST.get('trace_id', 0)),
                    int(request.POST.get('span_id', 0)))

    return HttpResponse(f"Feedback received: score = {score}, response_id = {response_id}")

def _record_feedback(feedback, response_id, trace_id, span_id):
    score = None
    if (feedback == '+1'):
        score = 1.0
    elif (feedback == '-1'):
        score = -1.0

    logger.emit(Event("gen_ai.evaluation.user_feedback",
                        span_id=span_id,
                        trace_id=trace_id,
                        body={"comment": "something users might provide"},
                        attributes={"gen_ai.response.id": response_id,
                                    "gen_ai.evaluation.score": score}))

    return (score, response_id)