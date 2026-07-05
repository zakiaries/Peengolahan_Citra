"""
==============================================
  BACKGROUND REMOVAL + FACE FILTER
  Menggunakan: OpenCV + MediaPipe
  Mata Kuliah: Pengelolaan Citra
  v5: Tambah fitur face filter [f]
==============================================

KONTROL:
  [1] Mode BG: Gambar   [2] Blur   [3] Warna Solid
  [a] / [d]  : Ganti background
  [f]        : Ganti filter wajah (off / kacamata / topi / hidung)
  [s]        : Screenshot
  [c]        : Ganti kamera
  [q]        : Keluar
"""

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import numpy as np
import os

# ──────────────────────────────────────────
# KONFIGURASI
# ──────────────────────────────────────────
BACKGROUND_FOLDER = "backgrounds"
FILTER_FOLDER     = "filters"          # folder PNG transparan filter
THRESHOLD         = 0.5

# ──────────────────────────────────────────
# SETUP MEDIAPIPE SELFIE SEGMENTATION
# ──────────────────────────────────────────
model_path  = "selfie_segmenter.tflite"
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
options      = vision.ImageSegmenterOptions(base_options=base_options,
                                            output_category_mask=True)
segmenter    = vision.ImageSegmenter.create_from_options(options)

# ──────────────────────────────────────────
# SETUP MEDIAPIPE FACE LANDMARKER (Tasks API)
# ──────────────────────────────────────────
face_model_path   = "face_landmarker.task"
face_base_options = mp.tasks.BaseOptions(model_asset_path=face_model_path)
face_options      = vision.FaceLandmarkerOptions(
    base_options=face_base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_faces=2,
    min_face_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
face_landmarker   = vision.FaceLandmarker.create_from_options(face_options)

# ──────────────────────────────────────────
# LANDMARK INDEX (FaceMesh 468 points)
# ──────────────────────────────────────────
# Mata kiri  (dari sudut dalam ke luar)
IDX_LEFT_EYE_INNER  = 133
IDX_LEFT_EYE_OUTER  = 33
# Mata kanan
IDX_RIGHT_EYE_INNER = 362
IDX_RIGHT_EYE_OUTER = 263
# Hidung
IDX_NOSE_TIP = 4
# Dahi / kepala atas
IDX_FOREHEAD = 10
# Dagu
IDX_CHIN     = 152
# Pipi kiri & kanan (untuk lebar wajah)
IDX_CHEEK_L  = 234
IDX_CHEEK_R  = 454

# ──────────────────────────────────────────
# FUNGSI OVERLAY PNG TRANSPARAN
# ──────────────────────────────────────────
def overlay_transparent(frame, overlay_bgra, x, y, w, h):
    """
    Tempelkan overlay_bgra (BGRA, 4-channel) ke frame (BGR)
    di posisi (x, y) dengan ukuran (w x h).
    """
    if w <= 0 or h <= 0:
        return frame

    overlay_resized = cv2.resize(overlay_bgra, (w, h), interpolation=cv2.INTER_AREA)

    # Kliping agar tidak keluar batas frame
    fh, fw = frame.shape[:2]
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, fw), min(y + h, fh)

    ox1 = x1 - x
    oy1 = y1 - y
    ox2 = ox1 + (x2 - x1)
    oy2 = oy1 + (y2 - y1)

    if ox2 <= ox1 or oy2 <= oy1:
        return frame

    roi     = frame[y1:y2, x1:x2]
    ovl_roi = overlay_resized[oy1:oy2, ox1:ox2]

    bgr   = ovl_roi[:, :, :3]
    alpha = ovl_roi[:, :, 3:4].astype(np.float32) / 255.0

    frame[y1:y2, x1:x2] = (bgr * alpha + roi * (1 - alpha)).astype(np.uint8)
    return frame

# ──────────────────────────────────────────
# FUNGSI BANTU: ambil koordinat piksel dari landmark
# ──────────────────────────────────────────
def lm_px(landmarks, idx, w, h):
    lm = landmarks[idx]
    return int(lm.x * w), int(lm.y * h)

