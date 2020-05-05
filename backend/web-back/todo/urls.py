# todo/urls.py
from django.urls import path, include
from .views import ListTodo, DetailTodo, health_check

urlpatterns = [
    path('<int:pk>/', DetailTodo.as_view()),
    path('', ListTodo.as_view()),
    path('healthz', health_check, name="healthz")
]
