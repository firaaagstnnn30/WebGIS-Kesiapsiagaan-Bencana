import geopandas as gpd
import momepy
import networkx as nx

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

jalan = jalan.explode(index_parts=False).reset_index(drop=True)

print("Jumlah ruas setelah explode:", len(jalan))


# ==========================================================
# 4. HAPUS GEOMETRI TIDAK VALID
# ==========================================================

jalan = jalan[
    jalan.geometry.notna()
    & ~jalan.geometry.is_empty
    & jalan.geometry.is_valid
].copy()

print("Jumlah ruas valid:", len(jalan))


# ==========================================================
# 5. BUAT ID UNTUK SETIAP RUAS
# ==========================================================

jalan["edge_id"] = range(len(jalan))
jalan["panjang_m"] = jalan.geometry.length


# ==========================================================
# 6. BUAT NETWORK
# ==========================================================

print("\nMembuat network jalan...")

G = momepy.gdf_to_nx(
    jalan,
    approach="primal",
    length="panjang_m"
)


# ==========================================================
# 7. INFORMASI NETWORK
# ==========================================================

print("\n===== HASIL NETWORK =====")

print("Jumlah node :", G.number_of_nodes())
print("Jumlah edge :", G.number_of_edges())


# ==========================================================
# 8. KOMPONEN JARINGAN
# ==========================================================

print("\n===== KONEKTIVITAS =====")

jumlah_komponen = nx.number_connected_components(G)

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
# 9. CONTOH NODE
# ==========================================================

print("\n===== CONTOH NODE =====")

for i, node in enumerate(G.nodes):

    print(
        i + 1,
        node
    )

    if i == 4:
        break


# ==========================================================
# 10. CONTOH EDGE
# ==========================================================

print("\n===== CONTOH EDGE =====")

for i, (u, v, data) in enumerate(
    G.edges(data=True)
):

    print(
        f"Edge {i+1}:",
        u,
        "→",
        v
    )

    print(
        "Data:",
        data
    )

    if i == 4:
        break


print("\n===== SELESAI =====")
print("Network jalan berhasil dibuat.")