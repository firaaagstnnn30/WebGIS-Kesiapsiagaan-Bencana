import geopandas as gpd
import pandas as pd
import math
import os

# ============================================================
# 1. PENGATURAN FILE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_ADMIN = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "administrasi.geojson"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "output"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 2. BACA DATA ADMINISTRASI
# ============================================================

print("=" * 60)
print("ANALISIS KEBUTUHAN FASILITAS BERDASARKAN SNI 03-1733-2004")
print("=" * 60)

admin = gpd.read_file(FILE_ADMIN)

print("\nJumlah kecamatan :", len(admin))
print("Kolom data       :", list(admin.columns))

# ============================================================
# 3. KONVERSI DATA PENDUDUK
# ============================================================

if "Penduduk" not in admin.columns:
    raise ValueError(
        "Kolom 'Penduduk' tidak ditemukan di administrasi.geojson"
    )

# Data penduduk menggunakan titik sebagai pemisah ribuan
# Contoh:
# 144.087 -> 144087
# 75.396  -> 75396

admin["Penduduk"] = (
    admin["Penduduk"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
)

admin["Penduduk"] = pd.to_numeric(
    admin["Penduduk"],
    errors="coerce"
)

# Cek data kosong
if admin["Penduduk"].isna().any():
    print("\nPERINGATAN: Ada data penduduk yang kosong!")

    print(
        admin.loc[
            admin["Penduduk"].isna(),
            ["NAME_3", "Penduduk"]
        ]
    )

    raise ValueError(
        "Periksa kembali kolom Penduduk sebelum melanjutkan."
    )
# ============================================================
# 4. STANDAR KAPASITAS PELAYANAN FASILITAS
# ============================================================

# Standar pelayanan berdasarkan jumlah penduduk:
# Rumah Sakit (RS)         = 1 fasilitas / 240.000 jiwa
# Puskesmas                 = 1 fasilitas / 120.000 jiwa
# Pos Pemadam Kebakaran     = 1 fasilitas / 90.000 jiwa
# Kantor Polisi             = 1 fasilitas / 30.000 jiwa

PENDUDUK_RS = 240000
PENDUDUK_PUSKESMAS = 120000
PENDUDUK_DAMKAR = 90000
PENDUDUK_POLISI = 30000

# ============================================================
# 5. HITUNG KEBUTUHAN FASILITAS
# ============================================================

admin["kebutuhan_rumah_sakit"] = (
    admin["Penduduk"]
    .apply(lambda x: math.ceil(x / PENDUDUK_RS))
)

admin["kebutuhan_puskesmas"] = (
    admin["Penduduk"]
    .apply(lambda x: math.ceil(x / PENDUDUK_PUSKESMAS))
)

admin["kebutuhan_pos_damkar"] = (
    admin["Penduduk"]
    .apply(lambda x: math.ceil(x / PENDUDUK_DAMKAR))
)

admin["kebutuhan_kantor_polisi"] = (
    admin["Penduduk"]
    .apply(lambda x: math.ceil(x / PENDUDUK_POLISI))
)

# ============================================================
# 6. TABEL HASIL
# ============================================================

hasil = admin[
    [
        "GID_3",
        "NAME_3",
        "Penduduk",
        "kebutuhan_rumah_sakit",
        "kebutuhan_puskesmas",
        "kebutuhan_pos_damkar",
        "kebutuhan_kantor_polisi"
    ]
].copy()

# ============================================================
# 7. TAMPILKAN HASIL
# ============================================================

print("\n")
print("HASIL KEBUTUHAN FASILITAS")
print("-" * 90)

print(
    hasil.to_string(index=False)
)

# ============================================================
# 8. SIMPAN CSV
# ============================================================

output_csv = os.path.join(
    OUTPUT_DIR,
    "kebutuhan_fasilitas_sni.csv"
)

hasil.to_csv(
    output_csv,
    index=False
)

print("\n")
print("=" * 60)
print("SELESAI")
print("=" * 60)

print("Output:")
print(output_csv)