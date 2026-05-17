import json

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Bus, BusStop, Stop


# ──────────────────────────────────────────────
#  Bus creation
# ──────────────────────────────────────────────

def _stops_for_json():
    stops = Stop.objects.order_by("name").values(
        "id", "name", "district", "landmark", "latitude", "longitude"
    )
    return [
        {
            **stop,
            "latitude": float(stop["latitude"]) if stop["latitude"] is not None else None,
            "longitude": float(stop["longitude"]) if stop["longitude"] is not None else None,
        }
        for stop in stops
    ]


def bus_create(request):
    """
    GET  – render the bus creation form.
    POST – validate and persist bus + ordered stop list.

    Expected POST body (application/x-www-form-urlencoded):
        bus_number   : str
        bus_type     : str
        is_active    : "on" | absent
        stops_json   : JSON array of stop objects
                       [{ stop_id, time, is_boarding, is_destination, order }, …]
    """
    if request.method == "POST":
        return _handle_bus_create(request)

    # Provide existing stops for the initial picker
    context = {
        "stops_json": json.dumps(_stops_for_json()),
        "bus_types": _BUS_TYPES,
    }
    return render(request, "bus/bus_form.html", context)


def _handle_bus_create(request):
    bus_number = request.POST.get("bus_number", "").strip()
    bus_type   = request.POST.get("bus_type", "").strip()
    is_active  = request.POST.get("is_active") == "on"
    stops_raw  = request.POST.get("stops_json", "[]")

    errors = []
    if not bus_number:
        errors.append("Bus number is required.")
    if not bus_type:
        errors.append("Bus type is required.")

    try:
        stops_data = json.loads(stops_raw)
    except json.JSONDecodeError:
        stops_data = []
        errors.append("Invalid stop data submitted.")

    if len(stops_data) < 2:
        errors.append("A bus route must have at least 2 stops.")

    if errors:
        for err in errors:
            messages.error(request, err)
        return render(request, "bus/bus_form.html", {
            "stops_json": json.dumps(_stops_for_json()),
            "bus_types": _BUS_TYPES,
            "form_data": {
                "bus_number": bus_number,
                "bus_type": bus_type,
                "is_active": is_active,
                "stops_json": stops_raw,
            },
        })

    with transaction.atomic():
        bus = Bus.objects.create(
            bus_number=bus_number,
            bus_type=bus_type,
            is_active=is_active,
        )
        bus_stops = []
        for item in stops_data:
            bus_stops.append(BusStop(
                bus=bus,
                stop_id=item["stop_id"],
                time=item["time"],
                is_boarding=item.get("is_boarding", False),
                is_destination=item.get("is_destination", False),
                order=item["order"],
                is_active=True,
            ))
        BusStop.objects.bulk_create(bus_stops)

    messages.success(request, f"Bus {bus_number} created successfully.")
    return redirect("bus_detail", pk=bus.pk)


# ──────────────────────────────────────────────
#  AJAX: stop search
# ──────────────────────────────────────────────

@require_GET
def stop_search_ajax(request):
    """
    GET /bus/stops/search/?q=<query>
    Returns JSON list of matching stops.
    """
    q = request.GET.get("q", "").strip()
    qs = Stop.objects.order_by("name")
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(district__icontains=q)
    stops = list(qs.values("id", "name", "district", "landmark", "latitude", "longitude")[:30])
    return JsonResponse({"stops": stops})


# ──────────────────────────────────────────────
#  AJAX: inline stop creation
# ──────────────────────────────────────────────

@require_POST
def stop_create_ajax(request):
    """
    POST /bus/stops/create/
    Body: JSON { name, district, landmark, latitude, longitude }
    Returns: JSON { id, name, district, landmark, latitude, longitude }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    name = data.get("name", "").strip()
    district = data.get("district", "").strip()

    if not name:
        return JsonResponse({"error": "Stop name is required."}, status=400)
    if not district:
        return JsonResponse({"error": "District is required."}, status=400)

    stop = Stop.objects.create(
        name=name,
        district=district,
        landmark=data.get("landmark", "").strip(),
        latitude=data.get("latitude") or None,
        longitude=data.get("longitude") or None,
    )
    return JsonResponse({
        "id":        stop.id,
        "name":      stop.name,
        "district":  stop.district,
        "landmark":  stop.landmark,
        "latitude":  float(stop.latitude)  if stop.latitude  else None,
        "longitude": float(stop.longitude) if stop.longitude else None,
    }, status=201)


# ──────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────

_BUS_TYPES = [
    "Ordinary",
    "Fast Passenger",
    "Super Fast",
    "Express",
    "Super Express",
    "AC Ordinary",
    "AC Express",
    "Limited Stop",
    "City Service",
    "Town Service",
]