# ──────────────────────────────────────────
# FUNGSI: TEMPEL FILTER KE WAJAH
# ──────────────────────────────────────────
def apply_face_filter(frame, filter_img, filter_name, landmarks):
    """
    Tempel filter_img (BGRA) ke frame berdasarkan posisi landmark.
    filter_name: 'glasses' | 'hat' | 'nose'
    """
    h, w = frame.shape[:2]

    if filter_name == "glasses":
        # Lebar = dari ujung luar mata kiri ke ujung luar mata kanan + padding
        lx, ly = lm_px(landmarks, IDX_LEFT_EYE_OUTER,  w, h)
        rx, ry = lm_px(landmarks, IDX_RIGHT_EYE_OUTER, w, h)

        eye_w = int(abs(rx - lx) * 1.4)
        eye_h = int(eye_w * 0.4)
        cx    = (lx + rx) // 2
        cy    = (ly + ry) // 2

        ox = cx - eye_w // 2
        oy = cy - eye_h // 2
        overlay_transparent(frame, filter_img, ox, oy, eye_w, eye_h)

    elif filter_name == "hat":
        # Lebar wajah = pipi kiri ke pipi kanan
        lx, _ = lm_px(landmarks, IDX_CHEEK_L, w, h)
        rx, _ = lm_px(landmarks, IDX_CHEEK_R, w, h)
        _, fy = lm_px(landmarks, IDX_FOREHEAD, w, h)   # y dahi

        face_w = int(abs(rx - lx) * 1.3)
        hat_h  = int(face_w * 0.85)
        cx     = (lx + rx) // 2

        ox = cx - face_w // 2
        oy = fy - hat_h          # di atas dahi
        overlay_transparent(frame, filter_img, ox, oy, face_w, hat_h)

    elif filter_name == "nose":
        nx, ny = lm_px(landmarks, IDX_NOSE_TIP, w, h)
        # Lebar hidung kira-kira 18% lebar wajah
        lx, _ = lm_px(landmarks, IDX_CHEEK_L, w, h)
        rx, _ = lm_px(landmarks, IDX_CHEEK_R, w, h)
        nose_w = int(abs(rx - lx) * 0.22)
        nose_h = int(nose_w * 0.7)
        ox = nx - nose_w // 2
        oy = ny - nose_h // 4
        overlay_transparent(frame, filter_img, ox, oy, nose_w, nose_h)

    return frame

# ──────────────────────────────────────────
# MUAT FILTER DARI FOLDER filters/
# ──────────────────────────────────────────
FILTER_MAP = {}   # name -> bgra image
FILTER_NAMES = ["glasses", "hat", "nose"]

