from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("code_agent", views.code_agent, name="code_agent"),
    path("code_agent_page", views.results_page, name="results_page"),

    path("file_search_agent", views.file_search_agent, name="file_search_agent"),
    path("file_search_agent_page", views.results_page, name="results_page"),

    path("ai_search_agent", views.ai_search_agent, name="ai_search_agent"),
    path("ai_search_agent_page", views.results_page, name="results_page"),

    path("feedback_page", views.feedback_page, name="feedback_page")
]
