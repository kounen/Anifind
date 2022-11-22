from django.urls import path

from .views import (
    UserListApiView,
)

urlpatterns = [
    path('api', UserListApiView.as_view()),
]