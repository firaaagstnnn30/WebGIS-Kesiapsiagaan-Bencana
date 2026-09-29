import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point
from shapely.ops import nearest_points
import math

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

admin = gpd.read_file(FILE_ADMIN).to_crs(CRS_ANALISIS)
damkar = gpd.read_file(FILE_DAMKAR).to_crs(CRS_ANALISIS)
rs = gpd.read_file(FILE_RS).to_crs(CRS_ANALISIS)
puskesmas = gpd.read_file(FILE_PUSKESMAS).to_crs(CRS_ANALISIS)
polisi = gpd.read_file(FILE_POLISI).to_crs(CRS_ANALISIS)

print("Jumlah ruas jalan :", len(jalan))
print("Jumlah kecamatan  :", len(admin))
print("Jumlah damkar     :", len(damkar))
print("Jumlah RS         :", len(rs))
print("Jumlah puskesmas  :", len(puskesmas))
print("Jumlah polisi     :", len(polisi))


# ============================================================
# 3. PASTIKAN JALAN BERUPA LINESTRING 2D
# ============================================================

from shapely.geometry import LineString

def ubah_ke_2d(geom):

    if geom is None:
        return None

    if geom.geom_type == "LineString":

        return LineString([
            (coord[0], coord[1])
            for coord in geom.coords
        ])

    return geom


jalan["geometry"] = jalan.geometry.apply(ubah_ke_2d)


# ============================================================
# 4. MEMBUAT GRAPH JALAN
# ============================================================

print("\n========================================")
print("MEMBUAT GRAPH JARINGAN JALAN")
print("========================================")

G = nx.Graph()

for idx, row in jalan.iterrows():

    geom = row.geometry

    if geom is None or geom.is_empty:
        continue

    if geom.geom_type != "LineString":
        continue

    coords = list(geom.coords)

    if len(coords) < 2:
        continue

    awal = (
        round(coords[0][0], 3),
        round(coords[0][1], 3)
    )

    akhir = (
        round(coords[-1][0], 3),
        round(coords[-1][1], 3)
    )

    panjang = geom.length

    G.add_edge(
        awal,
        akhir,
        weight=panjang
    )

print("Jumlah node :", G.number_of_nodes())
print("Jumlah edge :", G.number_of_edges())


# ============================================================
# 5. MEMBUAT REPRESENTATIVE POINT KECAMATAN
# ============================================================

admin["geometry"] = admin.geometry.representative_point()

titik_kecamatan = gpd.GeoDataFrame(
    admin[["GID_3", "NAME_3"]].copy(),
    geometry=admin.geometry,
    crs=CRS_ANALISIS
)


# ============================================================
# 6. UBAH FASILITAS MENJADI TITIK
# ============================================================

def fasilitas_ke_titik(data):

    data = data.copy()

    data["geometry"] = data.geometry.centroid

    return data


damkar_titik = fasilitas_ke_titik(damkar)
rs_titik = fasilitas_ke_titik(rs)
puskesmas_titik = fasilitas_ke_titik(puskesmas)
polisi_titik = fasilitas_ke_titik(polisi)


# ============================================================
# 7. CARI RUAS JALAN TERDEKAT
# ============================================================

print("\n========================================")
print("MENCARI RUAS JALAN TERDEKAT")
print("========================================")


def cari_ruas_terdekat(data, nama):

    hasil = gpd.sjoin_nearest(
        data,
        jalan[["geometry"]],
        how="left",
        distance_col="jarak_ke_ruas_m"
    )

    print(f"\n{nama}")

    print(
        "Minimum :",
        round(
            hasil["jarak_ke_ruas_m"].min(),
            2
        ),
        "meter"
    )

    print(
        "Median  :",
        round(
            hasil["jarak_ke_ruas_m"].median(),
            2
        ),
        "meter"
    )

    print(
        "Maksimum:",
        round(
            hasil["jarak_ke_ruas_m"].max(),
            2
        ),
        "meter"
    )

    return hasil


snap_kecamatan = cari_ruas_terdekat(
    titik_kecamatan,
    "KECAMATAN"
)

snap_damkar = cari_ruas_terdekat(
    damkar_titik,
    "DAMKAR"
)

snap_rs = cari_ruas_terdekat(
    rs_titik,
    "RUMAH SAKIT"
)

snap_puskesmas = cari_ruas_terdekat(
    puskesmas_titik,
    "PUSKESMAS"
)

snap_polisi = cari_ruas_terdekat(
    polisi_titik,
    "KANTOR POLISI"
)


# ============================================================
# 8. FUNGSI MENCARI TITIK PROYEKSI KE RUAS JALAN
# ============================================================

def titik_snap_ke_ruas(point, ruas):

    titik = ruas.geometry.iloc[0]

    titik_proyeksi = titik.interpolate(
        titik.project(point)
    )

    return titik_proyeksi


# ============================================================
# 9. MEMBUAT TITIK SNAP
# ============================================================

