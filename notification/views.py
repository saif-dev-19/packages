from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def notification_page(request):
    return render(request, "notification/notifications.html")