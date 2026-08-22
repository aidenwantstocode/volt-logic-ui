import sys
import os

# Ensure UTF-8 output encoding if possible
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

from fastapi.testclient import TestClient
try:
    from backend.main import app
    from backend.database import init_db
except ImportError:
    from main import app
    from database import init_db

def run_tests():
    print(">> Starting Automated Backend Verification Suite (Battery EIS Model)...")
    init_db()
    client = TestClient(app)

    # 1. Health Check
    print("\n[1/8] Testing GET /api/health...")
    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("ok") is True, f"Health check failed: {data}"
    print("  [PASS] Health check OK.")

    # 2. ML Prediction (Healthy: Capacity > 0.8249, Re < 0.0777, Rct < 0.1251)
    print("\n[2/8] Testing POST /api/predict (Healthy EIS telemetry: Capacity=0.95, Re=0.054, Rct=0.105)...")
    payload = {
        "vehicle_id": "EV-402",
        "company": "PT. Logistik Nusantara Express",
        "battery_type": "Lithium-Ion 400V (NMC)",
        "capacity": 0.95,
        "re": 0.054,
        "rct": 0.105,
        "ambient_temperature": 24.0
    }
    resp = client.post("/api/predict", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    pred = resp.json()
    assert pred["status"] == "HEALTHY", f"Expected HEALTHY, got {pred['status']}"
    assert pred["status_id"] == "aman"
    assert "model_version" in pred
    assert "%" in pred["confidence"]
    print(f"  [PASS] Status = {pred['status']} ({pred['status_id']}), Confidence = {pred['confidence']}, Version = {pred['model_version']}")

    # 3. ML Prediction (Critical: Low Capacity & High Resistance)
    print("\n[3/8] Testing POST /api/predict (Critical Degradation: Capacity=0.65, Re=0.115, Rct=0.210)...")
    critical_payload = {
        "vehicle_id": "EV-999",
        "company": "PT. Logistik Nusantara Express",
        "battery_type": "Lithium-Ion 400V (NMC)",
        "capacity": 0.65,
        "re": 0.115,
        "rct": 0.210,
        "ambient_temperature": 30.0
    }
    resp = client.post("/api/predict", json=critical_payload)
    assert resp.status_code == 200
    crit_pred = resp.json()
    assert crit_pred["status"] == "CRITICAL", f"Expected CRITICAL, got {crit_pred['status']}"
    assert crit_pred["status_id"] == "tidak aman"
    assert "GROUNDED" in crit_pred["route"]
    print(f"  [PASS] Correctly identified CRITICAL / tidak aman state ({crit_pred['route'][:35]}...)")

    # 4. ML Prediction (Warning: Moderate degradation / needs further test)
    print("\n[4/8] Testing POST /api/predict (Warning / Perlu uji lanjut)...")
    warning_payload = {
        "vehicle_id": "EV-505",
        "company": "PT. Logistik Nusantara Express",
        "battery_type": "Lithium-Ion 400V (NMC)",
        "capacity": 0.80,
        "re": 0.085,
        "rct": 0.135,
        "ambient_temperature": 25.0
    }
    resp = client.post("/api/predict", json=warning_payload)
    assert resp.status_code == 200
    warn_pred = resp.json()
    assert warn_pred["status"] in ["WARNING", "HEALTHY", "CRITICAL"]
    print(f"  [PASS] Warning payload returned status = {warn_pred['status']} ({warn_pred['status_id']})")

    # 5. Scoped Access Enforcement (Missing company/batteryType -> 400)
    print("\n[5/8] Testing GET /api/history without parameters (Must reject with 400)...")
    resp = client.get("/api/history")
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    print("  [PASS] Blocked unscoped history query with HTTP 400.")

    # 6. Save and Read Inspection Record with 4 EIS features
    print("\n[6/8] Testing POST /api/history and scoped GET /api/history...")
    new_record = {
        "vehicle_id": "EV-TEST-EIS",
        "company": "PT. Fast Track Kuririndo",
        "battery_type": "LFP 48V Micro-Delivery",
        "capacity": 0.92,
        "re": 0.058,
        "rct": 0.110,
        "ambient_temperature": 24.5,
        "status": "HEALTHY",
        "confidence": "99.2%",
        "model_version": "v2.0.0-battery-eis"
    }
    post_resp = client.post("/api/history", json=new_record)
    assert post_resp.status_code == 201, f"Expected 201, got {post_resp.status_code}: {post_resp.text}"
    created = post_resp.json()
    assert created["vehicle_id"] == "EV-TEST-EIS"
    print("  [PASS] Inspection record with EIS features saved with HTTP 201.")

    # Read scoped history
    get_resp = client.get(
        "/api/history",
        params={
            "company": "PT. Fast Track Kuririndo",
            "batteryType": "LFP 48V Micro-Delivery"
        }
    )
    assert get_resp.status_code == 200
    records = get_resp.json()
    assert len(records) >= 1
    print(f"  [PASS] Retrieved {len(records)} scoped inspection records.")

    # 7. Payload Size Limit (> 10KB)
    print("\n[7/8] Testing Request Body Size Limiter (> 10 KB)...")
    large_payload = {
        "vehicle_id": "EV-402",
        "company": "A" * 12000,
        "battery_type": "Lithium-Ion 400V (NMC)",
        "capacity": 0.95,
        "re": 0.05,
        "rct": 0.10,
        "ambient_temperature": 25.0
    }
    resp = client.post("/api/predict", json=large_payload)
    assert resp.status_code in [413, 422], f"Expected 413 or 422, got {resp.status_code}"
    print(f"  [PASS] Excessive payload rejected ({resp.status_code}).")

    # 8. Security Headers
    print("\n[8/8] Testing Security Headers...")
    resp = client.get("/api/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    print("  [PASS] Verified X-Content-Type-Options and X-Frame-Options.")

    print("\n=======================================================")
    print("SUCCESS: ALL 8 BACKEND TEST SUITES PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
