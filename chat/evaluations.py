import json
import sys
import threading
import time

from opentelemetry._events import Event
from opentelemetry.trace import get_tracer, get_current_span, SpanContext
from promptflow.evals.evaluate import evaluate

tracer = get_tracer(__name__)

class EvaluationQueue:
    def __init__(self, relevance_evaluator, logger):
        self.queue = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._background_task)
        self.evaluation_in_progress = False
        self.thread.start()
        self.relevance_evaluator = relevance_evaluator
        self.logger = logger

    def evaluate(self, question: str, answer: str, context: str, metadata: dict):
        item = {"question": question, "answer": answer, "context": context, "metadata": metadata}

        with self.lock:
            self.queue.append(item)

    def _background_task(self):
        while not self.stop_event.is_set():
            time.sleep(10)
            if len(self.queue) > 0:
                self._run_evaluation()

    def stop(self):
        self.stop_event.set()
        sys.exit(0)

    @tracer.start_as_current_span("run_evaluation")
    def _run_evaluation(self):
        items = []
        with self.lock:
            items = self.queue.copy()
            self.queue.clear()
            if self.evaluation_in_progress:
                return
            self.evaluation_in_progress = True

        if not items:
            return

        span = get_current_span()

        with open("data.jsonl", "w") as f:
            for item in items:
                metadata = item["metadata"]
                span.add_link(SpanContext(trace_id=metadata["trace_id"],
                                        span_id=metadata["span_id"],
                                        is_remote=True,
                                        trace_flags=metadata["trace_flags"]))
                f.write(json.dumps({"question": item["question"], "answer": item["answer"], "context": item["context"]}) + "\n")

        results = evaluate(
            data="data.jsonl",
            evaluators={
                "relevance": self.relevance_evaluator,
            },
            _use_pf_client=False)

        for i, item in enumerate(items):
            metadata = item["metadata"]
            eval = results["rows"][i]

            if "outputs.relevance.gpt_relevance" in eval:
                score = eval["outputs.relevance.gpt_relevance"]
                self.logger.emit(Event("gen_ai.evaluation.relevance",
                                trace_id=metadata["trace_id"],
                                span_id=metadata["span_id"],
                                trace_flags=metadata["trace_flags"],
                                body=JsonBody({}),
                                attributes={
                                    "gen_ai.response.id": metadata["response_id"],
                                    "gen_ai.evaluation.score": score,
                                }))
        with self.lock:
            self.evaluation_in_progress = False

class JsonBody(dict):
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj = {}
        super().__init__(obj, **kwargs)

    def to_json(self):
        return json.dumps(self)

    def __str__(self):
        return self.to_json()