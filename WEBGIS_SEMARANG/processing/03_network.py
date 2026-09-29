import geopandas as gpd
from shapely.geometry import LineString

# ==========================================
# 1. BACA DATA JALAN
# ==========================================

jalan = gpd.read_file("data/jalan.geojson")

# ==========================================
# 2. UBAH CRS KE UTM 49S
# ==========================================

jalan = jalan.to_crs("EPSG:32749")


# ==========================================
# 3. PECAH MULTILINESTRING
#    MENJADI LINESTRING
# ==========================================

jalan_potong = jalan.explode(
    index_parts=False
).reset_index(drop=True)


# ==========================================
# 4. CEK HASIL
# ==========================================

print("\n===== HASIL PECAH MULTILINESTRING =====")

print("Jumlah fitur awal  :", len(jalan))
print("Jumlah fitur akhir :", len(jalan_potong))

print("\n===== TIPE GEOMETRI =====")

print(
    jalan_potong.geometry.geom_type.value_counts()
)


# ==========================================
# 5. CEK PANJANG
# ==========================================

jalan_potong["panjang_m"] = (
    jalan_potong.geometry.length
)

jalan_potong["panjang_km"] = (
    jalan_potong.geometry.length / 1000
)


print("\n===== PANJANG JALAN =====")

print(
    "Total panjang:",
    jalan_potong["panjang_km"].sum(),
    "km"
)


# ==========================================
# 6. CEK CONTOH KOORDINAT
# ==========================================

print("\n===== CONTOH GEOMETRI =====")

for i in range(min(5, len(jalan_potong))):

    geom = jalan_potong.geometry.iloc[i]

    print(
        f"\nRuas {i+1}"
    )

    print(
        "Tipe:",
        geom.geom_type
    )

    print(
        "Jumlah titik:",
        len(geom.coords)
    )

    print(
        "Titik awal:",
        geom.coords[0]
    )

    print(
        "Titik akhir:",
        geom.coords[-1]
    )