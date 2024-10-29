import os
from pathlib import Path
from opentelemetry._events import get_event_logger
from promptflow.core import AzureOpenAIModelConfiguration
#from promptflow.evals.evaluate import evaluate
from promptflow.evals.evaluators import RelevanceEvaluator
from openai import AzureOpenAI
import signal

from chat.evaluations import EvaluationQueue

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-kl^t0c0l42fyt=usm+u(4j2e@v9@6gygw2n%dh%m3x#nr!1*(-"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chat.urls"

INSTALLED_APPS = [
   'chat',
]

SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "chat.wsgi.application"

MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
OPENAI_CLIENT = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

_evaluator = RelevanceEvaluator(model_config=AzureOpenAIModelConfiguration(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview",
    azure_deployment=MODEL,
))
EVENT_LOGGER = get_event_logger("chat", version="1.0.0")

#EVALUATION_QUEUE = EvaluationQueue(_evaluator, EVENT_LOGGER)

#def quit(*args):
#    EVALUATION_QUEUE.stop()

#signal.signal(signal.SIGINT, quit)
