from django.urls import path,include
from accounts import urls as accounts_urls  


urlpatterns = [
    path("auth/", include(accounts_urls), name="accounts"),
]

