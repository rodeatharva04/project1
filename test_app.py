import requests
import time
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000"

def log(msg):
    print(f"[TEST] {msg}")

def test_health():
    log("Testing /api/healthz...")
    try:
        r = requests.get(f"{BASE_URL}/api/healthz")
        if r.status_code == 200 and r.json().get('ok') is True:
            log("✅ Health check passed")
        else:
            log(f"❌ Health check failed: {r.text}")
            return False
    except Exception as e:
        log(f"❌ Health check connection failed: {e}")
        log("   (Make sure the server is running: python manage.py runserver)")
        return False
    return True

def test_create_and_fetch():
    log("Testing Create & Fetch...")
    payload = {"content": "Hello World", "ttl_seconds": 60, "max_views": 5}
    r = requests.post(f"{BASE_URL}/api/pastes", json=payload)
    if r.status_code != 201:
        log(f"❌ Create failed: {r.text}")
        return False
    
    data = r.json()
    pk = data['id']
    log(f"Created paste {pk}")

    r2 = requests.get(f"{BASE_URL}/api/pastes/{pk}")
    if r2.status_code == 200 and r2.json()['content'] == "Hello World":
        log("✅ Create & Fetch passed")
        return pk
    else:
        log("❌ Create & Fetch failed")
        return False

def test_view_limits():
    log("Testing View Limits...")
    r = requests.post(f"{BASE_URL}/api/pastes", json={"content": "Limit Test", "max_views": 2})
    pk = r.json()['id']

    # 1st view
    requests.get(f"{BASE_URL}/api/pastes/{pk}")
    # 2nd view
    requests.get(f"{BASE_URL}/api/pastes/{pk}")
    # 3rd view (should fail)
    r3 = requests.get(f"{BASE_URL}/api/pastes/{pk}")
    
    if r3.status_code == 404:
        log("✅ View limit enforcement passed (404 on 3rd try)")
        return True
    else:
        log(f"❌ View limit failed, got {r3.status_code}")
        return False

def test_ttl_expiry():
    log("Testing TTL Expiry (Deterministic)...")
    # This requires TEST_MODE=1 in the server environment
    r = requests.post(f"{BASE_URL}/api/pastes", json={"content": "Time Test", "ttl_seconds": 60})
    pk = r.json()['id']
    
    now_ms = int(time.time() * 1000)
    future_ms = now_ms + 70000 # 70 seconds in future

    # 1. Fetch "now" -> Should exist
    headers = {"x-test-now-ms": str(now_ms)}
    r1 = requests.get(f"{BASE_URL}/api/pastes/{pk}", headers=headers)
    if r1.status_code != 200:
        log(f"❌ Immediate fetch failed: {r1.status_code}")
        log("   (Note: This test might fail if TEST_MODE=1 is not set in server)")
        return False

    # 2. Fetch "future" -> Should be 404
    headers_future = {"x-test-now-ms": str(future_ms)}
    r2 = requests.get(f"{BASE_URL}/api/pastes/{pk}", headers=headers_future)
    
    if r2.status_code == 404:
        log("✅ TTL Expiry passed (404 with future timestamp)")
        return True
    else:
        log(f"❌ TTL Expiry failed, got {r2.status_code} for future time")
        return False

if __name__ == "__main__":
    print("=== Pastebin Lite Self-Test ===")
    if not test_health():
        sys.exit(1)
    
    test_create_and_fetch()
    test_view_limits()
    
    print("\n--- Testing TTL (Requires TEST_MODE=1) ---")
    test_ttl_expiry()
    print("\n✅ Done.")
