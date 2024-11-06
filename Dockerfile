FROM python:3.11

EXPOSE  8000
RUN apt-get update && apt-get install -y git && apt-get clean
WORKDIR /app
COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt

RUN git clone https://github.com/open-telemetry/opentelemetry-python-contrib opentelemetry-python-contrib

WORKDIR /app/opentelemetry-python-contrib
RUN git checkout main
RUN pip install /app/opentelemetry-python-contrib/instrumentation-genai/opentelemetry-instrumentation-openai-v2

WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]