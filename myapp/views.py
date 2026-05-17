# views.py

from django.shortcuts import render, get_object_or_404
from .models import Bus, Stop


def bus_search(request):

    buses = Bus.objects.all()
    stops = Stop.objects.all()

    selected_bus = None

    bus_id = request.GET.get('bus')

    if bus_id:
        selected_bus = get_object_or_404(Bus, id=bus_id)

    context = {
        'buses': buses,
        'stops': stops,
        'selected_bus': selected_bus
    }

    return render(request, 'bus/search.html', context)


def bus_detail(request, pk):

    buses = Bus.objects.all()
    stops = Stop.objects.all()

    selected_bus = get_object_or_404(Bus, id=pk)

    context = {
        'buses': buses,
        'stops': stops,
        'selected_bus': selected_bus
    }

    return render(request, 'bus/search.html', context)