def buat_titik_snap(data):

    hasil = []

    for idx, row in data.iterrows():

        point = row.geometry

        # Cari ruas jalan terdekat
        jarak = jalan.geometry.distance(
            point
        )

        indeks_terdekat = jarak.idxmin()

        ruas = jalan.loc[
            indeks_terdekat,
            "geometry"
        ]

        # Proyeksikan titik ke ruas
        titik_snap = ruas.interpolate(
            ruas.project(point)
        )

        hasil.append({

            "original_index": idx,

            "x": titik_snap.x,

            "y": titik_snap.y,

            "jarak_snap_m":
                point.distance(titik_snap)

        })

    return pd.DataFrame(hasil)


print("\n========================================")
print("MEMBUAT TITIK SNAP KE RUAS")
print("========================================")

snap_node_kecamatan = buat_titik_snap(
    titik_kecamatan
)

snap_node_damkar = buat_titik_snap(
    damkar_titik
)

snap_node_rs = buat_titik_snap(
    rs_titik
)

snap_node_puskesmas = buat_titik_snap(
    puskesmas_titik
)

snap_node_polisi = buat_titik_snap(
    polisi_titik
)


# ============================================================
# 10. MEMBUAT GRAPH YANG MEMUNGKINKAN
#     TITIK SNAP MASUK KE JARINGAN
# ============================================================

print("\n========================================")
print("MEMBUAT GRAPH SNAP")
print("========================================")


# ------------------------------------------------------------
# Fungsi mencari node terdekat
# ------------------------------------------------------------

def node_terdekat(point, graph):

    node_terdekat = None
    jarak_terdekat = float("inf")

    for node in graph.nodes:

        dx = node[0] - point.x
        dy = node[1] - point.y

        jarak = math.sqrt(
            dx * dx + dy * dy
        )

        if jarak < jarak_terdekat:

            jarak_terdekat = jarak

            node_terdekat = node

    return node_terdekat


# ------------------------------------------------------------
# Untuk saat ini titik snap akan dikaitkan dengan
# node jaringan terdekat setelah proyeksi ke ruas.
# ------------------------------------------------------------

def snap_ke_graph(data, graph):

    hasil = []

    for idx, row in data.iterrows():

        point = Point(
            row["x"],
            row["y"]
        )

        node = node_terdekat(
            point,
            graph
        )

        hasil.append({

            "original_index":
                row["original_index"],

            "node_x":
                node[0],

            "node_y":
                node[1],

            "jarak_node_dari_snap_m":
                point.distance(
                    Point(node[0], node[1])
                )

        })

    return pd.DataFrame(hasil)


graph_kecamatan = snap_ke_graph(
    snap_node_kecamatan,
    G
)

graph_damkar = snap_ke_graph(
    snap_node_damkar,
    G
)

graph_rs = snap_ke_graph(
    snap_node_rs,
    G
)

graph_puskesmas = snap_ke_graph(
    snap_node_puskesmas,
    G
)

graph_polisi = snap_ke_graph(
    snap_node_polisi,
    G
)


# ============================================================
# 11. FUNGSI SHORTEST PATH
# ============================================================

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


# ============================================================
# 12. HITUNG JARAK KE FASILITAS
# ============================================================

print("\n========================================")
print("MENGHITUNG SHORTEST PATH")
print("========================================")

hasil = []


for idx, kec in graph_kecamatan.iterrows():

    node_asal = (
        kec["node_x"],
        kec["node_y"]
    )

    # ----------------------------------------
    # DAMKAR
    # ----------------------------------------

    jarak_damkar = []

    for _, f in graph_damkar.iterrows():

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

    for _, f in graph_rs.iterrows():

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

    for _, f in graph_puskesmas.iterrows():

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

    for _, f in graph_polisi.iterrows():

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
            titik_kecamatan.iloc[idx]["GID_3"],

        "NAME_3":
            titik_kecamatan.iloc[idx]["NAME_3"],

        "jarak_damkar_km":
            min(jarak_damkar) / 1000
            if jarak_damkar else None,

        "jarak_rs_km":
            min(jarak_rs) / 1000
            if jarak_rs else None,

        "jarak_puskesmas_km":
            min(jarak_puskesmas) / 1000
            if jarak_puskesmas else None,

        "jarak_polisi_km":
            min(jarak_polisi) / 1000
            if jarak_polisi else None

    })


# ============================================================
# 13. HASIL
# ============================================================

hasil = pd.DataFrame(hasil)

print("\n========================================")
print("HASIL SHORTEST PATH")
print("========================================")

print(
    hasil.to_string(index=False)
)


# ============================================================
# 14. SIMPAN HASIL
# ============================================================

hasil.to_csv(
    "output/hasil_shortest_path.csv",
    index=False
)

graph_kecamatan.to_csv(
    "output/graph_kecamatan.csv",
    index=False
)

graph_damkar.to_csv(
    "output/graph_damkar.csv",
    index=False
)

graph_rs.to_csv(
    "output/graph_rs.csv",
    index=False
)

graph_puskesmas.to_csv(
    "output/graph_puskesmas.csv",
    index=False
)

graph_polisi.to_csv(
    "output/graph_polisi.csv",
    index=False
)


print("\n========================================")
print("SELESAI")
print("========================================")
print("Hasil tersimpan:")
print("output/hasil_shortest_path.csv")