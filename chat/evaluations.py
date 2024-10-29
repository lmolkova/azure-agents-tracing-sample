import json
import sys
import threading
import time

from opentelemetry._events import Event
from opentelemetry.trace import get_tracer, get_current_span, SpanContext
#from promptflow.evals.evaluate import evaluate

tracer = get_tracer(__name__)

class EvaluationQueue:
    def __init__(self, relevance_evaluator, logger):
        self.queue = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        #self.thread = threading.Thread(target=self._background_task)
        self.evaluation_in_progress = False
        #self.thread.start()
        self.relevance_evaluator = relevance_evaluator
        self.logger = logger

    def evaluate(self, question: str, answer: str, context: str, metadata: dict):
        item = {"question": question, "answer": answer, "context": context, "metadata": metadata}

        with self.lock:
            self.queue.append(item)

    def _background_task(self):
        #while not self.stop_event.is_set():
            #time.sleep(10)
        #    if len(self.queue) > 0:
        #        self._run_evaluation()
        pass

    def stop(self):
        self.stop_event.set()
        #sys.exit(0)

    @tracer.start_as_current_span("run_evaluation")
    def _run_evaluation(self):
        pass
class JsonBody(dict):
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj = {}
        super().__init__(obj, **kwargs)

    def to_json(self):
        return json.dumps(self)

    def __str__(self):
        return self.to_json()