import geopandas as gpd
import pandas as pd
import networkx as nx

from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union


# ==========================================================
# 1. BACA DATA JALAN
# ==========================================================

print("Membaca data jalan...")

jalan = gpd.read_file("data/jalan.geojson")

print("Jumlah fitur awal:", len(jalan))


# ==========================================================
# 2. UBAH CRS KE UTM 49S
# ==========================================================

jalan = jalan.to_crs("EPSG:32749")

print("CRS:", jalan.crs)


# ==========================================================
# 3. PECAH MULTILINESTRING
# ==========================================================

jalan = jalan.explode(
    index_parts=False
).reset_index(drop=True)

print(
    "Jumlah ruas setelah explode:",
    len(jalan)
)


# ==========================================================
# 4. HAPUS GEOMETRI TIDAK VALID
# ==========================================================

jalan = jalan[
    jalan.geometry.notna()
    & ~jalan.geometry.is_empty
    & jalan.geometry.is_valid
].copy()

print(
    "Jumlah ruas valid:",
    len(jalan)
)


# ==========================================================
# 5. UBAH GEOMETRI MENJADI 2D
# ==========================================================
# Data jalan mempunyai koordinat X, Y, Z.
# Untuk network analysis kita menggunakan X dan Y saja.

print("\nMengubah geometri menjadi 2D...")

def ubah_ke_2d(geom):

    koordinat_2d = [
        (coord[0], coord[1])
        for coord in geom.coords
    ]

    return LineString(koordinat_2d)


jalan["geometry"] = jalan.geometry.apply(
    ubah_ke_2d
)


# ==========================================================
# 6. GABUNG DAN NODE JARINGAN JALAN
# ==========================================================
# unary_union akan:
# - menemukan perpotongan garis
# - memecah garis pada titik perpotongan
# - menghasilkan ruas-ruas baru

print("\nMelakukan noding pada persimpangan...")
print("Proses ini mungkin membutuhkan waktu...")

network_noded = unary_union(
    jalan.geometry.tolist()
)

print("Noding selesai.")


# ==========================================================
# 7. UBAH HASIL MENJADI GEODATAFRAME
# ==========================================================

print("\nMembuat GeoDataFrame hasil noding...")

if isinstance(network_noded, LineString):

    garis_noded = [network_noded]

elif isinstance(network_noded, MultiLineString):

    garis_noded = list(network_noded.geoms)

else:

    garis_noded = []

    for geom in network_noded.geoms:

        if isinstance(geom, LineString):

            garis_noded.append(geom)

        elif isinstance(geom, MultiLineString):

            garis_noded.extend(
                list(geom.geoms)
            )


network = gpd.GeoDataFrame(
    {
        "edge_id": range(len(garis_noded))
    },
    geometry=garis_noded,
    crs="EPSG:32749"
)


# ==========================================================
# 8. HAPUS GARIS KOSONG / TIDAK VALID
# ==========================================================

network = network[
    network.geometry.notna()
    & ~network.geometry.is_empty
    & network.geometry.is_valid
].copy()

network = network.reset_index(drop=True)

network["edge_id"] = range(len(network))


# ==========================================================
# 9. HITUNG PANJANG SETIAP RUAS
# ==========================================================

network["panjang_m"] = (
    network.geometry.length
)


# ==========================================================
# 10. HAPUS RUAS DENGAN PANJANG 0
# ==========================================================

network = network[
    network["panjang_m"] > 0
].copy()

network = network.reset_index(drop=True)

network["edge_id"] = range(len(network))


# ==========================================================
# 11. INFORMASI HASIL NODING
# ==========================================================

print("\n===== HASIL NODING =====")

print(
    "Jumlah ruas sebelum noding:",
    len(jalan)
)

print(
    "Jumlah ruas setelah noding:",
    len(network)
)

print(
    "Total panjang jalan:",
    round(
        network["panjang_m"].sum() / 1000,
        3
    ),
    "km"
)


# ==========================================================
# 12. SIMPAN HASIL NODING
# ==========================================================

output_file = (
    "output/jalan_noded.gpkg"
)

network.to_file(
    output_file,
    layer="jalan_noded",
    driver="GPKG"
)

print(
    "\nHasil network tersimpan di:",
    output_file
)


# ==========================================================
# 13. BUAT GRAPH NETWORK
# ==========================================================

print("\nMembuat graph dari network hasil noding...")


G = nx.Graph()


for _, row in network.iterrows():

    geom = row.geometry

    # Titik awal
    titik_awal = geom.coords[0]

    # Titik akhir
    titik_akhir = geom.coords[-1]

    node_awal = (
        round(titik_awal[0], 3),
        round(titik_awal[1], 3)
    )

    node_akhir = (
        round(titik_akhir[0], 3),
        round(titik_akhir[1], 3)
    )

    panjang = row["panjang_m"]

    G.add_edge(
        node_awal,
        node_akhir,
        weight=panjang
    )


# ==========================================================
# 14. HASIL GRAPH
# ==========================================================

print("\n===== HASIL GRAPH SETELAH NODING =====")

print(
    "Jumlah node:",
    G.number_of_nodes()
)

print(
    "Jumlah edge:",
    G.number_of_edges()
)


# ==========================================================
# 15. CEK KONEKTIVITAS
# ==========================================================

print("\n===== KONEKTIVITAS =====")

jumlah_komponen = (
    nx.number_connected_components(G)
)

print(
    "Jumlah komponen jaringan:",
    jumlah_komponen
)


komponen_terbesar = max(
    nx.connected_components(G),
    key=len
)

print(
    "Node pada komponen terbesar:",
    len(komponen_terbesar)
)


# ==========================================================
# 16. CEK CONTOH NODE
# ==========================================================

print("\n===== CONTOH NODE =====")

for i, node in enumerate(G.nodes):

    print(
        i + 1,
        node
    )

    if i >= 4:
        break


# ==========================================================
# 17. CEK CONTOH EDGE
# ==========================================================

print("\n===== CONTOH EDGE =====")

for i, (u, v, data) in enumerate(
    G.edges(data=True)
):

    print(
        f"Edge {i+1}:",
        u,
        "→",
        v,
        "| panjang =",
        round(data["weight"], 2),
        "meter"
    )

    if i >= 4:
        break


# ==========================================================
# 18. SELESAI
# ==========================================================

print("\n===== SELESAI =====")

print(
    "Network jalan hasil noding berhasil dibuat."
)