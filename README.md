# WebGIS Kesiapsiagaan Bencana Kota Semarang

Aplikasi WebGIS interaktif untuk pemetaan ketersediaan, jangkauan waktu tanggap (isochrone), dan evaluasi pemenuhan fasilitas darurat (Rumah Sakit, Puskesmas, Pemadam Kebakaran, dan Kantor Polisi) berdasarkan standar SNI 03-1733-2004 di Kota Semarang.

---

## Tentang Aplikasi

WebGIS Kesiapsiagaan Bencana Kota Semarang merupakan aplikasi berbasis web yang digunakan untuk membantu melihat kondisi kesiapsiagaan fasilitas darurat di wilayah Kota Semarang.

Aplikasi ini menggabungkan informasi mengenai ketersediaan fasilitas darurat, pemenuhan kebutuhan berdasarkan standar SNI, serta aksesibilitas fasilitas berdasarkan waktu tempuh. Hasil analisis kemudian divisualisasikan dalam bentuk peta interaktif sehingga informasi dapat lebih mudah dipahami dan digunakan untuk mengevaluasi kondisi kesiapsiagaan setiap kecamatan.

Fasilitas darurat yang dianalisis meliputi:

- Rumah Sakit
- Puskesmas
- Pemadam Kebakaran
- Kantor Polisi

---

## Tujuan

WebGIS ini dibuat untuk membantu:
- memetakan persebaran fasilitas darurat;
- mengetahui pemenuhan fasilitas berdasarkan standar SNI;
- melihat jangkauan fasilitas berdasarkan waktu tanggap;
- mengidentifikasi wilayah yang masih memiliki kekurangan fasilitas; dan
- menyajikan hasil analisis dalam bentuk peta interaktif.

---

## Fitur WebGIS

WebGIS Kesiapsiagaan Bencana Kota Semarang menyediakan beberapa fitur utama untuk membantu visualisasi dan evaluasi kesiapsiagaan fasilitas darurat, yaitu:

- **Peta Interaktif**  
  Menampilkan peta Kota Semarang beserta batas administrasi dan persebaran fasilitas darurat.

- **Persebaran Fasilitas Darurat**  
  Menampilkan lokasi Rumah Sakit, Puskesmas, Pemadam Kebakaran, dan Kantor Polisi.

- **Analisis Pemenuhan Fasilitas**  
  Menampilkan perbandingan antara jumlah fasilitas yang tersedia dengan kebutuhan berdasarkan standar SNI 03-1733-2004.

- **Analisis Aksesibilitas**  
  Menampilkan informasi tingkat aksesibilitas fasilitas berdasarkan jaringan jalan dan waktu tempuh.

- **Analisis Isochrone**  
  Menampilkan area yang dapat dijangkau fasilitas darurat berdasarkan batas waktu tanggap tertentu.

- **Indeks Kesiapsiagaan**  
  Menampilkan hasil indeks kesiapsiagaan pada masing-masing kecamatan di Kota Semarang.

- **Informasi Kecamatan**  
  Menampilkan informasi hasil analisis pada setiap wilayah kecamatan.

---

## Data yang Digunakan

Data yang digunakan dalam pengembangan WebGIS meliputi data spasial dan data atribut yang berkaitan dengan fasilitas darurat dan kondisi wilayah Kota Semarang.

Data yang digunakan antara lain:

- Batas administrasi kecamatan Kota Semarang.
- Data lokasi Rumah Sakit.
- Data lokasi Puskesmas.
- Data lokasi Pemadam Kebakaran.
- Data lokasi Kantor Polisi.
- Data jumlah penduduk.
- Data WorldPop.
- Data jaringan jalan.
- Data hasil analisis kebutuhan dan aksesibilitas fasilitas.

Data tersebut digunakan sebagai dasar dalam proses analisis dan visualisasi pada WebGIS.

---

## Teknologi yang Digunakan

