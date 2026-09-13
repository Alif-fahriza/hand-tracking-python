"""
Hand Tracker Module — MediaPipe Tasks API v1.0
===============================================
Modul utama untuk mendeteksi dan melacak tangan menggunakan MediaPipe Tasks API.
Kompatibel dengan MediaPipe >= 1.0.0

Tahap 1: Membaca jari jemari (finger detection & landmark tracking)
Tahap 2: Pinch-to-Draw Box (rotated rectangle dari 4 landmark)
"""

import cv2
import math
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# Koneksi antar landmark untuk menggambar skeleton tangan
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Jempol
    (0, 5), (5, 6), (6, 7), (7, 8),       # Telunjuk
    (0, 9), (9, 10), (10, 11), (11, 12),  # Tengah
    (0, 13), (13, 14), (14, 15), (15, 16), # Manis
    (0, 17), (17, 18), (18, 19), (19, 20), # Kelingking
    (5, 9), (9, 13), (13, 17),             # Sambungan telapak
]


class HandTracker:
    """
    Kelas utama untuk mendeteksi tangan dan membaca posisi jari-jemari.
    Menggunakan MediaPipe Tasks API (v1.0+).
    """

    # ID Landmark untuk setiap ujung jari (tip)
    FINGER_TIPS = {
        "THUMB":  4,
        "INDEX":  8,
        "MIDDLE": 12,
        "RING":   16,
        "PINKY":  20,
    }

    # ID Landmark untuk sendi pangkal setiap jari (pip / mcp untuk jempol)
    FINGER_MCP = {
        "THUMB":  2,   # IP joint jempol
        "INDEX":  6,   # PIP joint telunjuk
        "MIDDLE": 10,  # PIP joint tengah
        "RING":   14,  # PIP joint manis
        "PINKY":  18,  # PIP joint kelingking
    }

    def __init__(
        self,
        model_path: str = "hand_landmarker.task",
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
    ):
        """
        Inisialisasi HandTracker dengan MediaPipe Tasks API.

        Args:
            model_path: Path ke file model .task dari MediaPipe.
            max_num_hands: Jumlah maksimum tangan yang dideteksi.
            min_detection_confidence: Confidence minimum untuk deteksi.
            min_tracking_confidence: Confidence minimum untuk tracking.
            min_presence_confidence: Confidence minimum untuk kehadiran tangan.
        """
        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            min_hand_presence_confidence=min_presence_confidence,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._result = None          # Hasil deteksi terakhir
        self.landmark_list = []      # Cache landmark untuk tangan aktif
        self._frame_ts = 0           # Timestamp frame (ms) untuk VIDEO mode

    # ------------------------------------------------------------------ #
    #  Core Detection                                                      #
    # ------------------------------------------------------------------ #

    def find_hands(self, frame, draw: bool = True):
        """
        Proses frame BGR untuk mendeteksi tangan.

        Args:
            frame: Frame BGR dari OpenCV (numpy array).
            draw: Jika True, gambar skeleton & landmark di frame.

        Returns:
            Frame yang sudah diproses.
        """
        # Konversi BGR → RGB untuk MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Increment timestamp (VIDEO mode butuh timestamp monoton)
        self._frame_ts += 33  # ~30 FPS
        self._result = self._landmarker.detect_for_video(mp_image, self._frame_ts)

        if draw and self._result.hand_landmarks:
            h, w = frame.shape[:2]
            for hand_lms in self._result.hand_landmarks:
                self._draw_landmarks(frame, hand_lms, h, w)

        return frame

    def _draw_landmarks(self, frame, hand_lms, h: int, w: int):
        """Gambar landmark dan koneksi pada frame menggunakan OpenCV."""
        points = []
        for lm in hand_lms:
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            points.append((cx, cy))

        # Gambar koneksi (garis skeleton)
        for start, end in HAND_CONNECTIONS:
            cv2.line(frame, points[start], points[end], (80, 200, 120), 2)

        # Gambar titik landmark
        for i, (cx, cy) in enumerate(points):
            if i in (4, 8, 12, 16, 20):  # Ujung jari: lebih besar
                cv2.circle(frame, (cx, cy), 8, (255, 255, 255), -1)
                cv2.circle(frame, (cx, cy), 8, (0, 255, 100), 2)
            elif i == 0:  # Pergelangan
                cv2.circle(frame, (cx, cy), 10, (200, 200, 255), -1)
            else:
                cv2.circle(frame, (cx, cy), 5, (200, 200, 200), -1)

    # ------------------------------------------------------------------ #
    #  Landmark Access                                                     #
    # ------------------------------------------------------------------ #

    def find_position(self, frame, hand_no: int = 0) -> list[tuple[int, int, int]]:
        """
        Dapatkan posisi pixel semua 21 landmark untuk tangan tertentu.

        Args:
            frame: Frame BGR dari OpenCV (digunakan untuk mendapatkan dimensi).
            hand_no: Indeks tangan (0 = tangan pertama).

        Returns:
            List berisi tuple (id, x, y). Kosong jika tidak terdeteksi.
        """
        result = []
        if not self._result or not self._result.hand_landmarks:
            return result
        if hand_no >= len(self._result.hand_landmarks):
            return result

        h, w = frame.shape[:2]
        for idx, lm in enumerate(self._result.hand_landmarks[hand_no]):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            result.append((idx, cx, cy))

        self.landmark_list = result
        return result

    def get_landmark(self, landmark_id: int, hand_no: int = 0) -> tuple | None:
        """
        Dapatkan posisi satu landmark tertentu.

        Returns:
            Tuple (id, x, y) atau None.
        """
        if self.landmark_list and landmark_id < len(self.landmark_list):
            return self.landmark_list[landmark_id]
        return None

    # ------------------------------------------------------------------ #
    #  Finger Analysis                                                     #
    # ------------------------------------------------------------------ #

    def get_open_fingers(self, lms: list | None = None) -> list[str]:
        """
        Tentukan jari mana yang sedang terbuka berdasarkan posisi landmark.

        Args:
            lms: List (id, x, y) dari find_position(). Gunakan self.landmark_list
                 jika None.

        Returns:
            List nama jari yang terbuka, misal: ['INDEX', 'MIDDLE'].
        """
        if lms is None:
            lms = self.landmark_list
        if not lms:
            return []

        open_fingers = []

        # Jempol: bandingkan koordinat X
        # Jika ujung jempol lebih ke kanan dari sendi bawahnya → terbuka
        thumb_tip_x = lms[self.FINGER_TIPS["THUMB"]][1]
        thumb_mcp_x = lms[self.FINGER_MCP["THUMB"]][1]
        if thumb_tip_x > thumb_mcp_x:
            open_fingers.append("THUMB")

        # Empat jari lain: bandingkan koordinat Y
        # Jika ujung jari lebih tinggi (y lebih kecil) dari sendi → terbuka
        for name in ("INDEX", "MIDDLE", "RING", "PINKY"):
            tip_y = lms[self.FINGER_TIPS[name]][2]
            mcp_y = lms[self.FINGER_MCP[name]][2]
            if tip_y < mcp_y:
                open_fingers.append(name)

        return open_fingers

    def count_fingers(self, lms: list | None = None) -> int:
        """Hitung jumlah jari yang terbuka (0–5)."""
        return len(self.get_open_fingers(lms))

    def get_distance(self, lm_id_1: int, lm_id_2: int) -> float:
        """
        Hitung jarak Euclidean antara dua landmark (dalam pixel).

        Returns:
            Jarak dalam pixel. -1.0 jika landmark tidak tersedia.
        """
        p1 = self.get_landmark(lm_id_1)
        p2 = self.get_landmark(lm_id_2)
        if p1 and p2:
            return math.hypot(p2[1] - p1[1], p2[2] - p1[2])
        return -1.0

    # ------------------------------------------------------------------ #
    #  Hand Info                                                           #
    # ------------------------------------------------------------------ #

    def num_hands_detected(self) -> int:
        """Kembalikan jumlah tangan yang saat ini terdeteksi."""
        if self._result and self._result.hand_landmarks:
            return len(self._result.hand_landmarks)
        return 0

    def get_hand_label(self, hand_no: int = 0) -> str | None:
        """
        Dapatkan label tangan ('Left' atau 'Right').

        Returns:
            'Left', 'Right', atau None.
        """
        if self._result and self._result.handedness:
            if hand_no < len(self._result.handedness):
                return self._result.handedness[hand_no][0].display_name
        return None

    def get_landmarks_both_hands(self, frame) -> dict:
        """
        Dapatkan landmark untuk kedua tangan sekaligus, dikelompokkan
        berdasarkan label 'Left' / 'Right'.

        Args:
            frame: Frame BGR dari OpenCV (digunakan untuk mendapatkan dimensi).

        Returns:
            Dict {'Left': lms_or_None, 'Right': lms_or_None}
            di mana lms adalah list[(id, x, y)] dari find_position().
        """
        result = {"Left": None, "Right": None}
        if not self._result or not self._result.hand_landmarks:
            return result

        num = len(self._result.hand_landmarks)
        for hand_no in range(num):
            label = self.get_hand_label(hand_no)  # 'Left' atau 'Right'
            if label in result:
                result[label] = self.find_position(frame, hand_no)
        return result

    def is_pinching(
        self,
        lms: list,
        threshold: float = 50.0,
    ) -> bool:
        """
        Cek apakah tangan dalam posisi pinch (jempol & telunjuk berdekatan).

        Args:
            lms  : List (id, x, y) dari find_position().
            threshold: Jarak maksimum (pixel) agar dianggap pinch.

        Returns:
            True jika jarak landmark 4 (jempol) dan 8 (telunjuk) < threshold.
        """
        if not lms or len(lms) < 9:
            return False
        thumb_x,  thumb_y  = lms[4][1], lms[4][2]
        index_x,  index_y  = lms[8][1], lms[8][2]
        import math
        dist = math.hypot(index_x - thumb_x, index_y - thumb_y)
        return dist < threshold

    def release(self):
        """Lepaskan resource MediaPipe."""
        if self._landmarker:
            self._landmarker.close()
