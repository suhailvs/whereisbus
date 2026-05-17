from django.urls import path
from django.contrib import admin
from myapp.views import bus_search, bus_detail
from myapp.user_views import bus_create, stop_search_ajax, stop_create_ajax
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bus_search, name='bus_search'),
    path('bus/<int:pk>/', bus_detail, name='bus_detail'),

    path("create/",               bus_create,         name="bus_create"),
    path("stops/search/",         stop_search_ajax,   name="stop_search_ajax"),
    path("stops/create/",         stop_create_ajax,   name="stop_create_ajax"),

]