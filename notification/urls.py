from django.urls import path
from .views import notification_page

urlpatterns = [
    path("notifications/", notification_page, name="notifications"),
]