import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point

# =========================================================
# 1. PENGATURAN
# =========================================================

CRS_ANALISIS = "EPSG:32749"

# File input
FILE_JALAN = "output/jalan_noded.gpkg"
LAYER_JALAN = "jalan_noded"

FILE_ADMIN = "data/administrasi.geojson"
FILE_DAMKAR = "data/damkar.geojson"
FILE_RS = "data/rumah_sakit.geojson"
FILE_PUSKESMAS = "data/puskesmas.geojson"
FILE_POLISI = "data/kantor_polisi.geojson"

# =========================================================
# 2. BACA DATA
# =========================================================

print("Membaca data...")

jalan = gpd.read_file(FILE_JALAN, layer=LAYER_JALAN)
admin = gpd.read_file(FILE_ADMIN)
damkar = gpd.read_file(FILE_DAMKAR)
rs = gpd.read_file(FILE_RS)
puskesmas = gpd.read_file(FILE_PUSKESMAS)
polisi = gpd.read_file(FILE_POLISI)

# Ubah ke CRS analisis
jalan = jalan.to_crs(CRS_ANALISIS)
admin = admin.to_crs(CRS_ANALISIS)
damkar = damkar.to_crs(CRS_ANALISIS)
rs = rs.to_crs(CRS_ANALISIS)
puskesmas = puskesmas.to_crs(CRS_ANALISIS)
polisi = polisi.to_crs(CRS_ANALISIS)

print("Semua data menggunakan:", CRS_ANALISIS)

# =========================================================
# 3. MEMBUAT TITIK REPRESENTATIF KECAMATAN
# =========================================================

admin["titik_representatif"] = admin.geometry.representative_point()

titik_kecamatan = gpd.GeoDataFrame(
    admin[["GID_3", "NAME_3"]].copy(),
    geometry=admin["titik_representatif"],
    crs=CRS_ANALISIS
)

print("\nJumlah titik kecamatan:", len(titik_kecamatan))

# =========================================================
# 4. MEMBUAT TITIK FASILITAS
# =========================================================

damkar_titik = damkar.copy()
rs_titik = rs.copy()
puskesmas_titik = puskesmas.copy()
polisi_titik = polisi.copy()

# Pastikan geometry berupa titik
damkar_titik["geometry"] = damkar_titik.geometry.centroid
rs_titik["geometry"] = rs_titik.geometry.centroid
puskesmas_titik["geometry"] = puskesmas_titik.geometry.centroid
polisi_titik["geometry"] = polisi_titik.geometry.centroid

# =========================================================
# 5. FUNGSI CEK JARAK KE JALAN TERDEKAT
# =========================================================

def cek_ke_jalan(data, nama_data):

    print(f"\n===== {nama_data.upper()} =====")

    hasil = gpd.sjoin_nearest(
        data,
        jalan[["geometry"]],
        how="left",
        distance_col="jarak_ke_jalan_m"
    )

    print("Jumlah data:", len(hasil))

    print(
        "Jarak minimum :",
        round(hasil["jarak_ke_jalan_m"].min(), 2),
        "meter"
    )

    print(
        "Jarak maksimum:",
        round(hasil["jarak_ke_jalan_m"].max(), 2),
        "meter"
    )

    print(
        "Jarak rata-rata:",
        round(hasil["jarak_ke_jalan_m"].mean(), 2),
        "meter"
    )

    print(
        "Jarak median  :",
        round(hasil["jarak_ke_jalan_m"].median(), 2),
        "meter"
    )

    return hasil


# =========================================================
# 6. CEK SEMUA TITIK TERHADAP JARINGAN JALAN
# =========================================================

hasil_kecamatan = cek_ke_jalan(
    titik_kecamatan,
    "Kecamatan"
)

hasil_damkar = cek_ke_jalan(
    damkar_titik,
    "Damkar"
)

hasil_rs = cek_ke_jalan(
    rs_titik,
    "Rumah Sakit"
)

hasil_puskesmas = cek_ke_jalan(
    puskesmas_titik,
    "Puskesmas"
)

hasil_polisi = cek_ke_jalan(
    polisi_titik,
    "Kantor Polisi"
)

# =========================================================
# 7. SIMPAN HASIL
# =========================================================

hasil_kecamatan.to_file(
    "output/snap_kecamatan.gpkg",
    layer="snap_kecamatan",
    driver="GPKG"
)

hasil_damkar.to_file(
    "output/snap_damkar.gpkg",
    layer="snap_damkar",
    driver="GPKG"
)

hasil_rs.to_file(
    "output/snap_rs.gpkg",
    layer="snap_rs",
    driver="GPKG"
)

hasil_puskesmas.to_file(
    "output/snap_puskesmas.gpkg",
    layer="snap_puskesmas",
    driver="GPKG"
)

hasil_polisi.to_file(
    "output/snap_polisi.gpkg",
    layer="snap_polisi",
    driver="GPKG"
)

print("\n========================================")
print("SELESAI")
print("========================================")
print("Hasil pengecekan titik terhadap jaringan jalan")
print("sudah disimpan di folder output.")