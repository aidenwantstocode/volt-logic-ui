# VOLT-LOGIC Backend — FastAPI + PostgreSQL

Operational Telemetry & ML Battery Diagnostic API for Electric Vehicle Logistics Fleets.

---

## ⚡ Features & Hardened Security Architecture

* **Endpoints**:
  * `GET /api/health` — Liveness check for uptime monitors & judges.
  * `POST /api/predict` — Runs electrical & thermal telemetry through the pre-trained ML classifier (`RandomForest` / `GradientBoosting`), returning health status (`HEALTHY`, `WARNING`, `CRITICAL`), confidence score, prescriptive route recommendation, and model versioning.
  * `GET /api/history` — Scoped inspection query strictly requiring both `company` and `batteryType` (rejects with `400` if missing; capped at `LIMIT 50`).
  * `POST /api/history` — Saves inspection records to PostgreSQL.
* **Security Hardening**:
  * **CORS locked**: Restricts cross-origin requests to configured frontend origins.
  * **Pydantic validation**: Enforces strict boundaries (voltage 0–1000V, current -500–500A, temperature -40–200°C, resistance 0–10Ω, vehicle_id max 32 chars).
  * **Rate limiting (`slowapi`)**: Per-IP limits on `/api/predict` (20/min) and `/api/history` (30/min).
  * **Body size limit**: Maximum 10 KB upload limit to block DoS payloads.
  * **Security headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Referrer-Policy`.
  * **Generic error messages**: Zero stack trace or SQL leakage to clients.
  * **PostgreSQL ORM**: Parameterized queries via SQLAlchemy (no SQL injection risk).

---

## 🚀 Setup & Execution

### 1. Configure Environment (`.env`)
Copy the template and set your credentials:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```ini
# PostgreSQL connection (e.g. Supabase, Neon, Render, or local PostgreSQL)
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres

# Place your external ML Model API Key here (if using external API)
ML_MODEL_API_KEY=your_api_key_here

# Frontend CORS URL
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

> **Note**: If `DATABASE_URL` is left as default `sqlite:///./volt_logic.db`, it will automatically run with SQLite for instant zero-infrastructure local demos.

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. (Optional) Re-train / Build ML Model
```bash
python -m backend.train_model
```

### 4. Run the Backend Server
```bash
python -m backend.run
```
or via Uvicorn:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Quick Test Endpoints

* **Health Check**:
  ```bash
  curl -X GET http://127.0.0.1:8000/api/health
  ```
* **ML Inference**:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/predict \
    -H "Content-Type: application/json" \
    -d '{
      "vehicle_id": "EV-402",
      "company": "PT. Logistik Nusantara Express",
      "battery_type": "Lithium-Ion 400V (NMC)",
      "voltage": 384.2,
      "current": 12.5,
      "temperature": 31.4,
      "internal_resistance": 0.038
    }'
  ```
* **History (Scoped Query)**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/history?company=PT.%20Logistik%20Nusantara%20Express&batteryType=Lithium-Ion%20400V%20(NMC)"
  ```
