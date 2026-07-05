# NASKAH PRESENTASI VIDEO
## Background Removal + Face Filter (OpenCV + MediaPipe)
**Mata Kuliah: Pengelolaan Citra**

> Total estimasi durasi: ± 7–9 menit
> Tips: kalimat yang **dicetak tebal** adalah penekanan; teks _miring_ adalah arahan aksi (bukan dibaca).

---

## BAGIAN 1 — PEMBUKAAN (± 30 detik)

"Assalamualaikum / Halo semuanya. Perkenalkan, nama saya **[Nama Anda]**.
Pada video ini saya akan mempresentasikan project tugas Pengelolaan Citra saya yang berjudul
**Background Removal dan Face Filter secara real-time** menggunakan **OpenCV** dan **MediaPipe**.

Singkatnya, aplikasi ini bisa **mengganti latar belakang** kita seperti di Zoom atau Google Meet,
dan juga menambahkan **filter wajah** seperti kacamata, topi, dan hidung badut — semuanya
langsung dari kamera secara real-time."

---

## BAGIAN 2 — LATAR BELAKANG & TUJUAN (± 45 detik)

"Latar belakang project ini sederhana. Saat video call atau membuat konten,
kita sering ingin **menyembunyikan latar belakang** yang berantakan, atau menambahkan
**efek filter** yang menarik. Biasanya ini butuh aplikasi berat atau green screen.

Tujuan saya adalah membuktikan bahwa dengan **pengolahan citra** dan **model AI ringan**,
hal tersebut bisa dilakukan **tanpa green screen**, hanya bermodal **satu webcam biasa**.

Ada dua fitur utama yang saya bangun:
1. **Background Removal** — memisahkan tubuh dari latar, lalu menggantinya.
2. **Face Filter** — menempelkan aksesoris ke wajah mengikuti gerakan kepala."

---

## BAGIAN 3 — TEKNOLOGI YANG DIPAKAI (± 45 detik)

"Teknologi yang saya gunakan ada tiga:

- **OpenCV**, untuk menangkap gambar dari kamera dan mengolah citra seperti blur dan penggabungan gambar.
- **MediaPipe Selfie Segmentation**, model AI dari Google untuk **memisahkan orang dari background**.
- **MediaPipe Face Landmarker**, model AI yang mendeteksi **468 titik wajah**,
  sehingga filter bisa menempel tepat di mata, dahi, dan hidung.

Jadi konsep intinya: AI memberi tahu kita **'di mana orangnya'** dan **'di mana wajahnya'**,
lalu OpenCV mengolah gambarnya."

---

## BAGIAN 4 — PENJELASAN KODE (± 3–4 menit)

> _Buka file background_removal.py, scroll ke fungsi yang sedang dijelaskan._

### 4a. Fungsi `remove_background()` — penghapus background

"Pertama, fungsi paling penting: **`remove_background`**.

Cara kerjanya:
- Gambar dari kamera saya kirim ke model **segmenter** MediaPipe.
- Model mengembalikan sebuah **mask**, yaitu peta hitam-putih yang menandai
  **mana piksel orang, dan mana piksel background**.
- Mask ini saya **blur** sedikit, supaya pinggiran tubuh terlihat halus, tidak bergerigi.
- Terakhir, saya gabungkan dengan rumus:
  **(gambar orang × mask) + (background × (1 − mask))**.

Hasilnya: tubuh saya tetap tampil, tapi latar belakangnya berganti sesuai pilihan."

### 4b. Tiga mode background

"Aplikasi ini punya **tiga mode** latar belakang yang bisa diganti dengan tombol angka:
- Tombol **1**: latar berupa **gambar** dari folder backgrounds.
- Tombol **2**: latar di-**blur**, seperti efek bokeh di Zoom.
- Tombol **3**: latar **warna solid**, misalnya hijau."

### 4c. Fungsi `apply_face_filter()` — penempel filter

"Berikutnya fitur kedua, **`apply_face_filter`**.

Setelah model mendeteksi titik-titik wajah, fungsi ini menghitung
**posisi dan ukuran** filter berdasarkan wajah:
- **Kacamata** diukur dari ujung mata kiri ke ujung mata kanan.
- **Topi** diukur dari pipi kiri ke kanan, lalu diletakkan di atas dahi.
- **Hidung badut** diletakkan tepat di ujung hidung.

Karena memakai titik wajah, filter akan **mengikuti gerakan kepala** secara otomatis."

### 4d. Fungsi `overlay_transparent()` — alpha blending

"Lalu bagaimana filter bisa menempel mulus tanpa kotak persegi di sekelilingnya?
Itu tugas fungsi **`overlay_transparent`**.

Filter saya simpan sebagai **PNG transparan**. Fungsi ini melakukan **alpha blending**:
bagian transparan dibuat tembus pandang, sehingga **hanya bentuk kacamata atau topinya**
yang terlihat menempel di wajah, bukan latar kotaknya."

### 4e. Fungsi pendukung

"Ada juga beberapa fungsi pendukung:
- **`lm_px`** mengubah koordinat titik wajah menjadi koordinat piksel layar.
- **`scan_cameras`** dan **`open_camera`** untuk mendeteksi dan berpindah kamera.
- File terpisah **`generate_filters.py`** yang saya jalankan sekali
  untuk **menggambar aset** kacamata, topi, dan hidung memakai OpenCV."

---

## BAGIAN 5 — DEMO LANGSUNG (± 2 menit)

> _Jalankan program: `python background_removal.py`. Tunjukkan wajah ke kamera._

"Sekarang saya demokan langsung.

_(Tekan 1)_ Ini **mode gambar** — latar belakang saya sudah berganti jadi gambar.
_(Tekan a / d)_ Saya bisa **mengganti-ganti** gambar latarnya.
_(Tekan 2)_ Ini **mode blur**, latar belakang menjadi buram.
_(Tekan 3)_ Dan ini **mode warna solid**.

_(Tekan f berkali-kali)_ Sekarang fitur filter. Saya tekan tombol **f**:
muncul **kacamata**... tekan lagi jadi **topi**... tekan lagi jadi **hidung badut**.
Perhatikan, saat kepala saya bergerak, filternya **tetap mengikuti**.

_(Tekan s)_ Saya juga bisa **screenshot** hasilnya dengan tombol **s**.
_(Goyangkan kepala / dekat-jauhkan wajah untuk menunjukkan tracking)_"

---

## BAGIAN 6 — KESIMPULAN & PENUTUP (± 45 detik)

"Kesimpulannya, project ini berhasil melakukan **penghapusan background**
dan **filter wajah secara real-time** hanya dengan webcam biasa, **tanpa green screen**.

Dari sini saya belajar konsep penting dalam pengolahan citra, yaitu **segmentation**,
**masking**, **alpha blending**, dan **deteksi landmark wajah**.

Untuk pengembangan ke depan, aplikasi ini bisa ditambah filter yang lebih banyak,
atau perekaman video.

Sekian presentasi dari saya. Terima kasih sudah menonton.
Wassalamualaikum / Sampai jumpa."

---

## LAMPIRAN — DAFTAR TOMBOL (untuk ditampilkan di layar)

| Tombol | Fungsi |
|--------|--------|
| 1 / 2 / 3 | Mode background: Gambar / Blur / Solid |
| a / d | Ganti gambar background |
| f | Ganti filter wajah (off → kacamata → topi → hidung) |
| s | Screenshot |
| c | Ganti kamera |
| q | Keluar |
