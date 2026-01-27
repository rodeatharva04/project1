import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /api/healthz...")
    try:
        r = requests.get(f"{BASE_URL}/api/healthz")
        assert r.status_code == 200
        assert r.json()['ok'] == True
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

def test_create_and_fetch():
    print("Testing Create & Fetch...")
    payload = {"content": "Hello World", "ttl_seconds": 60, "max_views": 5}
    r = requests.post(f"{BASE_URL}/api/pastes", json=payload)
    if r.status_code != 201:
        print(f"❌ Create failed: {r.text}")
        sys.exit(1)
    
    data = r.json()
    pk = data['id']
    print(f"Created paste {pk}")

    r2 = requests.get(f"{BASE_URL}/api/pastes/{pk}")
    assert r2.status_code == 200
    assert r2.json()['content'] == "Hello World"
    print("✅ Create & Fetch passed")
    return pk

def test_view_limits():
    print("Testing View Limits...")
    # Create with max_views = 2
    r = requests.post(f"{BASE_URL}/api/pastes", json={"content": "Limit Test", "max_views": 2})
    pk = r.json()['id']

    # 1st view
    r1 = requests.get(f"{BASE_URL}/api/pastes/{pk}")
    assert r1.status_code == 200
    
    # 2nd view
    r2 = requests.get(f"{BASE_URL}/api/pastes/{pk}")
    assert r2.status_code == 200

    # 3rd view (should fail)
    r3 = requests.get(f"{BASE_URL}/api/pastes/{pk}")
    if r3.status_code == 404:
        print("✅ View limit enforcement passed (404 on 3rd try)")
    else:
        print(f"❌ View limit failed, got {r3.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_health()
        test_create_and_fetch()
        test_view_limits()
        print("\n🎉 All basic sanity checks passed!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
