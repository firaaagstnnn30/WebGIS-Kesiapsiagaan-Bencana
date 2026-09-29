import geopandas as gpd
import networkx as nx
from shapely.geometry import Point

# ==========================================================
# 1. BACA DATA JALAN
# ==========================================================

print("Membaca data jalan...")

jalan = gpd.read_file("data/jalan.geojson")

# Ubah ke UTM 49S untuk analisis jarak
jalan = jalan.to_crs("EPSG:32749")

print("Jumlah fitur awal:", len(jalan))


# ==========================================================
# 2. PECAH MULTILINESTRING MENJADI LINESTRING
# ==========================================================

jalan = jalan.explode(index_parts=False).reset_index(drop=True)

print("Jumlah ruas setelah explode:", len(jalan))


# ==========================================================
# 3. BUANG GEOMETRI YANG TIDAK VALID
# ==========================================================

jalan = jalan[
    jalan.geometry.notna() &
    ~jalan.geometry.is_empty &
    jalan.geometry.is_valid
].copy()

print("Jumlah ruas valid:", len(jalan))


# ==========================================================
# 4. BUAT GRAPH
# ==========================================================

print("\nMembuat graph jaringan jalan...")

G = nx.Graph()

for i, row in jalan.iterrows():

    geom = row.geometry

    # Koordinat titik awal
    titik_awal = geom.coords[0]

    # Koordinat titik akhir
    titik_akhir = geom.coords[-1]

    # Ambil X dan Y saja, abaikan Z
    node_awal = (
        round(titik_awal[0], 3),
        round(titik_awal[1], 3)
    )

    node_akhir = (
        round(titik_akhir[0], 3),
        round(titik_akhir[1], 3)
    )

    # Panjang ruas dalam meter
    panjang = geom.length

    # Tambahkan edge
    G.add_edge(
        node_awal,
        node_akhir,
        weight=panjang
    )


# ==========================================================
# 5. INFORMASI GRAPH
# ==========================================================

print("\n===== HASIL GRAPH =====")

print("Jumlah node :", G.number_of_nodes())
print("Jumlah edge :", G.number_of_edges())


# ==========================================================
# 6. CEK KONEKTIVITAS
# ==========================================================

print("\n===== KONEKTIVITAS =====")

jumlah_komponen = nx.number_connected_components(G)

print("Jumlah komponen jaringan:", jumlah_komponen)

komponen_terbesar = max(
    nx.connected_components(G),
    key=len
)

print(
    "Node pada komponen terbesar:",
    len(komponen_terbesar)
)


# ==========================================================
# 7. CEK CONTOH NODE
# ==========================================================

print("\n===== CONTOH NODE =====")

for i, node in enumerate(G.nodes):

    print(i + 1, node)

    if i == 4:
        break


# ==========================================================
# 8. CEK CONTOH EDGE
# ==========================================================

print("\n===== CONTOH EDGE =====")

for i, (u, v, data) in enumerate(G.edges(data=True)):

    print(
        f"Edge {i+1}:",
        u,
        "→",
        v,
        "| panjang =",
        round(data["weight"], 2),
        "meter"
    )

    if i == 4:
        break


print("\n===== SELESAI =====")
print("Graph jaringan jalan berhasil dibuat.")