import json
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from datetime import datetime, timedelta
from .models import Paste

def get_logic_now(request):
    if getattr(settings, 'TEST_MODE', False):
        test_now_ms = request.headers.get('x-test-now-ms')
        if test_now_ms:
            try:
                dt = datetime.fromtimestamp(int(test_now_ms) / 1000.0)
                return timezone.make_aware(dt)
            except ValueError:
                pass
    return timezone.now()

def healthz(request):
    try:
        Paste.objects.exists() 
        return JsonResponse({"ok": True}, status=200)
    except Exception:
        return JsonResponse({"ok": False}, status=500)

@csrf_exempt
def create_paste(request):
    if request.method == 'GET':
        # This looks for templates/pastes/index.html
        return render(request, 'pastes/index.html')

    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    content = data.get('content')
    if not isinstance(content, str) or not content:
        return JsonResponse({"error": "content is required and must be non-empty string"}, status=400)

    ttl = data.get('ttl_seconds')
    expires_at = None
    if ttl is not None:
        if not isinstance(ttl, int) or ttl < 1:
            return JsonResponse({"error": "ttl_seconds must be integer >= 1"}, status=400)
        expires_at = timezone.now() + timedelta(seconds=ttl)

    max_v = data.get('max_views')
    if max_v is not None:
        if not isinstance(max_v, int) or max_v < 1:
            return JsonResponse({"error": "max_views must be integer >= 1"}, status=400)

    paste = Paste.objects.create(content=content, max_views=max_v, expires_at=expires_at)

    url = request.build_absolute_uri(f'/p/{paste.id}')
    if 'railway' in url or 'vercel' in url:
        url = url.replace('http://', 'https://')
    
    return JsonResponse({"id": str(paste.id), "url": url}, status=201)

def fetch_api(request, id):
    now = get_logic_now(request)
    with transaction.atomic():
        try:
            paste = Paste.objects.select_for_update().get(pk=id)
        except Paste.DoesNotExist:
            return JsonResponse({"error": "Not Found"}, status=404)

        if paste.is_unavailable(now):
            return JsonResponse({"error": "Unavailable"}, status=404)

        paste.current_views += 1
        paste.save()
        
        remaining = None
        if paste.max_views is not None:
            remaining = max(0, paste.max_views - paste.current_views)

        response_data = {
            "content": paste.content,
            "remaining_views": remaining,
            "expires_at": paste.expires_at.isoformat().replace("+00:00", "Z") if paste.expires_at else None
        }

    return JsonResponse(response_data, status=200)

def view_html(request, id):
    now = get_logic_now(request)
    with transaction.atomic():
        try:
            paste = Paste.objects.select_for_update().get(pk=id)
        except Paste.DoesNotExist:
            return HttpResponseNotFound("Not Found")

        if paste.is_unavailable(now):
            return HttpResponseNotFound("Unavailable")

        paste.current_views += 1
        paste.save()
        
        content_to_render = paste.content

    # This looks for templates/pastes/view.html
    return render(request, 'pastes/view.html', {'content': content_to_render})
