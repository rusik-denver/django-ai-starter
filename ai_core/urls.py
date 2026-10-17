from django.urls import path

from . import views

app_name = "ai_core"

urlpatterns = [
    path("score/", views.score_lead_view, name="score"),
    path("summarize/", views.summarize_view, name="summarize"),
    path("classify/", views.classify_view, name="classify"),
    path("draft-email/", views.draft_email_view, name="draft_email"),
]
