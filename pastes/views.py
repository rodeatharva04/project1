import json
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
from .models import Paste

def get_current_time(request):
    """Requirement: Deterministic time for testing."""
    test_now = request.headers.get('x-test-now-ms')
    if getattr(settings, 'TEST_MODE', False) and test_now:
        return timezone.make_aware(datetime.fromtimestamp(int(test_now) / 1000.0))
    return timezone.now()

def health_check(request):
    """Requirement: GET /api/healthz"""
    return JsonResponse({"ok": True})

@csrf_exempt
def create_paste(request):
    """Requirement: POST /api/pastes"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content')
            if not content or not isinstance(content, str):
                return JsonResponse({"error": "Content required"}, status=400)

            ttl = data.get('ttl_seconds')
            max_v = data.get('max_views')

            expires = None
            if isinstance(ttl, int) and ttl >= 1:
                expires = timezone.now() + timedelta(seconds=ttl)

            paste = Paste.objects.create(
                content=content,
                max_views=max_v if isinstance(max_v, int) and max_v >= 1 else None,
                expires_at=expires
            )

            url = f"{request.scheme}://{request.get_host()}/p/{paste.id}"
            return JsonResponse({"id": str(paste.id), "url": url}, status=201)
        except Exception:
            return JsonResponse({"error": "Invalid input"}, status=400)
    
    # Simple UI for creating pastes via browser
    return render(request, "pastes/index.html")

def fetch_paste_api(request, id):
    """Requirement: GET /api/pastes/:id"""
    paste = get_object_or_404(Paste, id=id)
    now = get_current_time(request)

    if paste.is_unavailable(now):
        return JsonResponse({"error": "Unavailable"}, status=404)

    paste.current_views += 1
    paste.save()

    remaining = None
    if paste.max_views:
        remaining = max(0, paste.max_views - paste.current_views)

    return JsonResponse({
        "content": paste.content,
        "remaining_views": remaining,
        "expires_at": paste.expires_at.isoformat().replace("+00:00", "Z") if paste.expires_at else None
    })

def fetch_paste_html(request, id):
    """Requirement: GET /p/:id (HTML)"""
    paste = get_object_or_404(Paste, id=id)
    now = get_current_time(request)

    if paste.is_unavailable(now):
        return HttpResponseNotFound("Paste is unavailable (expired or limit reached).")

    paste.current_views += 1
    paste.save()

    # Pre tag preserves formatting and Django escapes content safely by default
    return HttpResponse(f"<html><body><pre>{paste.content}</pre></body></html>")