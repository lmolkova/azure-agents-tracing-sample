from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from chat.settings import MODEL, OPENAI_CLIENT as openai
from chat.settings import EVENT_LOGGER as logger
from opentelemetry.trace import get_current_span
from opentelemetry._events import Event
from chat.settings import EVALUATION_QUEUE as evaluation_queue

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def chat_page(request):
    prompt = request.POST.get('prompt')
    response = _chat(prompt)
    response["prompt"] = prompt
    return render(request, 'chat_page.html', response)

def chat(request):
    prompt = request.GET.get('prompt')
    return JsonResponse(_chat(prompt))

def _chat(prompt):
    completion = openai.chat.completions.create(
        model=MODEL,
        max_tokens=100,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    current_ctx = get_current_span().get_span_context()
    metadata = {"response_id": completion.id,
                "trace_id": current_ctx.trace_id,
                "span_id": current_ctx.span_id,
                "trace_flags": current_ctx.trace_flags}
    content = {"completion": completion.choices[0].message.content, "metadata": metadata}

    evaluation_queue.evaluate(question=prompt, answer=completion.choices[0].message.content, context="no context", metadata=metadata)

    return content

@csrf_exempt
def feedback_page(request):
    (score, response_id) = _record_feedback(request.POST.get('feedback'),
                    request.POST.get('response_id'),
                    int(request.POST.get('trace_id', 0)),
                    int(request.POST.get('span_id', 0)))

    return HttpResponse(f"Feedback received: score = {score}, response_id = {response_id}")

@csrf_exempt
def feedback(request):
    (score, response_id) = _record_feedback(request.GET.get('feedback'),
                    request.GET.get('response_id'),
                    int(request.GET.get('trace_id', 0)),
                    int(request.GET.get('span_id', 0)))

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
                        body={"comment": "some user feedback"},
                        attributes={"gen_ai.response.id": response_id,
                                    "gen_ai.evaluation.score": score}))

    return (score, response_id)
