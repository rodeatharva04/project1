import json
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from datetime import datetime, timedelta
from .models import Paste

def get_current_time(request):
    test_now = request.headers.get('x-test-now-ms')
    if getattr(settings, 'TEST_MODE', False) and test_now:
        try:
            ts = int(test_now)
            return datetime.fromtimestamp(ts / 1000.0, timezone.utc)
        except (ValueError, OSError, OverflowError):
            pass
    return timezone.now()

def health_check(request):
    try:
        Paste.objects.first()
        return JsonResponse({"ok": True})
    except Exception:
        return JsonResponse({"ok": False}, status=200)

@csrf_exempt
def create_paste(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content')
            if not content or not isinstance(content, str):
                return JsonResponse({"error": "Content required"}, status=400)

            ttl = data.get('ttl_seconds')
            max_v = data.get('max_views')

            if ttl is not None and (not isinstance(ttl, int) or ttl < 1):
                 return JsonResponse({"error": "ttl_seconds must be a positive integer"}, status=400)
            
            if max_v is not None and (not isinstance(max_v, int) or max_v < 1):
                 return JsonResponse({"error": "max_views must be a positive integer"}, status=400)

            expires = None
            if ttl:
                expires = timezone.now() + timedelta(seconds=ttl)

            paste = Paste.objects.create(
                content=content,
                max_views=max_v,
                expires_at=expires
            )

            url = f"{request.scheme}://{request.get_host()}/p/{paste.id}"
            return JsonResponse({"id": str(paste.id), "url": url}, status=201)
        except Exception:
            return JsonResponse({"error": "Invalid input"}, status=400)
    
    return render(request, "pastes/index.html")

def fetch_paste_api(request, id):
    now = get_current_time(request)

    with transaction.atomic():
        try:
            paste = Paste.objects.select_for_update().get(id=id)
        except Paste.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)

        if paste.is_unavailable(now):
            return JsonResponse({"error": "Not found"}, status=404)

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

from django.utils.html import escape

def fetch_paste_html(request, id):
    now = get_current_time(request)

    with transaction.atomic():
        try:
            paste = Paste.objects.select_for_update().get(id=id)
        except Paste.DoesNotExist:
            return HttpResponseNotFound("Paste not found")

        if paste.is_unavailable(now):
            return HttpResponseNotFound("Not Found")

        paste.current_views += 1
        paste.save()

        return HttpResponse(f"<html><body><pre>{escape(paste.content)}</pre></body></html>")