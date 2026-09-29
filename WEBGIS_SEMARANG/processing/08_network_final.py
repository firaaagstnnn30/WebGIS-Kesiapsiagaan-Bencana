import geopandas as gpd
import pandas as pd
import networkx as nx

from shapely.geometry import Point, LineString
from shapely.ops import split


# ============================================================
# 1. PENGATURAN
# ============================================================

CRS_ANALISIS = "EPSG:32749"

FILE_JALAN = "output/jalan_noded.gpkg"
LAYER_JALAN = "jalan_noded"

FILE_ADMIN = "data/administrasi.geojson"
FILE_DAMKAR = "data/damkar.geojson"
FILE_RS = "data/rumah_sakit.geojson"
FILE_PUSKESMAS = "data/puskesmas.geojson"
FILE_POLISI = "data/kantor_polisi.geojson"


# ============================================================
# 2. BACA DATA
# ============================================================

print("========================================")
print("MEMBACA DATA")
print("========================================")

jalan = gpd.read_file(
    FILE_JALAN,
    layer=LAYER_JALAN
).to_crs(CRS_ANALISIS)

admin = gpd.read_file(
    FILE_ADMIN
).to_crs(CRS_ANALISIS)

damkar = gpd.read_file(
    FILE_DAMKAR
).to_crs(CRS_ANALISIS)

rs = gpd.read_file(
    FILE_RS
).to_crs(CRS_ANALISIS)

puskesmas = gpd.read_file(
    FILE_PUSKESMAS
).to_crs(CRS_ANALISIS)

polisi = gpd.read_file(
    FILE_POLISI
).to_crs(CRS_ANALISIS)

print("Jumlah ruas jalan :", len(jalan))
print("Jumlah kecamatan  :", len(admin))
print("Jumlah damkar     :", len(damkar))
print("Jumlah RS         :", len(rs))
print("Jumlah puskesmas  :", len(puskesmas))
print("Jumlah polisi     :", len(polisi))


# ============================================================
# 3. BERSIHKAN GEOMETRI JALAN
# ============================================================

def ubah_ke_2d(geom):

    if geom is None:
        return None

    if geom.is_empty:
        return None

    if geom.geom_type == "LineString":

        return LineString([
            (coord[0], coord[1])
            for coord in geom.coords
        ])

    return geom


jalan["geometry"] = jalan.geometry.apply(ubah_ke_2d)

jalan = jalan[
    jalan.geometry.notna()
].copy()

jalan = jalan[
    ~jalan.geometry.is_empty
].copy()

jalan = jalan[
    jalan.geometry.geom_type == "LineString"
].copy()

jalan = jalan.reset_index(drop=True)


# ============================================================
# 4. BUAT TITIK KECAMATAN
# ============================================================

admin["geometry"] = admin.geometry.representative_point()

kecamatan = gpd.GeoDataFrame(
    admin[["GID_3", "NAME_3"]].copy(),
    geometry=admin.geometry,
    crs=CRS_ANALISIS
)


# ============================================================
# 5. BUAT TITIK FASILITAS
# ============================================================

def buat_titik(data):

    data = data.copy()

    data["geometry"] = data.geometry.centroid

    return data


damkar = buat_titik(damkar)
rs = buat_titik(rs)
puskesmas = buat_titik(puskesmas)
polisi = buat_titik(polisi)


# ============================================================
# 6. GABUNG SEMUA TITIK
# ============================================================

print("\n========================================")
print("MENYIAPKAN TITIK ANALISIS")
print("========================================")

semua_titik = []

# Kecamatan
for idx, row in kecamatan.iterrows():

    semua_titik.append({
        "jenis": "kecamatan",
        "id": str(row["GID_3"]),
        "nama": row["NAME_3"],
        "geometry": row.geometry
    })


# Damkar
for idx, row in damkar.iterrows():

    nama = row["name"] if "name" in damkar.columns else f"Damkar_{idx}"

    semua_titik.append({
        "jenis": "damkar",
        "id": str(idx),
        "nama": nama,
        "geometry": row.geometry
    })


