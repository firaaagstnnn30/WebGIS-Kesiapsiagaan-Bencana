import geopandas as gpd
import pandas as pd


# ============================================================
# 1. PATH
# ============================================================

ADMIN_FILE = "data/administrasi.geojson"

JALAN_FILE = "output/jalan_noded.gpkg"
JALAN_LAYER = "jalan_noded"

SKOR_FILE = "output/hasil_skor_aksesibilitas.csv"

OUTPUT_FILE = "output/hasil_road_density.csv"


# ============================================================
# 2. BACA DATA
# ============================================================

print("\n========================================")
print("MEMBACA DATA")
print("========================================")

admin = gpd.read_file(ADMIN_FILE)

jalan = gpd.read_file(
    JALAN_FILE,
    layer=JALAN_LAYER
)

skor = pd.read_csv(SKOR_FILE)

print("Jumlah kecamatan :", len(admin))
print("Jumlah segmen jalan :", len(jalan))


# ============================================================
# 3. UBAH CRS KE UTM 49S
# ============================================================

print("\n========================================")
print("REPROJECT KE EPSG:32749")
print("========================================")

admin = admin.to_crs(epsg=32749)
jalan = jalan.to_crs(epsg=32749)


# ============================================================
# 4. HITUNG LUAS KECAMATAN
# ============================================================

admin["luas_km2"] = (
    admin.geometry.area / 1_000_000
)


# ============================================================
# 5. POTONG JALAN BERDASARKAN BATAS KECAMATAN
# ============================================================

print("\n========================================")
print("MENGHITUNG PANJANG JALAN")
print("========================================")

# Simpan hanya field yang diperlukan
admin_potong = admin[
    ["GID_3", "NAME_3", "luas_km2", "geometry"]
].copy()

jalan_potong = gpd.overlay(
    jalan[["geometry"]],
    admin_potong,
    how="intersection"
)


# ============================================================
# 6. HITUNG PANJANG JALAN
# ============================================================

jalan_potong["panjang_km"] = (
    jalan_potong.geometry.length / 1000
)


# ============================================================
# 7. JUMLAHKAN PANJANG JALAN PER KECAMATAN
# ============================================================

total_jalan = (
    jalan_potong
    .groupby("GID_3")["panjang_km"]
    .sum()
    .reset_index()
)

total_jalan = total_jalan.rename(
    columns={
        "panjang_km": "total_panjang_jalan_km"
    }
)


# ============================================================
# 8. GABUNGKAN DENGAN DATA KECAMATAN
# ============================================================

hasil = admin_potong.merge(
    total_jalan,
    on="GID_3",
    how="left"
)

hasil["total_panjang_jalan_km"] = (
    hasil["total_panjang_jalan_km"]
    .fillna(0)
)


# ============================================================
# 9. HITUNG ROAD DENSITY
# ============================================================

hasil["road_density_km_km2"] = (
    hasil["total_panjang_jalan_km"]
    / hasil["luas_km2"]
)


# ============================================================
# 10. TAMPILKAN HASIL
# ============================================================

print("\n========================================")
print("HASIL ROAD DENSITY")
print("========================================")

print(
    hasil[
        [
            "NAME_3",
            "luas_km2",
            "total_panjang_jalan_km",
            "road_density_km_km2"
        ]
    ]
    .sort_values("road_density_km_km2")
    .to_string(index=False)
)


# ============================================================
# 11. GABUNGKAN DENGAN SKOR FASILITAS
# ============================================================

hasil_final = skor.merge(
    hasil[
        [
            "GID_3",
            "luas_km2",
            "total_panjang_jalan_km",
            "road_density_km_km2"
        ]
    ],
    on="GID_3",
    how="left"
)


# ============================================================
# 12. NORMALISASI ROAD DENSITY
# ============================================================

xmin = hasil_final["road_density_km_km2"].min()
xmax = hasil_final["road_density_km_km2"].max()

print("\n========================================")
print("NORMALISASI ROAD DENSITY")
print("========================================")

print("Minimum road density :", xmin)
print("Maximum road density :", xmax)


if xmax == xmin:

    hasil_final["skor_jalan"] = 2

else:

    hasil_final["skor_jalan"] = (
        1
        + 2
        * (
            (
                hasil_final["road_density_km_km2"]
                - xmin
            )
            /
            (xmax - xmin)
        )
    )


hasil_final["skor_jalan"] = (
    hasil_final["skor_jalan"]
    .round(3)
)


# ============================================================
# 13. SIMPAN
# ============================================================

hasil_final.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 14. TAMPILKAN HASIL AKHIR
# ============================================================

print("\n========================================")
print("HASIL AKHIR ROAD DENSITY")
print("========================================")

print(
    hasil_final[
        [
            "NAME_3",
            "total_panjang_jalan_km",
            "road_density_km_km2",
            "skor_jalan"
        ]
    ]
    .sort_values("road_density_km_km2")
    .to_string(index=False)
)

print("\n========================================")
print("SELESAI")
print("========================================")

print(
    "Hasil disimpan ke:",
    OUTPUT_FILE
)