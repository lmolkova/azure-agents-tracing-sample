import os
from pathlib import Path
from opentelemetry._events import get_event_logger
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-kl^t0c0l42fyt=usm+u(4j2e@v9@6gygw2n%dh%m3x#nr!1*(-"
DEBUG = True
ALLOWED_HOSTS = ['*']

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
   'markdownify',
]

MARKDOWNIFY = {
    'default': {
        'LINKIFY_TEXT': {
            'AUTOLINKS': False
        }
    }
}

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

MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
PROJECT_CLIENT = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
)

AZMON_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if not AZMON_CONNECTION_STRING:
    AZMON_CONNECTION_STRING = PROJECT_CLIENT.telemetry.get_connection_string()

EVENT_LOGGER = get_event_logger("chat", version="1.0.0")

AGENT_IDS = {
    "code-agent": None,
    "file-search-agent": None,
}