# Rumah sakit
for idx, row in rs.iterrows():

    nama = row["name"] if "name" in rs.columns else f"RS_{idx}"

    semua_titik.append({
        "jenis": "rumah_sakit",
        "id": str(idx),
        "nama": nama,
        "geometry": row.geometry
    })


# Puskesmas
for idx, row in puskesmas.iterrows():

    nama = row["name"] if "name" in puskesmas.columns else f"Puskesmas_{idx}"

    semua_titik.append({
        "jenis": "puskesmas",
        "id": str(idx),
        "nama": nama,
        "geometry": row.geometry
    })


# Polisi
for idx, row in polisi.iterrows():

    nama = row["name"] if "name" in polisi.columns else f"Polisi_{idx}"

    semua_titik.append({
        "jenis": "polisi",
        "id": str(idx),
        "nama": nama,
        "geometry": row.geometry
    })


titik = gpd.GeoDataFrame(
    semua_titik,
    geometry="geometry",
    crs=CRS_ANALISIS
)

print("Total titik analisis:", len(titik))


# ============================================================
# 7. CARI RUAS JALAN TERDEKAT
# ============================================================

print("\n========================================")
print("MENCARI RUAS JALAN TERDEKAT")
print("========================================")

nearest = gpd.sjoin_nearest(
    titik,
    jalan[["geometry"]],
    how="left",
    distance_col="jarak_ke_jalan_m"
)

nearest = nearest.rename(
    columns={
        "index_right": "index_ruas"
    }
)

print(
    "Jarak minimum :",
    round(nearest["jarak_ke_jalan_m"].min(), 2),
    "m"
)

print(
    "Jarak median  :",
    round(nearest["jarak_ke_jalan_m"].median(), 2),
    "m"
)

print(
    "Jarak maksimum:",
    round(nearest["jarak_ke_jalan_m"].max(), 2),
    "m"
)


# ============================================================
# 8. PROYEKSI TITIK KE RUAS JALAN
# ============================================================

print("\n========================================")
print("MEMPROYEKSI TITIK KE RUAS JALAN")
print("========================================")

hasil_snap = []

for idx, row in nearest.iterrows():

    titik_asli = row.geometry

    index_ruas = row["index_ruas"]

    ruas = jalan.loc[
        index_ruas,
        "geometry"
    ]

    # Posisi sepanjang ruas
    posisi = ruas.project(
        titik_asli
    )

    # Titik hasil proyeksi
    titik_snap = ruas.interpolate(
        posisi
    )

    hasil_snap.append({

        "jenis": row["jenis"],

        "id": row["id"],

        "nama": row["nama"],

        "index_ruas": index_ruas,

        "jarak_snap_m":
            titik_asli.distance(
                titik_snap
            ),

        "geometry":
            titik_snap
    })


snap = gpd.GeoDataFrame(
    hasil_snap,
    geometry="geometry",
    crs=CRS_ANALISIS
)

print("Jumlah titik snap:", len(snap))


# ============================================================
# 9. MEMBUAT NODE BARU
# ============================================================

print("\n========================================")
print("MEMBUAT NODE BARU PADA RUAS")
print("========================================")


# ------------------------------------------------------------
# ID node dibuat berdasarkan koordinat
# ------------------------------------------------------------

def node_id(point):

    return (
        round(point.x, 3),
        round(point.y, 3)
    )


# ============================================================
# 10. KUMPULKAN TITIK SNAP PADA SETIAP RUAS
# ============================================================

titik_per_ruas = {}

for idx, row in snap.iterrows():

    ruas_id = row["index_ruas"]

    if ruas_id not in titik_per_ruas:

        titik_per_ruas[ruas_id] = []

    titik_per_ruas[ruas_id].append(
        row.geometry
    )


# ============================================================
# 11. SPLIT RUAS JALAN
# ============================================================

print("Melakukan split ruas jalan...")
print("Proses dapat membutuhkan waktu...")


ruas_baru = []


