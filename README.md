# VOLT-LOGIC UI

> **Sistem Diagnostik Baterai Kendaraan Listrik (EV) Pre-Dispatch**  
> Antarmuka inspeksi operasional untuk mengevaluasi kesehatan baterai armada logistik sebelum keberangkatan rute.

---

## ⚡ Gambaran Umum

**VOLT-LOGIC UI** adalah aplikasi Single-Page Application (SPA) yang dirancang untuk teknisi dan operator depot armada logistik. Sistem ini memproses data telemetri baterai secara langsung maupun simulasi (Tegangan, Arus, Suhu, dan Resistansi Internal) untuk menghasilkan keputusan operasional preskriptif secara instan (`HEALTHY`, `WARNING`, atau `CRITICAL`).

---

## 🛠 Teknologi yang Digunakan

| Komponen | Teknologi |
| :--- | :--- |
| **Framework** | [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) |
| **Build Tool & Bundler** | [Vite](https://vite.dev/) |
| **Styling Framework** | [Tailwind CSS v4](https://tailwindcss.com/) (via `@tailwindcss/vite`) |
| **Ikon & Aset** | Native SVG & [Lucide Icons](https://lucide.dev/) |

---

## 📋 Prasyarat Sistem

Pastikan perangkat Anda telah terpasang perangkat lunak berikut:

* **Node.js**: versi `v20.x` atau lebih baru (direkomendasikan `v24.x LTS`)
* **npm**: versi `v10.x` atau lebih baru
* **Git**

Periksa versi di terminal:
```bash
node -v
npm -v
git --version
```

---

## 🚀 Panduan Menjalankan Proyek di Lokal

### 1. Klon Repositori
```bash
git clone https://github.com/<username-atau-organisasi>/volt-logic-ui.git
cd volt-logic-ui
```

### 2. Pasang Dependensi
```bash
npm install
```

### 3. Jalankan Development Server
```bash
npm run dev
```

Aplikasi akan berjalan di `http://localhost:5173/` dengan fitur Hot Module Replacement (HMR) aktif otomatis saat kode dimodifikasi.

---

## 📖 Tutorial Penggunaan Antarmuka

Berikut alur operasional pengujian pada antarmuka VOLT-LOGIC:

### Langkah 1: Pilih Profil Perusahaan & Baterai
1. Klik dropdown **Nama Perusahaan** dan pilih profil mitra armada (contoh: `PT. Logistik Nusantara Express`).
2. Dropdown **Jenis baterai** akan aktif otomatis menampilkan opsi tipe kimia baterai yang sesuai. Pilih salah satu (contoh: `Lithium-Ion 400V (NMC)`).

### Langkah 2: Menjalankan Cek Telemetri (AI Health Check)
1. Klik tombol **Cek/Input Baterai** di sebelah kanan.
2. Modal input parameter telemetri akan terbuka.
3. Masukkan data pengujian kendaraan:
   * **Vehicle ID**: Nomor identitas armada (contoh: `EV-402`)
   * **Tegangan / Voltage (V)**: Tegangan aktual baterai (contoh: `384.2`)
   * **Arus / Current (A)**: Arus uji baterai (contoh: `12.5`)
   * **Suhu / Temp (°C)**: Suhu operasional sel baterai
   * **Internal Resistance (Ω)**: Nilai hambatan dalam baterai (contoh: `0.038`)
4. Klik tombol **Jalankan AI Health Check**.

### Langkah 3: Membaca Hasil Keputusan Preskriptif
Sistem inferensi AI akan mengembalikan status dan izin rute secara instan:
* **STATUS: HEALTHY** (Suhu <= 35°C): Izin muatan penuh untuk rute jarak jauh antarkota (*Authorized*).
* **STATUS: WARNING** (Suhu 35°C - 45°C): Pembatasan muatan dan dikhususkan untuk rute pendek dalam kota (*Restricted Micro-delivery*).
* **STATUS: CRITICAL** (Suhu > 45°C): Larangan jalan penuh (*Grounded*) dan kendaraan wajib dialihkan ke unit pemeliharaan teknis.

### Langkah 4: Meninjau Riwayat Inspeksi
1. Pastikan profil perusahaan dan baterai telah dipilih.
2. Klik tombol **Riwayat Database** di sebelah kiri.
3. Tinjau log tabel audit kendaraan sebelumnya beserta waktu inspeksi dan status AI.

---

## 📂 Struktur Direktori Proyek

```text
volt-logic-ui/
├── public/                # Aset publik statis (Logo SVG, favicon)
│   └── voltlogic-logo.svg
├── src/
│   ├── assets/            # Media internal pendukung komponen
│   ├── App.tsx            # Komponen utama antarmuka, state, logic, dan modal
│   ├── index.css          # Titik masuk Tailwind CSS v4 (@import "tailwindcss")
│   └── main.tsx           # Titik kait virtual DOM React
├── package.json           # Deklarasi paket, skrip, dan metadata proyek
├── tsconfig.json          # Konfigurasi compiler TypeScript
└── vite.config.ts         # Konfigurasi bundler Vite & plugin Tailwind v4
```

---

## 📜 Perintah yang Tersedia

| Perintah | Deskripsi |
| :--- | :--- |
| `npm run dev` | Menjalankan server lokal pengembangan Vite. |
| `npm run build` | Melakukan kompilasi TypeScript dan membuat bundle produksi di folder `/dist`. |
| `npm run preview` | Menjalankan server lokal untuk menguji hasil build produksi. |
| `npm run lint` | Menjalankan pemeriksaan format dan standar kode via ESLint. |

---

## 🤝 Panduan Kontribusi Tim

1. Pastikan cabang `main` lokal Anda sinkron dengan remote:
```bash
git checkout main
git pull origin main
```
2. Buat cabang fitur baru:
```bash
git checkout -b feat/nama-fitur-anda
```
3. Gunakan standar pesan commit **Conventional Commits**:
   * `feat: ...` untuk penambahan fitur atau komponen UI baru
   * `fix: ...` untuk perbaikan bug atau visual
   * `refactor: ...` untuk perapian kode tanpa mengubah alur logika
   * `chore: ...` untuk pembaruan dependensi atau konfigurasi
4. Unggah cabang ke GitHub dan ajukan **Pull Request (PR)** ke cabang `main`.