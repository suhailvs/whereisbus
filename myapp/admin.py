from django.contrib import admin

# Register your models here.
from .models import Stop,Bus,BusStop
admin.site.register(Stop)
admin.site.register(Bus)
admin.site.register(BusStop)