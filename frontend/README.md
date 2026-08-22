# VOLT-LOGIC Frontend

> **React 19 + TypeScript + Vite + Tailwind CSS v4**  
> Operational diagnostic UI for EV battery inspection.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Local Development Server
```bash
npm run dev
```
Accessible at [http://localhost:5173](http://localhost:5173).

### 3. Build for Production
```bash
npm run build
```

---

## 📁 Architecture & File Structure

```text
frontend/
├── public/                # Static assets (SVG logo, favicon)
│   └── voltlogic-logo.svg
├── src/
│   ├── assets/            # Embedded component media
│   ├── lib/
│   │   └── api.ts         # Typed API client for FastAPI backend
│   ├── App.tsx            # Root component with diagnostics, modals, and telemetry
│   ├── index.css          # Tailwind CSS entrypoint (@import "tailwindcss")
│   └── main.tsx           # React DOM root mounting
├── index.html             # HTML entrypoint
├── nginx.conf             # Production Nginx reverse proxy configuration
├── Dockerfile             # Multi-stage production container build
├── package.json           # Frontend package dependencies & scripts
├── tsconfig.json          # TypeScript project references
├── tsconfig.app.json      # React application TypeScript configuration
└── vite.config.ts         # Vite bundler & Tailwind v4 plugin config
```
