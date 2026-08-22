# VOLT-LOGIC

> **Sistem Diagnostik Baterai Kendaraan Listrik (EV) Pre-Dispatch**  
> Solusi full-stack cerdas untuk inspeksi kesehatan baterai armada logistik sebelum keberangkatan rute.

---

## ⚡ Arsitektur Proyek

Repository ini telah diorganisasi secara modular menjadi dua direktori terpisah:
* **[`backend/`](file:///backend/)**: FastAPI REST API + Scikit-Learn ML Inference Engine + SQLAlchemy Database layer.
* **[`frontend/`](file:///frontend/)**: React 19 + TypeScript + Vite + Tailwind CSS v4 Single Page Application.

```text
volt-logic-ui/
├── backend/                  # Python FastAPI Backend
│   ├── model/                # Model ML biner (classifier.joblib)
│   ├── config.py             # Konfigurasi Pydantic & environment
│   ├── database.py           # Koneksi SQLAlchemy & pool
│   ├── Dockerfile            # Docker image backend
│   ├── main.py               # Endpoint API REST
│   ├── middleware.py         # Middleware keamanan & limit payload
│   ├── ml_model.py           # Service inferensi Scikit-Learn
│   ├── models.py             # Schema tabel PostgreSQL / SQLite
│   ├── requirements.txt      # Dependensi Python
│   ├── run.py                # Server launcher script
│   ├── schemas.py            # Pydantic schemas DTO
│   ├── test_api.py           # Test suite otomatis
│   └── train_model.py        # Script pelatihan ML model
│
├── frontend/                 # React TypeScript Frontend
│   ├── public/               # Asset statis publik (SVG logo, favicon)
│   ├── src/
│   │   ├── assets/           # Media komponen
│   │   ├── lib/              # API Client (api.ts)
│   │   ├── App.tsx           # UI Dashboard & Modals
│   │   ├── index.css         # Styling Tailwind CSS v4
│   │   └── main.tsx          # React DOM mounting
│   ├── Dockerfile            # Multi-stage production Nginx build
│   ├── nginx.conf            # Reverse proxy & SPA routing config
│   ├── package.json          # Dependensi frontend UI
│   ├── tsconfig.json         # Konfigurasi TypeScript
│   └── vite.config.ts        # Konfigurasi bundler Vite
│
├── docker-compose.yml        # Orchestration PostgreSQL + Backend + Frontend
├── package.json              # Root workspace convenience scripts
└── README.md
```

---

## 🐳 Panduan Menjalankan dengan Docker (Rekomendasi)

Jalankan seluruh stack (**PostgreSQL Database + FastAPI Backend + React Frontend**) hanya dengan satu perintah:

```bash
docker compose up --build
```

Setelah service aktif:
* 🌐 **Frontend UI**: [http://localhost:5173](http://localhost:5173) atau [http://localhost](http://localhost)
* ⚡ **FastAPI Backend**: [http://localhost:8000](http://localhost:8000) (Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health))
* 🗄️ **PostgreSQL Database**: Port `5432` (`postgres:postgrespassword@localhost:5432/volt_logic`)

Untuk menghentikan:
```bash
docker compose down
```

---

## 🚀 Menjalankan Secara Manual di Lokal (Development)

### 1. Jalankan Backend (FastAPI + ML Model)
```bash
cd backend
pip install -r requirements.txt
python run.py
```
> Server backend akan berjalan di `http://127.0.0.1:8000` dengan fallback SQLite otomatis jika PostgreSQL belum dijalankan.

### 2. Jalankan Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
> Antarmuka UI akan berjalan di `http://localhost:5173` dengan proxy otomatis ke backend di port 8000.

---

## 🧪 Pengujian & Verifikasi

* **Menjalankan Test Suite Backend**:
  ```bash
  python backend/test_api.py
  # atau jika berada di direktori backend:
  cd backend && python test_api.py
  ```

* **Build Bundle Produksi Frontend**:
  ```bash
  cd frontend && npm run build
  ```