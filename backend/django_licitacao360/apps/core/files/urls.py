from django.urls import path
from . import views

app_name = "files"

urlpatterns = [
    path("serve/", views.serve_file, name="serve_file"),
]

