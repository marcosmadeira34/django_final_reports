from django.shortcuts import render
from django.contrib.auth.models import User
from .models import *


def homepage(request):
    return render(request, 'homepage.html')


def index(request):
    return render(request, 'index.html')


def query(request):
    return render(request, 'database_query.html')


def query_result(request):
    user = User.objects.get(username=request.user)
    data = Database.objects.filter(user=user)
    context = {'database_data': data}
    return render(request, 'database_query.html', context)