os.makedirs(FILTER_FOLDER, exist_ok=True)
for fname in FILTER_NAMES:
    path = os.path.join(FILTER_FOLDER, f"{fname}.png")
    if os.path.exists(path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None and img.shape[2] == 4:
            FILTER_MAP[fname] = img
            print(f"  [+] Filter: {fname}.png")
        else:
            print(f"  [!] {fname}.png tidak valid (harus PNG dengan alpha / 4 channel)")
    else:
        print(f"  [!] {fname}.png tidak ditemukan di folder filters/")

# Filter aktif: -1 = off, 0..n = index ke FILTER_NAMES
active_filters = [k for k in FILTER_NAMES if k in FILTER_MAP]
filter_cycle   = [-1] + list(range(len(active_filters)))  # -1 = off
filter_pos     = 0   # posisi di filter_cycle

# ──────────────────────────────────────────
# DETEKSI KAMERA
# ──────────────────────────────────────────
def scan_cameras(max_index=5):
    available = []
    for i in range(max_index):
        cap_test = cv2.VideoCapture(i)
        if cap_test.isOpened():
            ret, _ = cap_test.read()
            if ret:
                available.append(i)
                print(f"  [+] Kamera ditemukan: index {i}")
        cap_test.release()
    return available

print("\n[INFO] Mendeteksi kamera...")
camera_list = scan_cameras()

if not camera_list:
    print("[ERROR] Tidak ada kamera ditemukan!")
    exit()

print(f"[INFO] Total kamera: {len(camera_list)} — {camera_list}\n")
cam_idx_pos = 0

def open_camera(cam_index):
    c = cv2.VideoCapture(cam_index)
    c.set(3, 640)
    c.set(4, 480)
    return c

cap = open_camera(camera_list[cam_idx_pos])

# ──────────────────────────────────────────
# MUAT BACKGROUND
# ──────────────────────────────────────────
list_img_bg = []
if os.path.exists(BACKGROUND_FOLDER):
    for fname in sorted(os.listdir(BACKGROUND_FOLDER)):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            img = cv2.imread(os.path.join(BACKGROUND_FOLDER, fname))
            if img is not None:
                img = cv2.resize(img, (640, 480))
                list_img_bg.append(img)
                print(f"  [+] Background: {fname}")

if not list_img_bg:
    print("[!] Folder 'backgrounds' kosong — default ke mode BLUR\n")

idx_bg     = 0
MODE       = 0 if list_img_bg else 1
SOLID_COLOR = (34, 139, 34)

print("\n========================================")
print("  BACKGROUND REMOVAL + FACE FILTER SIAP!")
print("  [1] Gambar  [2] Blur  [3] Warna Solid")
print("  [a]/[d] Ganti BG  [s] Screenshot")
print("  [f] Ganti Filter Wajah  [c] Ganti Kamera")
print("  [q] Keluar")
print("========================================\n")

screenshot_count = 0

# ──────────────────────────────────────────
# FUNGSI: HAPUS BACKGROUND
# ──────────────────────────────────────────
def remove_background(img_bgr, bg_bgr):
    img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

    result       = segmenter.segment(mp_image)
    mask_array   = result.category_mask.numpy_view()
    mask_float   = (mask_array == 0).astype(np.float32)
    mask_blur    = cv2.GaussianBlur(mask_float, (21, 21), 0)
    mask_3ch     = np.stack([mask_blur] * 3, axis=-1)

    bg = cv2.resize(bg_bgr, (img_bgr.shape[1], img_bgr.shape[0]))
    return (img_bgr * mask_3ch + bg * (1 - mask_3ch)).astype(np.uint8)

# ──────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────
while True:
    success, img = cap.read()
    if not success:
        print("[ERROR] Kamera tidak terbaca.")
        break

    # ── Background ──
    if MODE == 0 and list_img_bg:
        bg = list_img_bg[idx_bg]
    elif MODE == 1:
        bg = cv2.GaussianBlur(img, (55, 55), 0)
    else:
        bg = np.full_like(img, SOLID_COLOR, dtype=np.uint8)

    img_out = remove_background(img, bg)

    # ── Face Filter ──
    cur_filter_idx = filter_cycle[filter_pos]
    if cur_filter_idx >= 0 and active_filters:
        fname_active = active_filters[cur_filter_idx]
        filter_img   = FILTER_MAP[fname_active]

        img_rgb   = cv2.cvtColor(img_out, cv2.COLOR_BGR2RGB)
        mp_face   = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        results   = face_landmarker.detect(mp_face)

        if results.face_landmarks:
            for face_landmarks in results.face_landmarks:
                apply_face_filter(img_out, filter_img,
                                  fname_active, face_landmarks)

    # ── HUD: baris atas ──
    mode_labels = {0: "GAMBAR", 1: "BLUR", 2: "SOLID"}
    label = f"Mode: {mode_labels.get(MODE, '-')}"
    if MODE == 0 and list_img_bg:
        label += f"  BG {idx_bg + 1}/{len(list_img_bg)}"
    label += f"  Cam {camera_list[cam_idx_pos]}"

    filter_label = "Filter: OFF"
    if cur_filter_idx >= 0 and active_filters:
        filter_label = f"Filter: {active_filters[cur_filter_idx].upper()}"
    elif not active_filters:
        filter_label = "Filter: (tidak ada aset)"

    overlay = img_out.copy()
    cv2.rectangle(overlay, (0, 0), (640, 50), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, img_out, 0.5, 0, img_out)
    cv2.putText(img_out, label,        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)
    cv2.putText(img_out, filter_label, (10, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 200), 2)

    # ── HUD: baris bawah ──
    cv2.putText(img_out,
                "[q] Keluar | [1][2][3] Mode | [a][d] BG | [f] Filter | [s] Foto | [c] Kamera",
                (10, 472), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (200, 200, 200), 1)

    cv2.imshow("Background Removal + Face Filter", img_out)

    key = cv2.waitKey(1) & 0xFF
    if 65 <= key <= 90:          # huruf besar A-Z -> kecil a-z (kebal Caps Lock)
        key += 32

    if key == ord('q'):
        print("[INFO] Keluar.")
        break

    elif key == ord('f'):
        filter_pos = (filter_pos + 1) % len(filter_cycle)
        idx = filter_cycle[filter_pos]
        name = active_filters[idx] if idx >= 0 else "OFF"
        print(f"[INFO] Filter: {name.upper()}")

    elif key == ord('c'):
        if len(camera_list) <= 1:
            print("[INFO] Hanya 1 kamera.")
        else:
            cap.release()
            cam_idx_pos = (cam_idx_pos + 1) % len(camera_list)
            cap = open_camera(camera_list[cam_idx_pos])
            print(f"[INFO] Ganti kamera: {camera_list[cam_idx_pos]}")

    elif key == ord('d') and list_img_bg:
        idx_bg = (idx_bg + 1) % len(list_img_bg)
    elif key == ord('a') and list_img_bg:
        idx_bg = (idx_bg - 1) % len(list_img_bg)

    elif key == ord('1'):
        if list_img_bg: MODE = 0
        print("[INFO] Mode: Gambar")
    elif key == ord('2'):
        MODE = 1
        print("[INFO] Mode: Blur")
    elif key == ord('3'):
        MODE = 2
        print("[INFO] Mode: Warna Solid")

    elif key == ord('s'):
        fname = f"screenshot_{screenshot_count:03d}.jpg"
        cv2.imwrite(fname, img_out)
        screenshot_count += 1
        print(f"[INFO] Screenshot: {fname}")

cap.release()
cv2.destroyAllWindows()
face_landmarker.close()
