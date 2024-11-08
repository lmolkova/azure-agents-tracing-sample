#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
HTTPXClientInstrumentor().instrument()

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.trace import set_tracer_provider
from opentelemetry._logs import set_logger_provider
from opentelemetry._events import set_event_logger_provider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor, ConsoleLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter, AzureMonitorTraceExporter

def configure_tracing() -> TracerProvider:
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    #provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    provider.add_span_processor(SimpleSpanProcessor(AzureMonitorTraceExporter()))
    set_tracer_provider(provider)
    return provider


def configure_logging():
    provider = LoggerProvider()
    provider.add_log_record_processor(SimpleLogRecordProcessor(OTLPLogExporter()))
    #provider.add_log_record_processor(SimpleLogRecordProcessor(ConsoleLogExporter()))
    provider.add_log_record_processor(SimpleLogRecordProcessor(AzureMonitorLogExporter()))
    set_logger_provider(provider)

    event_provider = EventLoggerProvider(provider)

    set_event_logger_provider(event_provider)
    return (provider, event_provider)


def main():
    configure_tracing()
    configure_logging()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")
    DjangoInstrumentor().instrument()
    OpenAIInstrumentor().instrument()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