Pengembangan WebGIS menggunakan beberapa teknologi dan perangkat lunak, antara lain:

- **HTML** — membangun struktur halaman WebGIS.
- **CSS** — mengatur tampilan dan antarmuka aplikasi.
- **JavaScript** — mengatur interaksi, visualisasi, dan fungsi analisis pada WebGIS.
- **Python** — digunakan untuk pengolahan dan analisis data spasial.
- **GeoJSON** — digunakan sebagai format data spasial untuk visualisasi pada WebGIS.
- **Visual Studio Code** — digunakan sebagai lingkungan pengembangan aplikasi.
- **Git dan GitHub** — digunakan untuk pengelolaan dan penyimpanan source code.

---

## Struktur Project

Struktur folder dan file utama pada project adalah sebagai berikut:

```text
WebGIS-Kesiapsiagaan-Bencana/
├── backend/        # Komponen backend aplikasi
├── data/           # Data spasial dan data pendukung
├── output/         # Hasil pengolahan dan analisis
├── processing/     # Script Python untuk pengolahan data
├── index.html      # Halaman utama WebGIS
├── script.js       # Script JavaScript aplikasi
├── style.css       # Pengaturan tampilan WebGIS
└── README.md       # Dokumentasi project
```

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

## Tahapan Pengerjaan

Pengembangan WebGIS Kesiapsiagaan Bencana Kota Semarang dilakukan melalui beberapa tahapan pengolahan data dan analisis spasial.

### 1. Persiapan dan Pengecekan Data

Tahap awal dilakukan dengan menyiapkan dan mengecek data yang akan digunakan dalam analisis. Data yang telah disiapkan kemudian diproses agar dapat digunakan pada tahapan analisis berikutnya.

### 2. Pengolahan Jaringan Jalan

Data jaringan jalan diolah untuk membentuk jaringan yang dapat digunakan dalam analisis aksesibilitas. Tahapan ini meliputi pembentukan jaringan, pembuatan graph, noding jaringan jalan, penyesuaian titik fasilitas terhadap jaringan, serta penyempurnaan jaringan.

### 3. Analisis Jarak dan Jalur

Jaringan jalan yang telah dibentuk digunakan untuk melakukan analisis jalur dan waktu tempuh. Hasil analisis digunakan sebagai dasar untuk mengetahui aksesibilitas fasilitas darurat terhadap wilayah di sekitarnya.

### 4. Analisis Aksesibilitas

Hasil pengolahan jaringan digunakan untuk menghitung nilai aksesibilitas fasilitas darurat. Nilai tersebut kemudian dinormalisasi dan diklasifikasikan untuk menghasilkan informasi tingkat aksesibilitas.

### 5. Analisis Kepadatan Jaringan Jalan

Kepadatan jaringan jalan dianalisis sebagai salah satu informasi yang mendukung penilaian aksesibilitas wilayah.

### 6. Perhitungan Kebutuhan Fasilitas Berdasarkan SNI

Kebutuhan fasilitas darurat pada setiap kecamatan dihitung berdasarkan standar SNI 03-1733-2004.

Jenis fasilitas yang dianalisis meliputi Rumah Sakit, Puskesmas, Pemadam Kebakaran, dan Kantor Polisi.

### 7. Evaluasi Ketersediaan Fasilitas

Jumlah fasilitas yang tersedia dibandingkan dengan kebutuhan fasilitas pada masing-masing kecamatan. Tahap ini digunakan untuk mengetahui tingkat pemenuhan serta mengidentifikasi kekurangan fasilitas.

### 8. Analisis Isochrone

Analisis isochrone digunakan untuk mengetahui jangkauan fasilitas berdasarkan waktu tanggap tertentu. Hasil analisis menunjukkan wilayah yang dapat dijangkau oleh fasilitas darurat dalam batas waktu yang telah ditentukan.

### 9. Perhitungan Indeks Kesiapsiagaan

