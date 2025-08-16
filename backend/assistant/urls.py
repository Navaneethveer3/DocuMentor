from django.urls import path
from .views import chat_with_document

urlpatterns = [
    path("chat", chat_with_document),
]
