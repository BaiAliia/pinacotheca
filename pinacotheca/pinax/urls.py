from django.contrib import admin
from django.urls import path, include, re_path
from django.urls import path
from django.views.generic import TemplateView


app_name = 'pinax'

urlpatterns = [
    path('', TemplateView.as_view(template_name="painting/index.html")),
]
