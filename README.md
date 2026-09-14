# ✋ Hand Tracking — Python + MediaPipe

> Project hand tracking berbasis Computer Vision yang mendeteksi **21 landmark tangan** secara real-time, menghitung jumlah jari terbuka, dan mengimplementasikan **Tahap 4: Hand Volume** dengan efek kamera cyanotype, stippling, dan risograph — dikembangkan secara bertahap dengan **MediaPipe** dan **OpenCV**.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00BCD4?logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243?logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?logo=opensource&logoColor=white)

---

## 📖 Tentang Project

Project ini merupakan implementasi **Hand Tracking** menggunakan **MediaPipe Hands** dan **OpenCV**. Program mendeteksi tangan secara *real-time* dari webcam, menampilkan 21 titik landmark pada setiap tangan, mendeteksi jari yang terbuka, dan mengimplementasikan **Tahap 4: Hand Volume** sebagai fitur utama.

Program ini menggabungkan semua fitur dari **Tahap 1 sampai Tahap 4** dalam satu program: mulai dari deteksi landmark dasar, analisis jari, gesture pinch, hingga visualisasi prisma segi-5 (Hand Volume) dengan efek kamera artistik.

Dikembangkan sebagai bagian dari portfolio Computer Vision dan dipublikasikan di GitHub.

---

## ✨ Fitur

> **Implementasi saat ini** sudah mencakup **Tahap 1 sampai Tahap 4** dalam satu program:
> `main.py` — program utama adalah implementasi **Tahap 4: Hand Volume**.

### ✅ Tahap 1 — Finger Detection

| Fitur | Keterangan |
|-------|-----------|
| **Multi-hand Detection** | Mendeteksi hingga **2 tangan** secara bersamaan |
| **21 Landmark per Tangan** | Menampilkan seluruh titik landmark MediaPipe |
| **Finger State Detection** | Mendeteksi jari mana yang terbuka/t Tertutup |
| **Finger Counter** | Menghitung jumlah jari terbuka (0–5) |
| **Landmark Coordinates** | Menampilkan koordinat pixel ujung setiap jari |
| **Thumb-Index Distance** | Mengukur jarak antara jempol dan telunjuk |
| **Hand Label** | Label tangan: **Kiri** / **Kanan** |
| **Live FPS Counter** | Menampilkan *frames per second* secara real-time |
| **Screenshot Feature** | Simpan frame sebagai screenshot (tekan `S`) |

### ✅ Tahap 2 — Gesture Recognition

| Fitur | Keterangan |
|-------|-----------|
| **Pinch Detection** | Deteksi posisi pinch (jempol + telunjuk berdekatan) |
| **2-Finger & 5-Finger Mode** | Mendeteksi mode gerakan 2 jari atau 5 jari |

### 🔜 Tahap 3 — Virtual Mouse

| Fitur | Keterangan |
|-------|-----------|
| **Belum diimplementasi** | Rencana pengembangan selanjutnya |

### ✅ Tahap 4 — Hand Volume (Implementasi Utama)

Program utama `main.py` adalah implementasi dari **Tahap 4: Hand Volume**.

| Fitur | Keterangan |
|-------|-----------|
| **Hand Volume (Prisma Segi-5)** | Menghubungkan 5 pasang jari dari kiri ke kanan: Tangan Kiri → Tangan Kanan |
| **10 Sudut Volume** | Kelingking, Manis, Tengah, Telunjuk, Jempol — dari kedua tangan |
| **Efek Kamera: Cyanotype** | Efek biru Prusia pada bidang quadrilateral |
| **Efek Kamera: Stippling** | Bintik hitam pada latar putih (prints multiples) |
| **Efek Kamera: Risograph** | Noise halftone dengan 2 warna spot (Biru & Pink) |
| **Efek Kamera: Negative** | Invert warna area quadrilateral |
| **HUD Status Pinch** | Status pinch kiri & kanan, mode 2/5 jari |
| **HUD Panel Per Tangan** | Info detail tiap tangan (label, jumlah jari, koordinat, jarak) |

---

## 📸 Demo

Program mendeteksi 2 tangan dengan 21 landmark, menghitung jumlah jari terbuka, dan menampilkan **Hand Volume (prisma segi-5)** dari 10 ujung jari kedua tangan saat kondisi pinch terdeteksi.

_(Screenshot tersedia di folder `screenshots/` setelah menjalankan program dengan tombol `S`)*

---

