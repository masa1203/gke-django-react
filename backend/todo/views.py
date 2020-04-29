# todos/views.py

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import Todo
from .serializers import TodoSerializer

def health_check(request):
    response = HttpResponse(status=200)
    return response

class ListTodo(generics.ListAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer


class DetailTodo(generics.RetrieveAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
