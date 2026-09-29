import geopandas as gpd
import networkx as nx
from shapely.geometry import Point


# ============================================================
# 1. PENGATURAN
# ============================================================

CRS_ANALISIS = "EPSG:32749"

FILE_JALAN = "output/jalan_network_fixed.gpkg"
LAYER_JALAN = "jalan_network_final"

FILE_SNAP = "output/titik_snap_fixed.gpkg"
LAYER_SNAP = "titik_snap"


# ============================================================
# 2. BACA DATA
# ============================================================

print("========================================")
print("CEK KOMPONEN JARINGAN")
print("========================================")

jalan = gpd.read_file(
    FILE_JALAN,
    layer=LAYER_JALAN
).to_crs(CRS_ANALISIS)

snap = gpd.read_file(
    FILE_SNAP,
    layer=LAYER_SNAP
).to_crs(CRS_ANALISIS)

print("Jumlah ruas jalan :", len(jalan))
print("Jumlah titik      :", len(snap))


# ============================================================
# 3. FUNGSI NODE
# ============================================================

def node_id(point):
    return (
        round(point.x, 3),
        round(point.y, 3)
    )


# ============================================================
# 4. BUAT GRAPH
# ============================================================

print("\nMembuat graph...")

G = nx.Graph()

for _, row in jalan.iterrows():

    geom = row.geometry

    if geom is None or geom.is_empty:
        continue

    coords = list(geom.coords)

    if len(coords) < 2:
        continue

    node_awal = node_id(
        Point(coords[0])
    )

    node_akhir = node_id(
        Point(coords[-1])
    )

    panjang = geom.length

    if panjang <= 0:
        continue

    G.add_edge(
        node_awal,
        node_akhir,
        weight=panjang
    )


print("Jumlah node :", G.number_of_nodes())
print("Jumlah edge :", G.number_of_edges())


# ============================================================
# 5. KOMPONEN JARINGAN
# ============================================================

komponen = list(
    nx.connected_components(G)
)

print("Jumlah komponen :", len(komponen))

komponen_sorted = sorted(
    komponen,
    key=len,
    reverse=True
)

print("\n10 komponen terbesar:")

for i, comp in enumerate(
    komponen_sorted[:10],
    start=1
):

    print(
        f"Komponen {i}: {len(comp)} node"
    )


# ============================================================
# 6. BUAT ID KOMPONEN
# ============================================================

node_ke_komponen = {}

for i, comp in enumerate(
    komponen_sorted,
    start=1
):

    for node in comp:

        node_ke_komponen[node] = i


# ============================================================
# 7. HUBUNGKAN TITIK SNAP KE NODE
# ============================================================

print("\n========================================")
print("MENGECEK 177 TITIK ANALISIS")
print("========================================")

snap["node_x"] = snap["node_x"].astype(float)
snap["node_y"] = snap["node_y"].astype(float)

snap["komponen"] = None

for idx, row in snap.iterrows():

    node = (
        round(row["node_x"], 3),
        round(row["node_y"], 3)
    )

    if node in node_ke_komponen:

        snap.loc[
            idx,
            "komponen"
        ] = node_ke_komponen[node]

    else:

        snap.loc[
            idx,
            "komponen"
        ] = "TIDAK DITEMUKAN"


# ============================================================
# 8. RINGKASAN KOMPONEN TITIK
# ============================================================

print("\nDistribusi titik berdasarkan komponen:")

print(
    snap[
        "komponen"
    ].value_counts()
)


# ============================================================
# 9. CEK TITIK DI LUAR KOMPONEN TERBESAR
# ============================================================

komponen_utama = 1

di_luar = snap[
    snap["komponen"] != komponen_utama
].copy()

print("\n========================================")
print("TITIK DI LUAR KOMPONEN UTAMA")
print("========================================")

print(
    "Jumlah:",
    len(di_luar)
)

if len(di_luar) > 0:

    print(
        di_luar[
            [
                "jenis",
                "id",
                "nama",
                "komponen"
            ]
        ].to_string(
            index=False
        )
    )

else:

    print(
        "SEMUA titik berada pada "
        "komponen jaringan utama."
    )


# ============================================================
# 10. CEK KHUSUS 16 KECAMATAN
# ============================================================

print("\n========================================")
print("KOMPONEN 16 KECAMATAN")
print("========================================")

cek_kec = snap[
    snap["jenis"] == "kecamatan"
].copy()

print(
    cek_kec[
        [
            "nama",
            "komponen"
        ]
    ].sort_values(
        "nama"
    ).to_string(
        index=False
    )
)


# ============================================================
# 11. SIMPAN HASIL CEK
# ============================================================

snap.to_file(
    "output/cek_komponen_titik.gpkg",
    layer="cek_komponen",
    driver="GPKG"
)


print("\n========================================")
print("SELESAI")
print("========================================")

print(
    "Hasil disimpan di:"
)

print(
    "output/cek_komponen_titik.gpkg"
)