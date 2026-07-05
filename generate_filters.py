"""
==============================================
  GENERATOR ASET FILTER WAJAH
  Jalankan sekali untuk membuat folder filters/
  berisi: glasses.png, hat.png, nose.png
==============================================
  Jalankan: python generate_filters.py
"""

import cv2
import numpy as np
import os

os.makedirs("filters", exist_ok=True)

# ──────────────────────────────────────────
# 1. KACAMATA (glasses.png)
# ──────────────────────────────────────────
W, H = 400, 160
canvas = np.zeros((H, W, 4), dtype=np.uint8)   # BGRA transparan

frame_color = (30, 30, 30, 255)    # hitam
lens_color  = (200, 230, 255, 120) # biru muda semi transparan
bridge_color = (30, 30, 30, 255)

# Lensa kiri
cv2.ellipse(canvas, (100, 80), (70, 50), 0, 0, 360, lens_color, -1)
cv2.ellipse(canvas, (100, 80), (70, 50), 0, 0, 360, frame_color,  6)

# Lensa kanan
cv2.ellipse(canvas, (300, 80), (70, 50), 0, 0, 360, lens_color, -1)
cv2.ellipse(canvas, (300, 80), (70, 50), 0, 0, 360, frame_color,  6)

# Jembatan tengah
cv2.line(canvas, (170, 80), (230, 80), bridge_color, 6)

# Gagang kiri & kanan
cv2.line(canvas, (30,  80), (0,   60), frame_color, 6)
cv2.line(canvas, (370, 80), (400, 60), frame_color, 6)

cv2.imwrite("filters/glasses.png", canvas)
print("[+] filters/glasses.png dibuat")

# ──────────────────────────────────────────
# 2. TOPI ULANG TAHUN (hat.png)
# ──────────────────────────────────────────
W, H = 300, 340
canvas = np.zeros((H, W, 4), dtype=np.uint8)

hat_color    = (0, 30, 220, 255)   # merah
stripe_color = (0, 220, 220, 255)  # kuning
pom_color    = (255, 255, 255, 255)

# Badan topi (segitiga)
pts = np.array([[150, 10], [20, 310], [280, 310]], dtype=np.int32)
cv2.fillPoly(canvas, [pts], hat_color)

# Garis-garis diagonal lucu
for i in range(3):
    y_offset = 80 + i * 75
    p1 = np.array([150, 10])
    p2 = np.array([20,  310])
    p3 = np.array([280, 310])
    # interpolasi titik di tepi kiri dan kanan topi
    t1 = (y_offset - 10) / 300
    t2 = (y_offset - 10) / 300
    lx = int(p1[0] + t1 * (p2[0] - p1[0]))
    rx = int(p1[0] + t2 * (p3[0] - p1[0]))
    cv2.line(canvas,
             (max(lx - 40, 20),  y_offset),
             (min(rx + 40, 280), y_offset),
             stripe_color, 8)

# Tumpul bawah topi
cv2.rectangle(canvas, (10, 305), (290, 340), (180, 180, 180, 255), -1)
cv2.rectangle(canvas, (10, 305), (290, 340), (100, 100, 100, 255),  3)

# Pompom di atas
cv2.circle(canvas, (150, 15), 22, pom_color, -1)

cv2.imwrite("filters/hat.png", canvas)
print("[+] filters/hat.png dibuat")

# ──────────────────────────────────────────
# 3. HIDUNG BADUT (nose.png)
# ──────────────────────────────────────────
W, H = 120, 100
canvas = np.zeros((H, W, 4), dtype=np.uint8)

# Bola merah
cv2.circle(canvas, (60, 50), 45, (0, 0, 220, 255), -1)

# Highlight putih agar terlihat 3D
cv2.circle(canvas, (42, 35), 12, (255, 255, 255, 160), -1)

cv2.imwrite("filters/nose.png", canvas)
print("[+] filters/nose.png dibuat")

print("\nSelesai! Folder filters/ siap dipakai.")
print("Jalankan: python background_removal.py")
