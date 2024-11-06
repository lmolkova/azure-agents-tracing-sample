#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
HTTPXClientInstrumentor().instrument()

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.metrics import get_meter_provider
from opentelemetry.trace import get_tracer_provider
from opentelemetry._logs import get_logger_provider
from opentelemetry._events import set_event_logger_provider
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor, ConsoleLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from azure.monitor.opentelemetry import configure_azure_monitor

def configure_tracing() -> TracerProvider:
    provider = get_tracer_provider()

    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    return provider


def configure_logging():
    provider = get_logger_provider()
    provider.add_log_record_processor(SimpleLogRecordProcessor(OTLPLogExporter()))
    provider.add_log_record_processor(SimpleLogRecordProcessor(ConsoleLogExporter()))
    event_provider = EventLoggerProvider()
    set_event_logger_provider(event_provider)
    return (provider, event_provider)

def configure_metrics() -> MeterProvider:
    provider = get_meter_provider()
    #provider.

    #MeterProvider(metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())])
    #metrics.set_meter_provider(provider)
    return provider

def main():
    configure_azure_monitor()
    configure_tracing()
    configure_logging()
    configure_metrics()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat.settings")
    DjangoInstrumentor().instrument()
    OpenAIInstrumentor().instrument()
    #AioHttpClientInstrumentor().instrument()
    #RequestsInstrumentor().instrument()

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
