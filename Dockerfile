FROM python:3.11 as base

EXPOSE  8000
RUN apt-get update && apt-get install -y git && apt-get clean
WORKDIR /app
COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

RUN git clone https://github.com/lmolkova/opentelemetry-python-contrib opentelemetry-python-contrib

WORKDIR /app/opentelemetry-python-contrib
RUN git checkout openai-update-semconv-to-latest
RUN pip install /app/opentelemetry-python-contrib/instrumentation/opentelemetry-instrumentation-openai-v2

WORKDIR /app

RUN git clone https://github.com/open-telemetry/opentelemetry-python opentelemetry-python

WORKDIR /app/opentelemetry-python
RUN git checkout main
RUN pip install /app/opentelemetry-python/opentelemetry-api
RUN pip install /app/opentelemetry-python/opentelemetry-semantic-conventions
RUN pip install /app/opentelemetry-python/opentelemetry-sdk

WORKDIR /app

RUN git clone https://github.com/lmolkova/azure-sdk-for-python azure-sdk-for-python

WORKDIR /app/azure-sdk-for-python
RUN git checkout azmon-exporter-complex_log_body
RUN pip install /app/azure-sdk-for-python/sdk/monitor/azure-monitor-opentelemetry-exporter

WORKDIR /app


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]