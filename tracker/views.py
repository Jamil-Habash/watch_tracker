import json
from datetime import date

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from .models import ShowEntry


def index(request):
    return render(request, "index.html")


def _serialize_entry(entry):
    return {
        "id": entry.id,
        "type": entry.type,
        "title": entry.title,
        "year": entry.year,
        "rating": entry.rating,
        "dateWatched": entry.date_watched.isoformat() if entry.date_watched else "",
        "status": entry.status,
        "epCurrent": entry.ep_current,
        "epTotal": entry.ep_total,
        "notes": entry.notes,
        "createdAt": int(entry.created_at.timestamp() * 1000) if entry.created_at else None,
    }


def _coerce_date(value):
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _coerce_int(value):
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value):
    if value in (None, "", "null"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_entry_kwargs(data):
    payload = data or {}
    return {
        "type": payload.get("type") or payload.get("type", "movie"),
        "title": (payload.get("title") or "").strip(),
        "year": _coerce_int(payload.get("year") or payload.get("productionYear")),
        "rating": _coerce_float(payload.get("rating")),
        "date_watched": _coerce_date(payload.get("dateWatched") or payload.get("date_watched")),
        "status": payload.get("status") or "completed",
        "ep_current": _coerce_int(payload.get("epCurrent") or payload.get("ep_current")),
        "ep_total": _coerce_int(payload.get("epTotal") or payload.get("ep_total")),
        "notes": (payload.get("notes") or "").strip(),
    }


@csrf_exempt
def entries_api(request):
    if request.method == "GET":
        entries = ShowEntry.objects.all()
        return JsonResponse([_serialize_entry(entry) for entry in entries], safe=False)

    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        entry = ShowEntry.objects.create(**_build_entry_kwargs(payload))
        return JsonResponse(_serialize_entry(entry), status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def entry_detail_api(request, pk):
    entry = get_object_or_404(ShowEntry, pk=pk)

    if request.method == "GET":
        return JsonResponse(_serialize_entry(entry))

    if request.method == "PUT":
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        for field, value in _build_entry_kwargs(payload).items():
            setattr(entry, field, value)
        entry.save()
        return JsonResponse(_serialize_entry(entry))

    if request.method == "DELETE":
        entry.delete()
        return JsonResponse({"deleted": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)