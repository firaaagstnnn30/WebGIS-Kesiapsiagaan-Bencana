import geopandas as gpd

# =====================================================
# 1. MEMBACA DATA
# =====================================================

admin = gpd.read_file("data/administrasi.geojson")
damkar = gpd.read_file("data/damkar.geojson")
jalan = gpd.read_file("data/jalan.geojson")
polisi = gpd.read_file("data/kantor_polisi.geojson")
puskesmas = gpd.read_file("data/puskesmas.geojson")
rumah_sakit = gpd.read_file("data/rumah_sakit.geojson")


# =====================================================
# 2. MENGUBAH CRS UNTUK ANALISIS
#    EPSG:32749 = UTM Zone 49S
# =====================================================

CRS_ANALISIS = "EPSG:32749"

admin = admin.to_crs(CRS_ANALISIS)
damkar = damkar.to_crs(CRS_ANALISIS)
jalan = jalan.to_crs(CRS_ANALISIS)
polisi = polisi.to_crs(CRS_ANALISIS)
puskesmas = puskesmas.to_crs(CRS_ANALISIS)
rumah_sakit = rumah_sakit.to_crs(CRS_ANALISIS)


print("\n===== CRS SETELAH REPROJECTION =====")

print("Administrasi :", admin.crs)
print("Damkar       :", damkar.crs)
print("Jalan        :", jalan.crs)
print("Polisi       :", polisi.crs)
print("Puskesmas    :", puskesmas.crs)
print("Rumah Sakit  :", rumah_sakit.crs)


# =====================================================
# 3. MENGHITUNG LUAS SETIAP KECAMATAN
# =====================================================

admin["luas_km2"] = admin.geometry.area / 1_000_000


# =====================================================
# 4. MEMBUAT TITIK REPRESENTATIF KECAMATAN
# =====================================================

admin["titik_representatif"] = admin.geometry.representative_point()

titik_kecamatan = admin[
    [
        "GID_3",
        "NAME_3",
        "luas_km2",
        "titik_representatif"
    ]
].copy()

titik_kecamatan = titik_kecamatan.set_geometry(
    "titik_representatif"
)


# =====================================================
# 5. MENCARI DAMKAR TERDEKAT
# =====================================================

hasil_damkar = gpd.sjoin_nearest(
    titik_kecamatan,
    damkar[["name", "geometry"]],
    how="left",
    distance_col="jarak_damkar_m"
)

hasil_damkar = hasil_damkar[
    [
        "GID_3",
        "NAME_3",
        "luas_km2",
        "jarak_damkar_m"
    ]
].copy()


# =====================================================
# 6. MENCARI RUMAH SAKIT TERDEKAT
# =====================================================

hasil_rs = gpd.sjoin_nearest(
    titik_kecamatan,
    rumah_sakit[["name", "geometry"]],
    how="left",
    distance_col="jarak_rs_m"
)

hasil_rs = hasil_rs[
    [
        "GID_3",
        "jarak_rs_m"
    ]
].copy()


# =====================================================
# 7. MENCARI PUSKESMAS TERDEKAT
# =====================================================

hasil_puskesmas = gpd.sjoin_nearest(
    titik_kecamatan,
    puskesmas[["name", "geometry"]],
    how="left",
    distance_col="jarak_puskesmas_m"
)

hasil_puskesmas = hasil_puskesmas[
    [
        "GID_3",
        "jarak_puskesmas_m"
    ]
].copy()


# =====================================================
# 8. MENCARI KANTOR POLISI TERDEKAT
# =====================================================

hasil_polisi = gpd.sjoin_nearest(
    titik_kecamatan,
    polisi[["name", "geometry"]],
    how="left",
    distance_col="jarak_polisi_m"
)

hasil_polisi = hasil_polisi[
    [
        "GID_3",
        "jarak_polisi_m"
    ]
].copy()


# =====================================================
# 9. MENGGABUNGKAN SEMUA HASIL
# =====================================================

hasil = hasil_damkar.merge(
    hasil_rs,
    on="GID_3",
    how="left"
)

hasil = hasil.merge(
    hasil_puskesmas,
    on="GID_3",
    how="left"
)

hasil = hasil.merge(
    hasil_polisi,
    on="GID_3",
    how="left"
)


# =====================================================
# 10. MENGUBAH METER → KILOMETER
# =====================================================

hasil["jarak_damkar_km"] = (
    hasil["jarak_damkar_m"] / 1000
)

hasil["jarak_rs_km"] = (
    hasil["jarak_rs_m"] / 1000
)

hasil["jarak_puskesmas_km"] = (
    hasil["jarak_puskesmas_m"] / 1000
)

hasil["jarak_polisi_km"] = (
    hasil["jarak_polisi_m"] / 1000
)


# =====================================================
# 11. MENAMPILKAN HASIL
# =====================================================

print("\n===== HASIL JARAK FASILITAS =====")

print(
    hasil[
        [
            "NAME_3",
            "jarak_damkar_km",
            "jarak_rs_km",
            "jarak_puskesmas_km",
            "jarak_polisi_km"
        ]
    ].to_string(index=False)
)