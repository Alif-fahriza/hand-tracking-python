"""
Box Gesture Module -- Tahap 4: Hand Volume
==========================================
Mengelola gesture Hand Volume (prisma segi-5) menggunakan semua jari
kedua tangan.

Alur:
  IDLE       -> (kedua tangan pinch bersamaan) -> BOX_ACTIVE
  BOX_ACTIVE -> volume real-time mengikuti semua ujung jari
  BOX_ACTIVE -> (tangan tidak terdeteksi)       -> IDLE

Corner mapping (10 sudut):
  Tangan Kiri  (A-E): A=Kelingking(20) B=Manis(16) C=Tengah(12)
                      D=Telunjuk(8)    E=Jempol(4)
  Tangan Kanan (F-J): F=Jempol(4)     G=Telunjuk(8) H=Tengah(12)
                      I=Manis(16)      J=Kelingking(20)

Pasangan (edge penghubung):
  A-J  B-I  C-H  D-G  E-F
"""

import cv2
import math
import numpy as np

# ----------------------------------------------------------------
#  Konstanta
# ----------------------------------------------------------------
PINCH_THRESHOLD = 50

_LEFT_TIPS   = [20, 16, 12, 8, 4]   # A, B, C, D, E
_RIGHT_TIPS  = [4,  8,  12, 16, 20]  # F, G, H, I, J
_LEFT_LABELS  = ["A", "B", "C", "D", "E"]
_RIGHT_LABELS = ["F", "G", "H", "I", "J"]
_ALL_LABELS   = _LEFT_LABELS + _RIGHT_LABELS

# Pasangan A-J, B-I, C-H, D-G, E-F
_PAIRS = [("A","J"), ("B","I"), ("C","H"), ("D","G"), ("E","F")]

# Warna per sudut (BGR)
_COLORS = {
    "A": (  0, 210, 255),  # kuning     - L_Kelingking
    "B": (180,  90, 255),  # ungu       - L_Manis
    "C": (220, 200,   0),  # cyan       - L_Tengah
    "D": ( 50, 220, 100),  # hijau      - L_Telunjuk
    "E": (  0, 140, 255),  # oranye     - L_Jempol
    "F": (  0, 100, 200),  # oranye tua - R_Jempol
    "G": ( 30, 160,  70),  # hijau tua  - R_Telunjuk
    "H": (160, 140,   0),  # cyan tua   - R_Tengah
    "I": (130,  60, 200),  # ungu tua   - R_Manis
    "J": (  0, 160, 200),  # kuning tua - R_Kelingking
}

# Warna muka (BGR)
_C_FACE_LEFT   = (180,  80, 255)   # ungu       - muka kiri
_C_FACE_RIGHT  = (255, 140,  60)   # oranye     - muka kanan
_C_QUADS = [
    ( 60, 180, 255),   # biru muda  - A-B-I-J
    ( 80, 200, 180),   # teal       - B-C-H-I
    (100, 200, 100),   # hijau muda - C-D-G-H
    (200, 180,  60),   # kuning     - D-E-F-G
]

_C_BORDER      = (255, 200,  80)   # kuning-emas
_C_BORDER_IN   = (255, 255, 255)   # putih
_C_PAIR_LINE   = (200, 200, 230)   # abu-biru
_C_HUD_OK = ( 50, 220, 100)
_C_HUD_NO = ( 60,  60, 220)
_C_HUD_BG = ( 20,  20,  30)


