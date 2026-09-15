import json
from datetime import date

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import ShowEntry


@login_required(login_url='login')
def index(request):
    return render(request, "index.html")


def _json_error(message, status=403, extra=None):
    payload = {"error": message}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=status)


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
        "type": payload.get("type") or "movie",
        "title": (payload.get("title") or "").strip(),
        "year": _coerce_int(payload.get("year") or payload.get("productionYear")),
        "rating": _coerce_float(payload.get("rating")),
        "date_watched": _coerce_date(payload.get("dateWatched") or payload.get("date_watched")),
        "status": payload.get("status") or "completed",
        "ep_current": _coerce_int(payload.get("epCurrent") or payload.get("ep_current")),
        "ep_total": _coerce_int(payload.get("epTotal") or payload.get("ep_total")),
        "notes": (payload.get("notes") or "").strip(),
    }


def _validate_entry_payload(data):
    """Validate payload and return list of error messages."""
    errors = []
    if not data:
        return ["No data provided."]
    title = (data.get("title") or "").strip()
    if not title:
        errors.append("Title is required.")
    if len(title) > 255:
        errors.append("Title must be 255 characters or fewer.")
    entry_type = data.get("type") or "movie"
    if entry_type not in dict(ShowEntry.TYPE_CHOICES):
        errors.append(f"Invalid type: {entry_type}.")
    status = data.get("status") or "completed"
    if status not in dict(ShowEntry.STATUS_CHOICES):
        errors.append(f"Invalid status: {status}.")
    rating = data.get("rating")
    if rating is not None and rating != "":
        try:
            r = float(rating)
            if not (0 <= r <= 10):
                errors.append("Rating must be between 0 and 10.")
        except (TypeError, ValueError):
            errors.append("Rating must be a number.")
    year = data.get("year")
    if year is not None and year != "":
        try:
            y = int(year)
            if y < 0:
                errors.append("Year cannot be negative.")
        except (TypeError, ValueError):
            errors.append("Year must be a number.")
    return errors


@csrf_exempt
@require_http_methods(["GET", "POST"])
def entries_api(request):
    if not request.user.is_authenticated:
        return _json_error("Authentication required", status=401)

    if request.method == "GET":
        entries = ShowEntry.objects.filter(user=request.user)
        return JsonResponse([_serialize_entry(entry) for entry in entries], safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _json_error("Invalid JSON in request body.", status=400)

        validation_errors = _validate_entry_payload(payload)
        if validation_errors:
            return _json_error("Validation failed", status=400, extra={"details": validation_errors})

        try:
            entry = ShowEntry.objects.create(user=request.user, **_build_entry_kwargs(payload))
            return JsonResponse(_serialize_entry(entry), status=201)
        except ValidationError as exc:
            return _json_error("Validation error", status=400, extra={"details": exc.message_dict})
        except Exception as exc:
            return _json_error(str(exc), status=400)

    return _json_error("Method not allowed", status=405)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def entry_detail_api(request, pk):
    if not request.user.is_authenticated:
        return _json_error("Authentication required", status=401)

    entry = get_object_or_404(ShowEntry, pk=pk, user=request.user)

    if request.method == "GET":
        return JsonResponse(_serialize_entry(entry))

    if request.method == "PUT":
        try:
            payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _json_error("Invalid JSON in request body.", status=400)

        validation_errors = _validate_entry_payload(payload)
        if validation_errors:
            return _json_error("Validation failed", status=400, extra={"details": validation_errors})

        try:
            for field, value in _build_entry_kwargs(payload).items():
                setattr(entry, field, value)
            entry.full_clean()
            entry.save()
            return JsonResponse(_serialize_entry(entry))
        except ValidationError as exc:
            return _json_error("Validation error", status=400, extra={"details": exc.message_dict})
        except Exception as exc:
            return _json_error(str(exc), status=400)

    if request.method == "DELETE":
        entry.delete()
        return JsonResponse({"deleted": True})

    return _json_error("Method not allowed", status=405)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(request.POST.get('next') or 'index')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.POST.get('next') or request.GET.get('next') or 'index')
    else:
        form = AuthenticationForm()

    return render(request, 'log_in.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


def logout_view(request):
    logout(request)
    return redirect('login')