from .views import *
from django.urls import path
from app_authentication.views import login_view

urlpatterns = [
    path('', login_view, name='homepage'),
    path('index/', index, name='index'),
    path('query/', query_result, name='query'),

]   


