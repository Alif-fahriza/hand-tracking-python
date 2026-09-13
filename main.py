"""
Hand Tracking - Tahap 4: Hand Volume
====================================
Program utama untuk mendeteksi tangan dan menggambar volume tangan (prisma segi-5)
menggunakan gesture pinch dua tangan secara real-time.

Kompatibel dengan MediaPipe >= 1.0.0 (Tasks API)

Fitur Tahap 4:
  - Semua fitur Tahap 1, 2, dan 3
  - Menghubungkan 5 pasang jari dari kiri ke kanan:
    A=J (Kelingking), B=I (Manis), C=H (Tengah), D=G (Telunjuk), E=F (Jempol)
  - Membuat prisma segi-5 (Hand Volume)
  - Setiap jari dan muka prisma diberi warna unik
  - Volume hilang saat tangan tidak terdeteksi

Kontrol:
  - Q : Keluar
  - S : Simpan screenshot
"""

import cv2
import time
import os
from hand_tracker import HandTracker
from box_gesture import BoxGesture

# ─────────────────────────────────────────────
#  Konfigurasi
# ─────────────────────────────────────────────
CAMERA_INDEX        = 0
FRAME_WIDTH         = 1280
FRAME_HEIGHT        = 720
MAX_HANDS           = 2
DETECT_CONFIDENCE   = 0.7
TRACK_CONFIDENCE    = 0.5
MODEL_PATH          = "hand_landmarker.task"
SCREENSHOT_DIR      = "screenshots"

# Warna (BGR)
C_PANEL     = (20, 20, 30)
C_WHITE     = (255, 255, 255)
C_GREEN     = (50, 220, 100)
C_RED       = (60, 60, 220)
C_YELLOW    = (0, 210, 255)
C_CYAN      = (220, 200, 0)
C_ORANGE    = (0, 140, 255)
C_GRAY      = (120, 120, 130)
C_ACCENT    = (180, 90, 255)
C_DARK_GRAY = (50, 50, 60)

FINGER_COLORS = {
    "THUMB":  C_ORANGE,
    "INDEX":  C_GREEN,
    "MIDDLE": C_CYAN,
    "RING":   C_ACCENT,
    "PINKY":  C_YELLOW,
}
FINGER_LABEL_ID = {
    "THUMB":  "Jempol",
    "INDEX":  "Telunjuk",
    "MIDDLE": "Tengah",
    "RING":   "Manis",
    "PINKY":  "Kelingking",
}
FINGER_ORDER = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]


# ─────────────────────────────────────────────
#  Helper UI
# ─────────────────────────────────────────────

def overlay_alpha(img, x1, y1, x2, y2, color, alpha=0.70, radius=10):
    """Gambar rectangle transparan dengan sudut membulat (simulasi)."""
    overlay = img.copy()
    # Isi utama
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    for cx, cy in [(x1 + radius, y1 + radius), (x2 - radius, y1 + radius),
                   (x1 + radius, y2 - radius), (x2 - radius, y2 - radius)]:
        cv2.circle(overlay, (cx, cy), radius, color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


def put_text(img, text, x, y, font_scale=0.5, color=C_WHITE, thickness=1,
             font=cv2.FONT_HERSHEY_SIMPLEX):
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness,
                cv2.LINE_AA)


def draw_finger_pill(img, cx: int, cy: int, name: str, is_open: bool):
    """Gambar indikator bulat berwarna untuk setiap jari."""
    color = FINGER_COLORS[name] if is_open else C_DARK_GRAY
    border = C_WHITE if is_open else (70, 70, 80)
    r = 18
    cv2.circle(img, (cx, cy), r, color, -1)
    cv2.circle(img, (cx, cy), r + 1, border, 1)
    label = FINGER_LABEL_ID[name][:3]
    ts = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.32, 1)[0]
    put_text(img, label, cx - ts[0] // 2, cy + ts[1] // 2,
             font_scale=0.32, color=C_WHITE)


# ─────────────────────────────────────────────
#  HUD Rendering
# ─────────────────────────────────────────────