for idx, row in jalan.iterrows():

    geom = row.geometry

    # Jika ruas memiliki titik snap
    if idx in titik_per_ruas:

        titik_split = titik_per_ruas[idx]

        # Hilangkan titik yang terlalu dekat dengan ujung
        titik_valid = []

        for p in titik_split:

            if (
                p.distance(
                    Point(geom.coords[0])
                ) > 0.001
                and
                p.distance(
                    Point(geom.coords[-1])
                ) > 0.001
            ):

                titik_valid.append(p)

        # Jika tidak ada titik valid
        if len(titik_valid) == 0:

            ruas_baru.append(geom)

            continue

        # Split satu per satu
        bagian = [geom]

        for p in titik_valid:

            bagian_baru = []

            for garis in bagian:

                try:

                    hasil_split = split(
                        garis,
                        p
                    )

                    bagian_baru.extend(
                        list(
                            hasil_split.geoms
                        )
                    )

                except:

                    bagian_baru.append(
                        garis
                    )

            bagian = bagian_baru

        ruas_baru.extend(
            bagian
        )

    else:

        ruas_baru.append(
            geom
        )


# ============================================================
# 12. HASIL RUAS SETELAH SPLIT
# ============================================================

jalan_final = gpd.GeoDataFrame(
    geometry=ruas_baru,
    crs=CRS_ANALISIS
)

jalan_final = jalan_final[
    ~jalan_final.geometry.is_empty
].copy()

jalan_final = jalan_final[
    jalan_final.geometry.length > 0.001
].copy()

jalan_final.reset_index(
    drop=True,
    inplace=True
)

jalan_final["panjang_m"] = (
    jalan_final.geometry.length
)


print("\n===== HASIL SPLIT =====")

print(
    "Ruas sebelum split :",
    len(jalan)
)

print(
    "Ruas setelah split :",
    len(jalan_final)
)

print(
    "Total panjang jalan:",
    round(
        jalan_final["panjang_m"].sum() / 1000,
        3
    ),
    "km"
)


# ============================================================
# 13. BUAT GRAPH FINAL
# ============================================================

print("\n========================================")
print("MEMBUAT GRAPH FINAL")
print("========================================")

G = nx.Graph()


for idx, row in jalan_final.iterrows():

    geom = row.geometry

    coords = list(
        geom.coords
    )

    if len(coords) < 2:
        continue

    node_awal = node_id(
        Point(coords[0])
    )

    node_akhir = node_id(
        Point(coords[-1])
    )

    panjang = geom.length

    G.add_edge(
        node_awal,
        node_akhir,
        weight=panjang
    )


print(
    "Jumlah node:",
    G.number_of_nodes()
)

print(
    "Jumlah edge:",
    G.number_of_edges()
)


# ============================================================
# 14. CEK KONEKTIVITAS
# ============================================================

komponen = list(
    nx.connected_components(G)
)

komponen_terbesar = max(
    komponen,
    key=len
)

print(
    "Jumlah komponen:",
    len(komponen)
)

print(
    "Node komponen terbesar:",
    len(komponen_terbesar)
)


# ============================================================
# 15. CARI NODE HASIL SNAP
# ============================================================

print("\n========================================")
print("MENGHUBUNGKAN TITIK ANALISIS")
print("========================================")


def cari_node_snap(point):

    target = node_id(point)

    # Kalau node persis ada
    if target in G.nodes:

        return target

    # Kalau pembulatan membuat sedikit beda,
    # cari node terdekat
    node_terdekat = None
    jarak_terdekat = float("inf")

    for node in G.nodes:

        dx = node[0] - point.x
        dy = node[1] - point.y

        jarak = math.sqrt(
            dx * dx + dy * dy
        )

        if jarak < jarak_terdekat:

            jarak_terdekat = jarak
            node_terdekat = node

    return node_terdekat


# ============================================================
# 16. IMPORT MATH
# ============================================================

import math


# ============================================================
# 17. HUBUNGKAN SETIAP TITIK KE GRAPH
# ============================================================

snap["node_x"] = None
snap["node_y"] = None

for idx, row in snap.iterrows():

    node = cari_node_snap(
        row.geometry
    )

    snap.loc[
        idx,
        "node_x"
    ] = node[0]

    snap.loc[
        idx,
        "node_y"
    ] = node[1]


# ============================================================
# 18. HITUNG SHORTEST PATH
# ============================================================

