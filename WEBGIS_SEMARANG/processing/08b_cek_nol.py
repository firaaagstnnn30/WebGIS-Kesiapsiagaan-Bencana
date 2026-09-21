import geopandas as gpd
import pandas as pd
import networkx as nx
import math

CRS = "EPSG:32749"

# Baca hasil snap
snap = gpd.read_file(
    "output/titik_snap_final.gpkg",
    layer="titik_snap"
)

# Ambil Ngaliyan
ngaliyan = snap[
    (snap["jenis"] == "kecamatan") &
    (snap["nama"] == "Ngaliyan")
].iloc[0]

node_ngaliyan = (
    ngaliyan["node_x"],
    ngaliyan["node_y"]
)

print("========================================")
print("CEK NGALIYAN → PUSKESMAS")
print("========================================")

print("Node Ngaliyan:")
print(node_ngaliyan)

puskesmas = snap[
    snap["jenis"] == "puskesmas"
].copy()

# Cari puskesmas yang node-nya sama
puskesmas_sama = puskesmas[
    (puskesmas["node_x"] == node_ngaliyan[0]) &
    (puskesmas["node_y"] == node_ngaliyan[1])
]

print("\nPuskesmas dengan node sama:")

if len(puskesmas_sama) == 0:

    print("TIDAK ADA")

else:

    print(
        puskesmas_sama[
            [
                "id",
                "nama",
                "jarak_snap_m",
                "node_x",
                "node_y"
            ]
        ].to_string(index=False)
    )

print("\n========================================")
print("SELESAI")
print("========================================")