def draw_hud(frame, tracker: HandTracker, fps: float, frame_count: int):
    h, w = frame.shape[:2]
    num = tracker.num_hands_detected()

    # ── Header ────────────────────────────────────────────────────
    overlay_alpha(frame, 8, 6, 480, 54, C_PANEL, alpha=0.78)
    put_text(frame, "HAND TRACKING  |  Tahap 4: Hand Volume",
             18, 36, 0.62, C_ACCENT, 1, cv2.FONT_HERSHEY_DUPLEX)

    # ── FPS badge ───────────────────────────────────────
    fps_col = C_GREEN if fps >= 25 else (C_YELLOW if fps >= 15 else C_RED)
    fps_txt = f"FPS: {fps:5.1f}"
    fsz = cv2.getTextSize(fps_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.62, 2)[0]
    fx = w - fsz[0] - 22
    overlay_alpha(frame, fx - 10, 6, w - 8, 48, C_PANEL, alpha=0.78)
    put_text(frame, fps_txt, fx, 36, 0.62, fps_col, 2)

    # ── Frame counter ────────────────────────────────────
    put_text(frame, f"Frame #{frame_count:06d}", 18, 68, 0.38, C_GRAY)

    # ── Tidak ada tangan ────────────────────────────────
    if num == 0:
        overlay_alpha(frame, 8, 80, 350, 115, C_PANEL, alpha=0.75)
        put_text(frame, "Arahkan tangan ke kamera...", 18, 103, 0.5, C_RED)
        # Hint
        _draw_hint(frame, w, h)
        return

    # ── Panel per tangan ────────────────────────────────
    for hand_no in range(num):
        lms = tracker.find_position(frame, hand_no)
        open_fingers = tracker.get_open_fingers(lms)
        total_open = len(open_fingers)
        label = tracker.get_hand_label(hand_no) or "?"
        label_id = "Kanan" if label == "Right" else "Kiri"

        panel_x = 8 + hand_no * 345
        panel_y = 78
        pw, ph = 330, 200

        overlay_alpha(frame, panel_x, panel_y, panel_x + pw, panel_y + ph,
                      C_PANEL, alpha=0.82)

        # Judul
        put_text(frame, f"Tangan {label_id}  [{total_open}/5 jari terbuka]",
                 panel_x + 12, panel_y + 26, 0.55, C_WHITE, 1)

        # Separator
        cv2.line(frame, (panel_x + 10, panel_y + 32),
                 (panel_x + pw - 10, panel_y + 32), (60, 60, 80), 1)

        # Indikator jari
        spacing = pw // (len(FINGER_ORDER) + 1)
        for i, fname in enumerate(FINGER_ORDER):
            bx = panel_x + spacing * (i + 1)
            by = panel_y + 72
            draw_finger_pill(frame, bx, by, fname, fname in open_fingers)

        # Jari yang terbuka
        open_str = "  ".join([FINGER_LABEL_ID[f] for f in open_fingers]) \
                   if open_fingers else "─ Tidak ada ─"
        put_text(frame, open_str, panel_x + 12, panel_y + 115, 0.42, C_YELLOW)

        # Koordinat ujung jari
        put_text(frame, "Koordinat (x, y):", panel_x + 12, panel_y + 140,
                 0.37, C_GRAY)
        tip_ids = [4, 8, 12, 16, 20]
        coords = " ".join(
            [f"({lms[tid][1]},{lms[tid][2]})" for tid in tip_ids if lms and tid < len(lms)]
        )
        put_text(frame, coords, panel_x + 12, panel_y + 160, 0.33, C_CYAN)

        # Jarak jempol–telunjuk
        dist = tracker.get_distance(4, 8)
        d_col = C_GREEN if dist < 60 else C_WHITE
        put_text(frame, f"Jarak Jempol-Telunjuk: {dist:.0f} px",
                 panel_x + 12, panel_y + 182, 0.38, d_col)

        # Highlight ujung jari
        for fname, tip_id in HandTracker.FINGER_TIPS.items():
            if lms and tip_id < len(lms):
                _, cx, cy = lms[tip_id]
                col = FINGER_COLORS[fname]
                cv2.circle(frame, (cx, cy), 13, col, -1)
                cv2.circle(frame, (cx, cy), 13, C_WHITE, 2)

    _draw_hint(frame, w, h)


