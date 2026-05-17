# views.py
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from .models import Bus, BusStop, Stop


def _bus_stops_prefetch():
    """Shared prefetch for bus stop details."""
    return Prefetch('bus_stops', queryset=BusStop.objects.select_related('stop'))


def _active_stops_qs():
    """Stops that actually have buses, for dropdowns."""
    return Stop.objects.filter(buses__isnull=False).distinct().order_by('name')


def _parse_stop_id(raw):
    """Return int stop id or None; never raises on bad input."""
    try:
        return int(raw) if raw else None
    except (ValueError, TypeError):
        return None


def bus_search(request):
    from_stop_id = _parse_stop_id(request.GET.get('from_stop'))
    to_stop_id = _parse_stop_id(request.GET.get('to_stop'))

    buses = Bus.objects.prefetch_related(_bus_stops_prefetch())

    if from_stop_id:
        buses = buses.filter(bus_stops__stop_id=from_stop_id)
    if to_stop_id:
        buses = buses.filter(bus_stops__stop_id=to_stop_id)

    buses = buses.distinct()

    # Filter by correct travel direction (from comes before to in stop order)
    if from_stop_id and to_stop_id and from_stop_id != to_stop_id:
        valid_ids = []
        for bus in buses:
            order_by_stop = {bs.stop_id: bs.order for bs in bus.bus_stops.all()}
            from_order = order_by_stop.get(from_stop_id)
            to_order = order_by_stop.get(to_stop_id)
            if from_order is not None and to_order is not None and from_order < to_order:
                valid_ids.append(bus.id)
        buses = Bus.objects.filter(id__in=valid_ids).prefetch_related(_bus_stops_prefetch())

    # Reuse already-fetched bus if possible, else fetch by id
    selected_bus = None
    bus_id = _parse_stop_id(request.GET.get('bus'))
    if bus_id:
        # Try to find in already-evaluated queryset to avoid extra query
        fetched = {b.id: b for b in buses} if buses._result_cache else {}
        selected_bus = fetched.get(bus_id) or get_object_or_404(
            Bus.objects.prefetch_related(_bus_stops_prefetch()), id=bus_id
        )

    context = {
        'buses': buses,
        'stops': _active_stops_qs(),
        'selected_bus': selected_bus,
        'selected_from_stop': from_stop_id,
        'selected_to_stop': to_stop_id,
    }
    return render(request, 'bus/search.html', context)


def bus_detail(request, pk):
    selected_bus = get_object_or_404(
        Bus.objects.prefetch_related(_bus_stops_prefetch()), id=pk
    )
    # Only fetch the full bus list if the template sidebar needs it
    buses = Bus.objects.prefetch_related(_bus_stops_prefetch())

    context = {
        'buses': buses,
        'stops': _active_stops_qs(),
        'selected_bus': selected_bus,
        'selected_from_stop': _parse_stop_id(request.GET.get('from_stop')),
        'selected_to_stop': _parse_stop_id(request.GET.get('to_stop')),
    }
    return render(request, 'bus/search.html', context)