## 🛠️ Teknologi

| Teknologi | Kegunaan |
|-----------|----------|
| **[Python 3.11+](https://www.python.org/)** | Bahasa pemrograman utama |
| **[MediaPipe](https://mediapipe.dev/)** | Deteksi & tracking tangan (21 landmark) — Google |
| **[OpenCV](https://opencv.org/)** | Akses kamera, rendering, & efek visual |
| **[NumPy](https://numpy.org/)** | Pemrosesan array & perhitungan koordinat |

---

## 📁 Struktur Project

```
hand-tracking-python/
├── main.py                 # Program utama — Tahap 4: Hand Volume (entry point)
├── hand_tracker.py         # Modul inti: HandTracker class (deteksi & landmark)
├── box_gesture.py          # Deteksi gesture & Hand Volume (prisma segi-5)
├── hand_landmarker.task    # Model landmark tangan (TFLite task)
├── requirements.txt        # Dependency Python
├── run.bat                 # Script batch untuk menjalankan program (Windows)
├── screenshots/            # Folder hasil screenshot (otomatis)
└── README.md               # Dokumentasi ini
```

---

## 🚀 Instalasi & Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/Alif-fahriza/hand-tracking-python.git
cd hand-tracking-python
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Catatan:** Pastikan webcam aktif dan OpenCV dapat mengaksesnya.

### 3. Jalankan Program

```bash
python main.py
```

Atau gunakan script batch (Windows):

```bash
run.bat
```

### 4. Kontrol Program

| Tombol | Fungsi |
|--------|--------|
| **`Q`** | Keluar dari program |
| **`S`** | Simpan screenshot ke folder `screenshots/` |

---

## 🖐️ MediaPipe Hand Landmark Reference

MediaPipe mendeteksi **21 landmark** pada setiap tangan:

```
        8   12  16  20
        |   |   |   |
        7   11  15  19
        |   |   |   |
        6   10  14  18
         \  |   |  /
          5  9  13 17
            \|  |/
             2  0
              \/
              1
        (4 = ujung jempol)
```

| ID | Landmark |
|----|----------|
| 0  | Pergelangan tangan (wrist) |
| 1  | Ibu jari — sendi 1 |
| 2  | Ibu jari — sendi 2 |
| 3  | Ibu jari — sendi 3 |
| 4  | Ujung ibu jari (thumb tip) |
| 5  | Jari telunjuk — sendi 1 (MCP) |
| 6  | Jari telunjuk — sendi 2 (PIP) |
| 7  | Jari telunjuk — sendi 3 (DIP) |
| 8  | Ujung jari telunjuk (index tip) |
| 9  | Jari tengah — sendi 1 (MCP) |
| 10 | Jari tengah — sendi 2 (PIP) |
| 11 | Jari tengah — sendi 3 (DIP) |
| 12 | Ujung jari tengah (middle tip) |
| 13 | Jari manis — sendi 1 (MCP) |
| 14 | Jari manis — sendi 2 (PIP) |
| 15 | Jari manis — sendi 3 (DIP) |
| 16 | Ujung jari manis (ring tip) |
| 17 | Kelingking — sendi 1 (MCP) |
| 18 | Kelingking — sendi 2 (PIP) |
| 19 | Kelingking — sendi 3 (DIP) |
| 20 | Ujung kelingking (pinky tip) |

---

## 🤖 AI Model

Model yang digunakan: **MediaPipe Hands** (task file `hand_landmarker.task`)

- **Tipe:** Hand Landmarker (TFLite)
- **Landmark:** 21 titik per tangan
- **Max hands:** 2 tangan secara bersamaan
- **Mode:** Live tracking dari kamera

---

## 👨‍💻 Developer

| | |
|---|---|
| **Nama** | Alif Fahriza |
| **Email** | aliffahriza70@gmail.com |
| **GitHub** | [@Alif-fahriza](https://github.com/Alif-fahriza) |

---

## 🙏 Terima Kasih

- **[MediaPipe](https://mediapipe.dev/)** — Google's open-source ML framework
- **[OpenCV](https://opencv.org/)** — Computer vision library
- Semua pihak yang telah berkontribusi dalam ekosistem Computer Vision 🙌

---

> 💡 **Tips:** Ikuti repository ini untuk update pengembangan selanjutnya (Tahap 3: Virtual Mouse, Tahap 4: Air Canvas).

⭐ **Jangan lupa beri star kalau project ini membantu!**
