# WebGIS Kesiapsiagaan Bencana Kota Semarang

Aplikasi WebGIS interaktif untuk pemetaan ketersediaan, jangkauan waktu tanggap (isochrone), dan evaluasi pemenuhan fasilitas darurat (Rumah Sakit, Puskesmas, Pemadam Kebakaran, dan Kantor Polisi) berdasarkan standar SNI 03-1733-2004 di Kota Semarang.

---

## Cara Menjalankan Project

Pilih salah satu cara mendapatkan kode project di bawah ini:

### 1. Mendapatkan Kode Project

#### Opsi A: Menggunakan Git (Rekomendasi)
Jika baru pertama kali:
```bash
git clone https://github.com/firaaagstnnn30/WebGIS-Kesiapsiagaan-Bencana.git
cd WebGIS-Kesiapsiagaan-Bencana
```
Jika sudah pernah clone dan ingin memperbarui kode ke versi terbaru:
```bash
git pull origin main
```

#### Opsi B: Download ZIP (Tanpa Git)
1. Buka repository GitHub di browser: https://github.com/firaaagstnnn30/WebGIS-Kesiapsiagaan-Bencana
2. Klik tombol **Code** lalu pilih **Download ZIP**.
3. Ekstrak file ZIP tersebut di komputer Anda.
4. Buka terminal atau command prompt dan masuk ke folder hasil ekstrak:
   ```bash
   cd WebGIS-Kesiapsiagaan-Bencana-main
   ```

---

### 2. Menjalankan Tampilan WebGIS di Browser

Karena aplikasi ini membaca data spasial (.geojson) menggunakan fungsi fetch(), halaman web wajib dijalankan melalui web server lokal (bukan klik ganda file index.html langsung) untuk menghindari pembatasan keamanan browser (CORS).

#### Cara 1: Menggunakan Python (Paling Praktis)
Buka terminal di folder project, lalu jalankan:

**Linux / macOS / Windows:**
```bash
python3 -m http.server 8000
```
*(Atau gunakan `python -m http.server 8000` jika perintah `python3` tidak dikenali pada Windows)*.

Setelah muncul tulisan:
```text
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```
Buka browser dan akses alamat:
**http://localhost:8000**

> Catatan: Untuk menghentikan server, tekan `Ctrl + C` di terminal.

#### Cara 2: Menggunakan VS Code (Ekstensi Live Server)
1. Buka folder project di Visual Studio Code.
2. Pasang ekstensi **Live Server** dari menu Extensions (Ctrl + Shift + X).
3. Klik kanan pada file `index.html` lalu pilih **Open with Live Server**.
4. Halaman WebGIS akan terbuka otomatis di browser default Anda.

---

## Menjalankan Script Pengolahan Data (Opsional)

Folder `processing/` berisi script Python untuk pemodelan GIS dan analisis spasial. Bagian ini hanya perlu dijalankan apabila Anda ingin mengolah ulang data mentah:

### 1. Instalasi Dependensi Python
```bash
pip install geopandas pandas shapely
```

### 2. Urutan Menjalankan Script Analisis
```bash
# 1. Menghitung kebutuhan fasilitas berdasarkan SNI
python3 processing/16_kebutuhan_sni.py

# 2. Evaluasi ketersediaan fasilitas eksisting vs kebutuhan
python3 processing/17_evaluasi_fasilitas.py

# 3. Perhitungan indeks final gabungan
python3 processing/18_indeks_final.py

# 4. Penggabungan atribut ke GeoJSON akhir untuk WebGIS
python3 processing/15_gabung_hasil.py
```