def _draw_hint(frame, w, h):
    hint = "Q: Keluar   |   S: Screenshot"
    sz = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
    hx = (w - sz[0]) // 2
    overlay_alpha(frame, hx - 10, h - 32, hx + sz[0] + 10, h - 5,
                  C_PANEL, alpha=0.70)
    put_text(frame, hint, hx, h - 11, 0.4, C_GRAY)


# ─────────────────────────────────────────────
#  Main Program
# ─────────────────────────────────────────────

def find_camera() -> cv2.VideoCapture | None:
    """Coba buka kamera dari index 0 hingga 3, kembalikan yang berhasil."""
    for idx in range(4):
        print(f"  Mencoba kamera index {idx}...", end=" ")
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # CAP_DSHOW lebih stabil di Windows
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"OK! (index {idx})")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
                return cap
            else:
                cap.release()
                print("terbuka tapi tidak bisa membaca frame.")
        else:
            print("tidak tersedia.")
    return None


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # ── Auto-detect kamera ──
    print("Mencari kamera yang tersedia...")
    cap = find_camera()

    if cap is None:
        print()
        print("[ERROR] Tidak ada kamera yang ditemukan!")
        print("        Pastikan webcam sudah terhubung dan tidak dipakai aplikasi lain.")
        print("        (Tutup Zoom, Teams, atau aplikasi kamera lain)")
        return

    # ── Inisialisasi tracker ──
    print("Memuat model MediaPipe HandLandmarker...")
    tracker = HandTracker(
        model_path=MODEL_PATH,
        max_num_hands=MAX_HANDS,
        min_detection_confidence=DETECT_CONFIDENCE,
        min_tracking_confidence=TRACK_CONFIDENCE,
    )
    box = BoxGesture()

    prev_time   = time.time()
    frame_count = 0
    ss_count    = 0

    print("=" * 55)
    print("  HAND TRACKING - Tahap 4: Hand Volume")
    print("=" * 55)
    print(f"  [OK] Kamera       : index {CAMERA_INDEX}")
    print(f"  [OK] Resolusi     : {FRAME_WIDTH}x{FRAME_HEIGHT}")
    print(f"  [OK] Jumlah tangan: maks {MAX_HANDS}")
    print(f"  [OK] Model        : {MODEL_PATH}")
    print()
    print("  Kontrol:")
    print("    Q  -> Keluar")
    print("    S  -> Simpan screenshot")
    print("=" * 55)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Gagal membaca frame.")
            break

        frame = cv2.flip(frame, 1)   # Mirror agar natural
        frame_count += 1

        # Deteksi tangan
        frame = tracker.find_hands(frame, draw=True)

        # Ambil landmark kedua tangan (Left/Right)
        both = tracker.get_landmarks_both_hands(frame)
        right_lms = both["Right"]
        left_lms  = both["Left"]

        # Update & gambar kotak
        box.update(right_lms, left_lms)
        box.draw(frame)

        # Hitung FPS
        now = time.time()
        fps = 1.0 / (now - prev_time + 1e-9)
        prev_time = now

        # Gambar HUD
        draw_hud(frame, tracker, fps, frame_count)

        # Gambar badge status pinch
        box.draw_hud(frame, right_lms, left_lms)

        # Tampilkan
        cv2.imshow("Hand Tracking - Tahap 4: Hand Volume | Tekan Q untuk keluar", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            print("\n[INFO] Keluar...")
            break
        elif key in (ord('s'), ord('S')):
            ss_count += 1
            path = os.path.join(SCREENSHOT_DIR, f"ss_{ss_count:03d}.png")
            cv2.imwrite(path, frame)
            print(f"[INFO] Screenshot disimpan: {path}")

    tracker.release()
    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Selesai — total frame: {frame_count}")


if __name__ == "__main__":
    main()
