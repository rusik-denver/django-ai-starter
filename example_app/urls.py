from django.urls import path

from . import views

app_name = "example_app"

urlpatterns = [
    path("", views.demo, name="demo"),
    path("api/submit/", views.submit_lead, name="submit"),
]
