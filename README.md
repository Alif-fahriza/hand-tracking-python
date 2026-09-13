# Hand Tracking Project

Project hand tracking berbasis Python yang dikembangkan secara bertahap.

## Teknologi
- Python 3.11+
- [MediaPipe](https://mediapipe.dev/) — deteksi hand landmark 21 titik
- [OpenCV](https://opencv.org/) — akses kamera & rendering UI

## Struktur Project

```
HAND TRACKING/
├── hand_tracker.py     # Modul inti: HandTracker class
├── main.py             # Program utama (Tahap 1)
├── requirements.txt    # Dependensi
├── screenshots/        # Hasil screenshot (dibuat otomatis)
└── README.md
```

## Instalasi

```bash
pip install -r requirements.txt
```

## Cara Menjalankan

```bash
python main.py
```

## Kontrol
| Tombol | Fungsi |
|--------|--------|
| `Q` | Keluar dari program |
| `S` | Simpan screenshot |

---

## Tahap Pengembangan

### ✅ Tahap 1 — Finger Detection (Selesai)
- Mendeteksi hingga **2 tangan** secara bersamaan
- Menampilkan **21 landmark** pada setiap tangan
- Mendeteksi **jari mana saja yang terbuka**
- Menghitung **jumlah jari** (0–5)
- Menampilkan **koordinat pixel** ujung setiap jari
- Mengukur **jarak** antara jempol dan telunjuk
- Menampilkan **label tangan** (Kiri / Kanan)
- Live **FPS counter**
- Fitur **screenshot** (tekan `S`)

### 🔜 Tahap 2 — Gesture Recognition (Rencana)
- Deteksi gesture: OK, peace ✌, thumbs up 👍, fist ✊
- Gesture classifier berbasis rule-based

### 🔜 Tahap 3 — Virtual Mouse (Rencana)
- Kontrol kursor mouse dengan gerakan jari telunjuk
- Klik dengan gesture pinch (jempol + telunjuk menyentuh)

### 🔜 Tahap 4 — Air Canvas (Rencana)
- Menggambar di layar menggunakan jari
- Pilih warna, hapus, simpan gambar

---

## Landmark Reference

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

| ID | Landmark        |
|----|-----------------|
| 0  | Pergelangan     |
| 1  | Ibu jari sendi 1 |
| 2  | Ibu jari sendi 2 |
| 3  | Ibu jari sendi 3 |
| 4  | Ujung ibu jari  |
| 5–8 | Jari telunjuk  |
| 9–12 | Jari tengah   |
| 13–16 | Jari manis   |
| 17–20 | Kelingking   |
