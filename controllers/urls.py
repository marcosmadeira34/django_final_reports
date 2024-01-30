from .views import *
from django.urls import path

urlpatterns = [
    path('', homepage, name='/homepage'),
    path('index/', index, name='index'),
    path('query/', query, name='query'),

]   