Hasil analisis pemenuhan fasilitas dan aksesibilitas kemudian digunakan untuk menghasilkan indeks kesiapsiagaan. Hasil akhir diklasifikasikan untuk memberikan gambaran kondisi kesiapsiagaan pada masing-masing kecamatan.

### 10. Penggabungan Hasil

Seluruh hasil analisis kemudian digabungkan ke dalam data spasial yang digunakan oleh WebGIS sehingga informasi hasil pengolahan dapat divisualisasikan secara interaktif.

### 11. Visualisasi pada WebGIS

Tahap akhir adalah menampilkan hasil pengolahan dalam WebGIS. Pengguna dapat melihat persebaran fasilitas, indeks kesiapsiagaan, aksesibilitas, area jangkauan waktu tanggap, serta informasi hasil evaluasi pada setiap kecamatan.

---

## Reproduksi Analisis

Analisis pada WebGIS dapat dilakukan kembali menggunakan script yang terdapat pada folder `processing/`.

Secara umum, tahapan pengolahan dilakukan sebagai berikut:

### 1. Pengecekan dan Persiapan Data

Data spasial dan data atribut diperiksa untuk memastikan kelengkapan dan kesesuaiannya sebelum digunakan dalam analisis.

### 2. Pengolahan Jaringan Jalan

Jaringan jalan diproses untuk membentuk jaringan yang dapat digunakan dalam analisis aksesibilitas dan perhitungan jalur.

### 3. Pembentukan Network

Jaringan jalan dibentuk menjadi struktur jaringan yang dapat digunakan untuk menghitung hubungan antarsegmen jalan dan titik fasilitas.

### 4. Penyesuaian Titik Fasilitas

Lokasi fasilitas disesuaikan terhadap jaringan jalan sehingga dapat digunakan dalam analisis jalur dan waktu tempuh.

### 5. Analisis Jalur Terpendek

Analisis jalur digunakan untuk memperoleh jarak atau waktu tempuh dari fasilitas menuju wilayah yang dianalisis.

### 6. Normalisasi dan Klasifikasi

Nilai hasil analisis aksesibilitas dinormalisasi dan diklasifikasikan untuk menghasilkan informasi tingkat aksesibilitas.

### 7. Analisis Kebutuhan Fasilitas

Kebutuhan Rumah Sakit, Puskesmas, Pemadam Kebakaran, dan Kantor Polisi dihitung berdasarkan standar SNI 03-1733-2004.

### 8. Evaluasi Fasilitas

Jumlah fasilitas eksisting dibandingkan dengan kebutuhan fasilitas pada masing-masing kecamatan.

### 9. Analisis Isochrone

Jangkauan fasilitas berdasarkan waktu tanggap dihitung untuk mengetahui wilayah yang dapat dijangkau dalam batas waktu tertentu.

### 10. Perhitungan Indeks Kesiapsiagaan

Hasil evaluasi fasilitas dan aksesibilitas digunakan untuk menghasilkan indeks kesiapsiagaan setiap kecamatan.

### 11. Penggabungan Hasil

Hasil analisis digabungkan dengan data spasial untuk menghasilkan data akhir yang digunakan dalam WebGIS.

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

---

## Hasil yang Dihasilkan

Hasil pengolahan dan analisis pada project ini meliputi:

- data spasial fasilitas darurat;
- informasi pemenuhan fasilitas berdasarkan standar SNI;
- nilai dan klasifikasi aksesibilitas;
- hasil analisis kepadatan jaringan jalan;
- area jangkauan fasilitas berdasarkan waktu tanggap;
- indeks kesiapsiagaan setiap kecamatan; dan
- data spasial akhir yang digunakan untuk visualisasi pada WebGIS.

Hasil tersebut divisualisasikan dalam bentuk peta interaktif sehingga pengguna dapat melihat kondisi kesiapsiagaan fasilitas darurat pada masing-masing wilayah kecamatan di Kota Semarang.