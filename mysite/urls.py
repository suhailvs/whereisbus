from django.urls import path
from myapp.views import bus_search, bus_detail

urlpatterns = [
    path('', bus_search, name='bus_search'),
    path('bus/<int:pk>/', bus_detail, name='bus_detail'),
]