from django.contrib import admin
from django.urls import path

from .views import ParserListView

urlpatterns = [
    path('', ParserListView.as_view()),
]
