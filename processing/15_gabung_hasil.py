import geopandas as gpd
import pandas as pd
import os

# ============================================================
# 1. PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADMIN_FILE = os.path.join(BASE_DIR, "..", "data", "administrasi.geojson")
HASIL_AKSES_FILE = os.path.join(BASE_DIR, "..", "output", "indeks_aksesibilitas_klasifikasi.csv")
EVALUASI_FILE = os.path.join(BASE_DIR, "..", "output", "evaluasi_pemenuhan_fasilitas.csv")
FINAL_FILE = os.path.join(BASE_DIR, "..", "output", "indeks_final_evaluasi.csv")

OUTPUT_FILE = os.path.join(BASE_DIR, "..", "output", "kecamatan_aksesibilitas.geojson")


# ============================================================
# 2. BACA DATA
# ============================================================

print("\n========================================")
print("MEMBACA DATA SPASIAL DAN TABULAR HASIL ANALISIS")
print("========================================")

admin = gpd.read_file(ADMIN_FILE)

# Baca hasil analisis aksesibilitas dasar (jarak & kerapatan jalan)
hasil_df = pd.read_csv(HASIL_AKSES_FILE)

# Gabungkan dengan hasil evaluasi pemenuhan fasilitas SNI jika tersedia
final_path = FINAL_FILE if os.path.exists(FINAL_FILE) else os.path.join(BASE_DIR, "output", "indeks_final_evaluasi.csv")
eval_path = EVALUASI_FILE if os.path.exists(EVALUASI_FILE) else os.path.join(BASE_DIR, "output", "evaluasi_pemenuhan_fasilitas.csv")

if os.path.exists(final_path):
    final_df = pd.read_csv(final_path)
    cols_to_merge = [c for c in final_df.columns if c not in hasil_df.columns or c == "GID_3"]
    hasil_df = hasil_df.merge(final_df[cols_to_merge], on="GID_3", how="left")
    print("Membaca dan menggabungkan data dari indeks_final_evaluasi.csv")
elif os.path.exists(eval_path):
    eval_df = pd.read_csv(eval_path)
    cols_to_merge = [c for c in eval_df.columns if c not in hasil_df.columns or c == "GID_3"]
    hasil_df = hasil_df.merge(eval_df[cols_to_merge], on="GID_3", how="left")
    print("Membaca dan menggabungkan data dari evaluasi_pemenuhan_fasilitas.csv")

# Gabungkan dengan hasil analisis isochrone jika tersedia
iso_path = os.path.join(BASE_DIR, "..", "output", "cakupan_isochrone_worldpop.csv")
if os.path.exists(iso_path):
    iso_df = pd.read_csv(iso_path)
    cols_to_merge = [c for c in iso_df.columns if c not in hasil_df.columns or c == "GID_3"]
    hasil_df = hasil_df.merge(iso_df[cols_to_merge], on="GID_3", how="left")
    print("Membaca dan menggabungkan data dari cakupan_isochrone_worldpop.csv")

# Pastikan kolom kelas_aksesibilitas dan kelas_final tersedia
if "kelas_final" in hasil_df.columns and "kelas_aksesibilitas" not in hasil_df.columns:
    hasil_df["kelas_aksesibilitas"] = hasil_df["kelas_final"]
elif "kelas_aksesibilitas" in hasil_df.columns and "kelas_final" not in hasil_df.columns:
    hasil_df["kelas_final"] = hasil_df["kelas_aksesibilitas"]

print("Jumlah polygon kecamatan :", len(admin))
print("Jumlah data hasil        :", len(hasil_df))


# ============================================================
# 3. JOIN BERDASARKAN GID_3
# ============================================================

admin_hasil = admin.merge(
    hasil_df,
    on="GID_3",
    how="left"
)

# Tangani duplikasi nama jika ada
for col in ["NAME_3_y", "NAME_3_x"]:
    if col in admin_hasil.columns:
        if col == "NAME_3_x":
            admin_hasil["NAME_3"] = admin_hasil["NAME_3_x"]
        admin_hasil = admin_hasil.drop(columns=[col])


# ============================================================
# 4. SIMPAN GEOJSON
# ============================================================

admin_hasil.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("\n========================================")
print("GEOJSON BERHASIL DIPERBARUI")
print("========================================")
print("Output file:", OUTPUT_FILE)
print("Jumlah atribut:", len(admin_hasil.columns))