# ----------------------------------------------------------------
#  BoxGesture
# ----------------------------------------------------------------
class BoxGesture:
    """
    State machine: IDLE <-> BOX_ACTIVE.

    Usage:
        box = BoxGesture()
        box.update(right_lms, left_lms)
        box.draw(frame)
        box.draw_hud(frame, right_lms, left_lms)
    """

    _THUMB_TIP = 4
    _INDEX_TIP = 8

    def __init__(self, pinch_threshold: float = PINCH_THRESHOLD):
        self.pinch_threshold = pinch_threshold
        self._state: str       = "IDLE"
        self._pts:   dict|None = None

    # ----------------------------------------------------------------
    #  Public API
    # ----------------------------------------------------------------

    def update(self, right_lms: list|None, left_lms: list|None) -> None:
        """Perbarui state dan posisi 10 sudut."""
        # Tidak ada tangan -> reset
        if right_lms is None and left_lms is None:
            if self._state in ["BOX_2_ACTIVE", "BOX_5_ACTIVE"]:
                self._state = "IDLE"
                self._pts   = None
            return

        right_pinch_type = self._get_pinch_type(right_lms)
        left_pinch_type  = self._get_pinch_type(left_lms)

        if self._state == "IDLE":
            if right_pinch_type == "5_FINGER" and left_pinch_type == "5_FINGER":
                self._state = "BOX_5_ACTIVE"
            elif right_pinch_type in ["2_FINGER", "5_FINGER"] and left_pinch_type in ["2_FINGER", "5_FINGER"]:
                self._state = "BOX_2_ACTIVE"
        else:
            # Mengizinkan transisi mode saat aktif
            if right_pinch_type == "5_FINGER" and left_pinch_type == "5_FINGER":
                self._state = "BOX_5_ACTIVE"
            elif right_pinch_type == "2_FINGER" and left_pinch_type == "2_FINGER":
                self._state = "BOX_2_ACTIVE"

        if self._state in ["BOX_2_ACTIVE", "BOX_5_ACTIVE"]:
            if right_lms and left_lms:
                self._pts = self._compute_points(right_lms, left_lms)

    def draw(self, frame: np.ndarray) -> None:
        """Gambar Hand Volume jika aktif."""
        if self._state not in ["BOX_2_ACTIVE", "BOX_5_ACTIVE"] or self._pts is None:
            return
        _draw_hand_volume(frame, self._pts, self._state)

    def draw_hud(
        self,
        frame:     np.ndarray,
        right_lms: list|None,
        left_lms:  list|None,
    ) -> None:
        """Badge status di pojok kanan bawah."""
        h, w = frame.shape[:2]
        right_p = self._get_pinch_type(right_lms)
        left_p  = self._get_pinch_type(left_lms)

        lines = [
            ("PINCH KANAN",  right_p != "NONE"),
            ("PINCH KIRI",   left_p != "NONE"),
            ("MODE 2 JARI",  self._state == "BOX_2_ACTIVE"),
            ("MODE 5 JARI",  self._state == "BOX_5_ACTIVE"),
        ]

        panel_w, panel_h = 210, 115
        px = w - panel_w - 10
        py = h - panel_h - 40

        _overlay_alpha(frame, px, py, px + panel_w, py + panel_h,
                       _C_HUD_BG, alpha=0.80)

        for i, (label, active) in enumerate(lines):
            col  = _C_HUD_OK if active else _C_HUD_NO
            icon = "+" if active else "-"
            cv2.putText(frame, f"{icon} {label}",
                        (px + 10, py + 24 + i * 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, col, 1, cv2.LINE_AA)

    @property
    def is_active(self) -> bool:
        return self._state in ["BOX_2_ACTIVE", "BOX_5_ACTIVE"]

    # ----------------------------------------------------------------
    #  Internal helpers
    # ----------------------------------------------------------------

    def _get_pinch_type(self, lms: list|None) -> str:
        if not lms or len(lms) < 21:
            return "NONE"
        tx, ty = lms[self._THUMB_TIP][1], lms[self._THUMB_TIP][2]
        ix, iy = lms[self._INDEX_TIP][1], lms[self._INDEX_TIP][2]
        mx, my = lms[12][1], lms[12][2]
        rx, ry = lms[16][1], lms[16][2]
        px, py = lms[20][1], lms[20][2]
        
        d_i = math.hypot(ix - tx, iy - ty)
        d_m = math.hypot(mx - tx, my - ty)
        d_r = math.hypot(rx - tx, ry - ty)
        d_p = math.hypot(px - tx, py - ty)

        if d_i < self.pinch_threshold:
            if d_m < self.pinch_threshold * 1.5 and d_r < self.pinch_threshold * 1.5 and d_p < self.pinch_threshold * 1.5:
                return "5_FINGER"
            return "2_FINGER"
        return "NONE"

    @staticmethod
    def _compute_points(right_lms: list, left_lms: list) -> dict:
        """
        Hitung 10 posisi ujung jari.

        Kiri  A=Kelingking(20) B=Manis(16) C=Tengah(12) D=Telunjuk(8) E=Jempol(4)
        Kanan F=Jempol(4)     G=Telunjuk(8) H=Tengah(12) I=Manis(16) J=Kelingking(20)
        """
        pts: dict = {}
        for label, tip_id in zip(_LEFT_LABELS, _LEFT_TIPS):
            if tip_id < len(left_lms):
                pts[label] = (left_lms[tip_id][1], left_lms[tip_id][2])
        for label, tip_id in zip(_RIGHT_LABELS, _RIGHT_TIPS):
            if tip_id < len(right_lms):
                pts[label] = (right_lms[tip_id][1], right_lms[tip_id][2])
        return pts


# ----------------------------------------------------------------
#  Rendering
# ----------------------------------------------------------------

def _draw_hand_volume(frame: np.ndarray, pts: dict, state: str) -> None:
    """Gambar Hand Volume dari 10 sudut atau 4 sudut tergantung state."""
    if not all(k in pts for k in _ALL_LABELS):
        return

    A, B, C, D, E = pts["A"], pts["B"], pts["C"], pts["D"], pts["E"]
    F, G, H, I, J = pts["F"], pts["G"], pts["H"], pts["I"], pts["J"]

    overlay = frame.copy()

    if state == "BOX_5_ACTIVE":
        # ── Fill muka pentagon kiri (A-B-C-D-E) ──────────────────────────────
        left_pts = np.array([A, B, C, D, E], dtype=np.int32)
        cv2.fillPoly(overlay, [left_pts], _C_FACE_LEFT)

        # ── Fill muka pentagon kanan (J-I-H-G-F, reversed winding) ───────────
        right_pts = np.array([J, I, H, G, F], dtype=np.int32)
        cv2.fillPoly(overlay, [right_pts], _C_FACE_RIGHT)

    cv2.addWeighted(overlay, 0.22, frame, 0.78, 0, frame)

    # ── Terapkan Efek Kamera pada Tiap Kotak Samping ────────────────────────
    if state == "BOX_5_ACTIVE":
        quad_effects = [
            ([A, B, I, J], "negative"),
            ([B, C, H, I], "stippling"),
            ([C, D, G, H], "cyanotype"),
            ([D, E, F, G], "risograph")
        ]
        active_pairs = _PAIRS
        left_labels_draw = _LEFT_LABELS
        right_labels_draw = _RIGHT_LABELS
        active_labels = _ALL_LABELS
    else: # BOX_2_ACTIVE
        quad_effects = [
            ([D, E, F, G], "risograph")
        ]
        active_pairs = [("D", "G"), ("E", "F")]
        left_labels_draw = ["D", "E"]
        right_labels_draw = ["F", "G"]
        active_labels = ["D", "E", "F", "G"]

    frame_h, frame_w = frame.shape[:2]

    for q_pts, effect_name in quad_effects:
        quad_arr = np.array(q_pts, dtype=np.int32)
        x, y, bw, bh = cv2.boundingRect(quad_arr)
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(frame_w, x + bw), min(frame_h, y + bh)

        if x2 <= x1 or y2 <= y1:
            continue

        roi = frame[y1:y2, x1:x2].copy()
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        eff_roi = np.zeros_like(roi)

        if effect_name == "negative":
            # Negatif (Invert Colors)
            eff_roi = 255 - roi

        elif effect_name == "cyanotype":
            # Map ke warna Cyanotype (Prussian Blue ke Putih)
            norm = gray.astype(np.float32) / 255.0
            eff_roi[:, :, 0] = (140 + norm * 115).astype(np.uint8)  # B
            eff_roi[:, :, 1] = (80 + norm * 160).astype(np.uint8)   # G
            eff_roi[:, :, 2] = (20 + norm * 200).astype(np.uint8)   # R

        elif effect_name == "risograph":
            # Risograph: Noise halftone dengan 2 warna spot (Blue & Pink)
            noise = np.random.randint(-40, 40, size=gray.shape, dtype=np.int16)
            noisy_gray = np.clip(gray.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            mask_dark = noisy_gray < 128
            mask_light = noisy_gray >= 128
            eff_roi[mask_dark] = (200, 50, 20)    # Blue (BGR)
            eff_roi[mask_light] = (150, 100, 255) # Pink (BGR)

        elif effect_name == "stippling":
            # Stippling: Bintik hitam pada latar putih
            norm = np.clip((gray.astype(np.float32) - 50) / 150.0, 0, 1)
            prob = 1.0 - norm
            rand = np.random.rand(*gray.shape)
            dots = (rand < prob)
            eff_roi.fill(255)
            eff_roi[dots] = (0, 0, 0)

        mask = np.zeros((frame_h, frame_w), dtype=np.uint8)
        cv2.fillPoly(mask, [quad_arr], 255)
        mask_roi = mask[y1:y2, x1:x2]

        idx = mask_roi > 0
        frame_roi = frame[y1:y2, x1:x2]
        frame_roi[idx] = eff_roi[idx]

    # ── Rusuk pasangan (A-J, B-I, C-H, D-G, E-F) ────────────────────────
    for l1, l2 in active_pairs:
        p1, p2 = pts[l1], pts[l2]
        cv2.line(frame, p1, p2, _C_PAIR_LINE,  2, cv2.LINE_AA)

    # ── Rusuk outline tangan kiri (A-B-C-D-E) ────────────────────────────
    for i in range(len(left_labels_draw) - 1):
        p1 = pts[left_labels_draw[i]]
        p2 = pts[left_labels_draw[i + 1]]
        cv2.line(frame, p1, p2, _C_BORDER,    3, cv2.LINE_AA)
        cv2.line(frame, p1, p2, _C_BORDER_IN, 1, cv2.LINE_AA)

    # ── Rusuk outline tangan kanan (F-G-H-I-J) ───────────────────────────
    for i in range(len(right_labels_draw) - 1):
        p1 = pts[right_labels_draw[i]]
        p2 = pts[right_labels_draw[i + 1]]
        cv2.line(frame, p1, p2, _C_BORDER,    3, cv2.LINE_AA)
        cv2.line(frame, p1, p2, _C_BORDER_IN, 1, cv2.LINE_AA)

    # ── Marker sudut dan label ────────────────────────────────────────────
    for label in active_labels:
        pt  = pts[label]
        col = _COLORS.get(label, _C_BORDER_IN)
        is_left = label in _LEFT_LABELS

        r = 10 if is_left else 9
        cv2.circle(frame, pt, r, col,        -1)
        cv2.circle(frame, pt, r, _C_BORDER,   2)
        cv2.circle(frame, pt, r + 1, (0,0,0), 1)

        # Offset label: kiri -> teks di kiri; kanan -> teks di kanan
        off_x = -22 if is_left else 13
        off_y = -7
        lx, ly = pt[0] + off_x, pt[1] + off_y
        cv2.putText(frame, label, (lx, ly), cv2.FONT_HERSHEY_DUPLEX,
                    0.50, _C_BORDER, 2, cv2.LINE_AA)
        cv2.putText(frame, label, (lx, ly), cv2.FONT_HERSHEY_DUPLEX,
                    0.50, (255, 255, 255), 1, cv2.LINE_AA)


# ----------------------------------------------------------------
#  Utility helpers
# ----------------------------------------------------------------

def _overlay_alpha(
    img:    np.ndarray,
    x1: int, y1: int, x2: int, y2: int,
    color:  tuple,
    alpha:  float = 0.70,
    radius: int   = 8,
) -> None:
    """Rectangle transparan dengan sudut membulat."""
    overlay = img.copy()
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    for cx, cy in [
        (x1 + radius, y1 + radius), (x2 - radius, y1 + radius),
        (x1 + radius, y2 - radius), (x2 - radius, y2 - radius),
    ]:
        cv2.circle(overlay, (cx, cy), radius, color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
