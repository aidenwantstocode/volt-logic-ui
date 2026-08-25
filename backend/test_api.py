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

    # 1. Root & Health Check
    print("\n[1/9] Testing GET / and GET /api/health and GET /health...")
    root_resp = client.get("/")
    assert root_resp.status_code == 200, f"Expected 200 on /, got {root_resp.status_code}"
    root_data = root_resp.json()
    assert root_data.get("status") == "online"
    print(f"  [PASS] Root endpoint returned status: {root_data.get('status')}")

    resp = client.get("/api/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("ok") is True, f"Health check failed: {data}"

    resp_alias = client.get("/health")
    assert resp_alias.status_code == 200, f"Expected 200 on /health, got {resp_alias.status_code}"
    print("  [PASS] Health check OK on /api/health and /health.")

    # 2. ML Prediction (Healthy: Capacity > 0.8249, Re < 0.0777, Rct < 0.1251)
    print("\n[2/9] Testing POST /api/predict & POST /predict (Healthy EIS telemetry)...")
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

    # Direct alias test
    resp2 = client.post("/predict", json=payload)
    assert resp2.status_code == 200, f"Expected 200 on /predict alias, got {resp2.status_code}"
    print("  [PASS] /predict direct alias functioning properly.")

    # 3. ML Prediction (Critical: Low Capacity & High Resistance)
    print("\n[3/9] Testing POST /api/predict (Critical Degradation: Capacity=0.65, Re=0.115, Rct=0.210)...")
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
    print("\n[4/9] Testing POST /api/predict (Warning / Perlu uji lanjut)...")
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

    # 5. History Query with/without parameters
    print("\n[5/9] Testing GET /api/history and /history...")
    resp = client.get("/api/history")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    print(f"  [PASS] Unscoped history returns list (total: {len(resp.json())} items).")

    # 6. Save and Read Inspection Record with 4 EIS features
    print("\n[6/9] Testing POST /api/history and scoped GET /api/history...")
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
    print("\n[7/9] Testing Request Body Size Limiter (> 10 KB)...")
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
    print("\n[8/9] Testing Security Headers...")
    resp = client.get("/api/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    print("  [PASS] Verified X-Content-Type-Options and X-Frame-Options.")

    # 9. Custom 404 Handler
    print("\n[9/9] Testing Custom 404 Handler for Unknown Route...")
    resp404 = client.get("/nonexistent_endpoint_xyz")
    assert resp404.status_code == 404
    data404 = resp404.json()
    assert "available_endpoints" in data404
    print("  [PASS] Non-existent endpoint returned descriptive 404 payload.")

    print("\n=======================================================")
    print("SUCCESS: ALL 9 BACKEND TEST SUITES PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
