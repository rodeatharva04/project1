import json
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import datetime, timedelta
from .models import Paste

def get_logic_now(request):
    """Handles deterministic time for bot testing."""
    if getattr(settings, 'TEST_MODE', False):
        test_now_ms = request.headers.get('x-test-now-ms')
        if test_now_ms:
            try:
                return timezone.make_aware(datetime.fromtimestamp(int(test_now_ms) / 1000.0))
            except: pass
    return timezone.now()

def healthz(request):
    """GET /api/healthz - Checks persistence"""
    try:
        # Check if we can hit the DB
        Paste.objects.exists()
        return JsonResponse({"ok": True})
    except Exception:
        return JsonResponse({"ok": False}, status=500)

@csrf_exempt
def create_paste(request):
    """POST /api/pastes - Strict Validation"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Content Validation
    content = data.get('content')
    if not isinstance(content, str) or not content:
        return JsonResponse({"error": "content is required and must be non-empty"}, status=400)

    # TTL Validation
    ttl_seconds = data.get('ttl_seconds')
    expires_at = None
    if ttl_seconds is not None:
        if not isinstance(ttl_seconds, int) or ttl_seconds < 1:
            return JsonResponse({"error": "ttl_seconds must be integer >= 1"}, status=400)
        expires_at = timezone.now() + timedelta(seconds=ttl_seconds)

    # Max Views Validation
    max_views = data.get('max_views')
    if max_views is not None:
        if not isinstance(max_views, int) or max_views < 1:
            return JsonResponse({"error": "max_views must be integer >= 1"}, status=400)

    paste = Paste.objects.create(content=content, max_views=max_views, expires_at=expires_at)
    
    # Absolute URL without hardcoding localhost
    url = request.build_absolute_uri(f'/p/{paste.id}')
    if not request.is_secure() and 'railway' in url:
        url = url.replace('http://', 'https://')

    return JsonResponse({"id": str(paste.id), "url": url}, status=201)

def fetch_paste_api(request, id):
    """GET /api/pastes/:id - Increments view counts"""
    now = get_logic_now(request)
    
    with transaction.atomic():
        try:
            paste = Paste.objects.select_for_update().get(pk=id)
        except:
            return JsonResponse({"error": "Not Found"}, status=404)

        if paste.is_unavailable(now):
            return JsonResponse({"error": "Unavailable"}, status=404)

        paste.current_views += 1
        paste.save()

    remaining = None
    if paste.max_views is not None:
        remaining = max(0, paste.max_views - paste.current_views)

    return JsonResponse({
        "content": paste.content,
        "remaining_views": remaining,
        "expires_at": paste.expires_at.isoformat().replace("+00:00", "Z") if paste.expires_at else None
    })

def fetch_paste_html(request, id):
    """GET /p/:id - HTML rendering"""
    now = get_logic_now(request)
    
    with transaction.atomic():
        try:
            paste = Paste.objects.select_for_update().get(pk=id)
        except:
            return HttpResponseNotFound("Not Found")

        if paste.is_unavailable(now):
            return HttpResponseNotFound("Unavailable")

        paste.current_views += 1
        paste.save()

    return render(request, 'pastes/view.html', {'content': paste.content})

def index(request):
    """UI for creating pastes"""
    return render(request, 'pastes/index.html')
