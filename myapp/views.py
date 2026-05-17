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


def _annotate_buses(buses):
    """
    Evaluate the queryset to a list and attach first_stop, last_stop,
    and stop_count as plain attributes so templates never call |first or
    |last on a QuerySet (which raises ValueError: Negative indexing is
    not supported).
    """
    bus_list = list(buses)
    for bus in bus_list:
        # bus_stops is already prefetched and ordered by `order`
        stops = list(bus.bus_stops.all())
        bus.first_stop = stops[0] if stops else None
        bus.last_stop  = stops[-1] if stops else None
        bus.stop_count = len(stops)
    return bus_list


def bus_search(request):
    from_stop_id = _parse_stop_id(request.GET.get('from_stop'))
    to_stop_id   = _parse_stop_id(request.GET.get('to_stop'))

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
            to_order   = order_by_stop.get(to_stop_id)
            if from_order is not None and to_order is not None and from_order < to_order:
                valid_ids.append(bus.id)
        buses = Bus.objects.filter(id__in=valid_ids).prefetch_related(_bus_stops_prefetch())

    # Evaluate to list and attach first_stop / last_stop / stop_count
    bus_list = _annotate_buses(buses)

    # Resolve selected bus from ?bus= param
    selected_bus = None
    bus_id = _parse_stop_id(request.GET.get('bus'))
    if bus_id:
        fetched = {b.id: b for b in bus_list}
        if bus_id in fetched:
            selected_bus = fetched[bus_id]
        else:
            raw = get_object_or_404(
                Bus.objects.prefetch_related(_bus_stops_prefetch()), id=bus_id
            )
            _annotate_buses([raw])   # attaches attributes in-place
            selected_bus = raw

    context = {
        'buses': bus_list,
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
    # Attach first_stop / last_stop / stop_count to selected bus
    _annotate_buses([selected_bus])

    # Sidebar list — annotated so bus cards render correctly
    bus_list = _annotate_buses(
        Bus.objects.prefetch_related(_bus_stops_prefetch())
    )

    context = {
        'buses': bus_list,
        'stops': _active_stops_qs(),
        'selected_bus': selected_bus,
        'selected_from_stop': _parse_stop_id(request.GET.get('from_stop')),
        'selected_to_stop':   _parse_stop_id(request.GET.get('to_stop')),
    }
    return render(request, 'bus/detail.html', context)