print("\n========================================")
print("MENGHITUNG SHORTEST PATH")
print("========================================")


def shortest_path(
    node_asal,
    node_tujuan
):

    try:

        return nx.shortest_path_length(
            G,
            source=node_asal,
            target=node_tujuan,
            weight="weight"
        )

    except nx.NetworkXNoPath:

        return None


# ------------------------------------------------------------
# Pisahkan titik berdasarkan jenis
# ------------------------------------------------------------

data_kecamatan = snap[
    snap["jenis"] == "kecamatan"
].copy()

data_damkar = snap[
    snap["jenis"] == "damkar"
].copy()

data_rs = snap[
    snap["jenis"] == "rumah_sakit"
].copy()

data_puskesmas = snap[
    snap["jenis"] == "puskesmas"
].copy()

data_polisi = snap[
    snap["jenis"] == "polisi"
].copy()


# ============================================================
# 19. HITUNG JARAK SETIAP KECAMATAN
# ============================================================

hasil = []


for idx, kec in data_kecamatan.iterrows():

    node_asal = (
        kec["node_x"],
        kec["node_y"]
    )

    # ----------------------------------------
    # DAMKAR
    # ----------------------------------------

    jarak_damkar = []

    for _, f in data_damkar.iterrows():

        node_tujuan = (
            f["node_x"],
            f["node_y"]
        )

        d = shortest_path(
            node_asal,
            node_tujuan
        )

        if d is not None:

            jarak_damkar.append(d)


    # ----------------------------------------
    # RUMAH SAKIT
    # ----------------------------------------

    jarak_rs = []

    for _, f in data_rs.iterrows():

        node_tujuan = (
            f["node_x"],
            f["node_y"]
        )

        d = shortest_path(
            node_asal,
            node_tujuan
        )

        if d is not None:

            jarak_rs.append(d)


    # ----------------------------------------
    # PUSKESMAS
    # ----------------------------------------

    jarak_puskesmas = []

    for _, f in data_puskesmas.iterrows():

        node_tujuan = (
            f["node_x"],
            f["node_y"]
        )

        d = shortest_path(
            node_asal,
            node_tujuan
        )

        if d is not None:

            jarak_puskesmas.append(d)


    # ----------------------------------------
    # POLISI
    # ----------------------------------------

    jarak_polisi = []

    for _, f in data_polisi.iterrows():

        node_tujuan = (
            f["node_x"],
            f["node_y"]
        )

        d = shortest_path(
            node_asal,
            node_tujuan
        )

        if d is not None:

            jarak_polisi.append(d)


    # ----------------------------------------
    # SIMPAN
    # ----------------------------------------

    hasil.append({

        "GID_3":
            kec["id"],

        "NAME_3":
            kec["nama"],

        "jarak_damkar_km":
            min(jarak_damkar) / 1000
            if jarak_damkar
            else None,

        "jarak_rs_km":
            min(jarak_rs) / 1000
            if jarak_rs
            else None,

        "jarak_puskesmas_km":
            min(jarak_puskesmas) / 1000
            if jarak_puskesmas
            else None,

        "jarak_polisi_km":
            min(jarak_polisi) / 1000
            if jarak_polisi
            else None
    })


hasil = pd.DataFrame(hasil)


# ============================================================
# 20. TAMPILKAN HASIL
# ============================================================

print("\n========================================")
print("HASIL SHORTEST PATH FINAL")
print("========================================")

print(
    hasil.to_string(
        index=False
    )
)


# ============================================================
# 21. SIMPAN HASIL
# ============================================================

hasil.to_csv(
    "output/hasil_shortest_path_final.csv",
    index=False
)

snap.to_file(
    "output/titik_snap_final.gpkg",
    layer="titik_snap",
    driver="GPKG"
)

jalan_final.to_file(
    "output/jalan_network_final.gpkg",
    layer="jalan_network_final",
    driver="GPKG"
)


print("\n========================================")
print("SELESAI")
print("========================================")

print(
    "Hasil jarak:"
)

print(
    "output/hasil_shortest_path_final.csv"
)

print(
    "Network:"
)

print(
    "output/jalan_network_final.gpkg"
)