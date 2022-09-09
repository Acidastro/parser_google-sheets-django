from django.shortcuts import render
from django.views.generic import ListView

from .models import ParserListModel


class ParserListView(ListView):
    context_object_name = 'data'
    model = ParserListModel
    template_name = 'parser_app/index.html'