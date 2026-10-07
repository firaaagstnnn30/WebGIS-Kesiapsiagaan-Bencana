import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.strtree import STRtree
import os
import json

print("=" * 70)
print("ANALISIS CAKUPAN LAYANAN FASILITAS DENGAN ISOCHRONE & WORLDPOP")
print("=" * 70)

CRS_ANALISIS = "EPSG:32749"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_JALAN = os.path.join(BASE_DIR, "..", "output", "jalan_network_fixed.gpkg")
FILE_SNAP = os.path.join(BASE_DIR, "..", "output", "titik_snap_fixed.gpkg")
FILE_ADMIN = os.path.join(BASE_DIR, "..", "data", "administrasi.geojson")
FILE_RASTER = os.path.join(BASE_DIR, "..", "worldpop_semarang.tif")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")

# 1. BACA DATA
print("\n[1/6] Membaca data jaringan jalan, fasilitas, dan batas administrasi...")
jalan = gpd.read_file(FILE_JALAN).to_crs(CRS_ANALISIS)
snap = gpd.read_file(FILE_SNAP).to_crs(CRS_ANALISIS)
admin = gpd.read_file(FILE_ADMIN).to_crs(CRS_ANALISIS)

# 2. BUAT GRAPH JALAN
print("[2/6] Membangun graph jaringan jalan...")
G = nx.Graph()
for idx, row in jalan.iterrows():
    geom = row.geometry
    if geom and geom.geom_type == "LineString":
        coords = geom.coords
        n1 = (round(coords[0][0], 2), round(coords[0][1], 2))
        n2 = (round(coords[-1][0], 2), round(coords[-1][1], 2))
        G.add_edge(n1, n2, weight=geom.length)

node_points = [Point(n[0], n[1]) for n in G.nodes()]
tree = STRtree(node_points)

# 3. DEFINISI WAKTU TANGGAP & PARAMETER KECEPATAN
# Kecepatan darurat dalam kota: 30 km/jam = 500 meter / menit
# Damkar: 15 menit (Standar Response Time Permendagri / Damkar Nasional) -> 7.500 m
# Polisi: 15 menit -> 7.500 m
# Puskesmas: 15 menit -> 7.500 m
# Rumah Sakit: 30 menit -> 15.000 m (dan 15 menit -> 7.500 m)
KECEPATAN_M_PER_MENIT = 500  # 30 km/jam

PARAM_FASILITAS = {
    "damkar": {
        "nama": "Pemadam Kebakaran",
        "waktu_menit": 15,
        "cutoff_m": 15 * KECEPATAN_M_PER_MENIT,
        "warna": "#ef4444",
        "standar_jiwa": 90000
    },
    "polisi": {
        "nama": "Kantor Polisi",
        "waktu_menit": 15,
        "cutoff_m": 15 * KECEPATAN_M_PER_MENIT,
        "warna": "#3b82f6",
        "standar_jiwa": 30000
    },
    "puskesmas": {
        "nama": "Puskesmas",
        "waktu_menit": 15,
        "cutoff_m": 15 * KECEPATAN_M_PER_MENIT,
        "warna": "#10b981",
        "standar_jiwa": 120000
    },
    "rumah_sakit": {
        "nama": "Rumah Sakit",
        "waktu_menit": 30,
        "cutoff_m": 30 * KECEPATAN_M_PER_MENIT,
        "warna": "#8b5cf6",
        "standar_jiwa": 240000
    }
}

# 4. BUAT POLIGON ISOCHRONE
print("\n[3/6] Menghitung poligon isochrone jangkauan per jenis fasilitas...")
isochrone_polygons = {}
isochrone_geojson_features = []

for jenis, param in PARAM_FASILITAS.items():
    pts = snap[snap["jenis"] == jenis]
    sources = []
    for idx, row in pts.iterrows():
        p = Point(row["node_x"], row["node_y"])
        idx_near = tree.nearest(p)
        sources.append((round(node_points[idx_near].x, 2), round(node_points[idx_near].y, 2)))
    
    # Hitung multi-source Dijkstra
    lengths = nx.multi_source_dijkstra_path_length(G, sources, cutoff=param["cutoff_m"])
    sub = G.subgraph(lengths.keys())
    
    edges = [LineString([Point(u), Point(v)]) for u, v in sub.edges()]
    if edges:
        edge_gdf = gpd.GeoDataFrame(geometry=edges, crs=CRS_ANALISIS)
        # Buffer 200m koridor permukiman sepanjang jaringan jalan yang terjangkau
        iso_poly = edge_gdf.geometry.buffer(200).union_all()
        # Simplify sedikit agar GeoJSON tidak terlalu berat
        iso_poly = iso_poly.simplify(15)
        isochrone_polygons[jenis] = iso_poly
        
        # Simpan untuk layer GeoJSON di WebGIS (diubah ke EPSG:4326)
        iso_gdf = gpd.GeoDataFrame([{"jenis": jenis, "nama": param["nama"], "waktu_menit": param["waktu_menit"], "warna": param["warna"]}], geometry=[iso_poly], crs=CRS_ANALISIS).to_crs("EPSG:4326")
        isochrone_geojson_features.append(iso_gdf)
        
        print(f"  -> {param['nama']:<20}: {len(pts)} titik, jangkauan {param['waktu_menit']} menit ({param['cutoff_m']} m), luas jangkauan: {iso_poly.area / 1e6:.1f} km²")

# Gabungkan dan simpan file isochrone geojson
all_isochrones = gpd.GeoDataFrame(pd.concat(isochrone_geojson_features, ignore_index=True), crs="EPSG:4326")
all_isochrones.to_file(os.path.join(OUTPUT_DIR, "isochrone_fasilitas.geojson"), driver="GeoJSON")
print("  ✓ Tersimpan: output/isochrone_fasilitas.geojson")

# 5. HITUNG CAKUPAN PENDUDUK WORLDPOP PER KECAMATAN
print("\n[4/6] Menghitung cakupan penduduk WorldPop per kecamatan...")
with rasterio.open(FILE_RASTER) as src:
    nodata = src.nodata
    
    hasil_kecamatan = []
    
    for idx, row in admin.iterrows():
        kec_name = row["NAME_3"]
        gid = row["GID_3"]
        geom_kec = row.geometry
        
        # Hitung total WorldPop di kecamatan ini
        try:
            out_img, _ = mask(src, [geom_kec], crop=True)
            d = out_img[0]
            if nodata is not None:
                mask_valid = (d != nodata) & (~np.isnan(d)) & (d >= 0)
            else:
                mask_valid = (~np.isnan(d)) & (d >= 0)
            pop_total_kec = float(np.sum(d[mask_valid]))
        except Exception as e:
            pop_total_kec = 0.0
        
        row_res = {
            "GID_3": gid,
            "NAME_3": kec_name,
            "worldpop_total": round(pop_total_kec, 0)
        }
        
        # Untuk setiap faskes, hitung irisan isochrone dengan kecamatan
        skor_faskes_list = []
        for jenis, param in PARAM_FASILITAS.items():
            iso_geom = isochrone_polygons.get(jenis)
            if iso_geom and geom_kec.intersects(iso_geom):
                irisan = geom_kec.intersection(iso_geom)
                if not irisan.is_empty:
                    try:
                        out_faskes, _ = mask(src, [irisan], crop=True)
                        dfaskes = out_faskes[0]
                        if nodata is not None:
                            mf = (dfaskes != nodata) & (~np.isnan(dfaskes)) & (dfaskes >= 0)
                        else:
                            mf = (~np.isnan(dfaskes)) & (dfaskes >= 0)
                        pop_tercover = float(np.sum(dfaskes[mf]))
                    except Exception:
                        pop_tercover = 0.0
                else:
                    pop_tercover = 0.0
            else:
                pop_tercover = 0.0
                
            pct_cover = (pop_tercover / pop_total_kec * 100) if pop_total_kec > 0 else 0.0
            pct_cover = min(100.0, pct_cover)
            
            row_res[f"pop_tercover_{jenis}"] = round(pop_tercover, 0)
            row_res[f"persen_cakupan_{jenis}"] = round(pct_cover, 1)
            skor_faskes_list.append(pct_cover)
            
        # Rata-rata indeks aksesibilitas isochrone
        indeks_isochrone = float(np.mean(skor_faskes_list))
        row_res["indeks_isochrone"] = round(indeks_isochrone, 1)
        
        hasil_kecamatan.append(row_res)

df_hasil = pd.DataFrame(hasil_kecamatan)

# 6. KLASIFIKASI & RANKING KECAMATAN
print("\n[5/6] Mengklasifikasikan & merangking kecamatan...")
min_val = df_hasil["indeks_isochrone"].min()
max_val = df_hasil["indeks_isochrone"].max()
interval = (max_val - min_val) / 3
b1 = min_val + interval
b2 = min_val + (2 * interval)

def klas_iso(val):
    if val <= b1:
        return "Rendah"
    elif val <= b2:
        return "Sedang"
    else:
        return "Tinggi"

df_hasil["kelas_isochrone"] = df_hasil["indeks_isochrone"].apply(klas_iso)
df_hasil["rank_isochrone"] = df_hasil["indeks_isochrone"].rank(ascending=False, method="min").astype(int)
df_hasil = df_hasil.sort_values(by="indeks_isochrone", ascending=False).reset_index(drop=True)

# Simpan CSV hasil analisis isochrone
csv_iso_path = os.path.join(OUTPUT_DIR, "cakupan_isochrone_worldpop.csv")
df_hasil.to_csv(csv_iso_path, index=False)
print("  ✓ Tersimpan: output/cakupan_isochrone_worldpop.csv")

# Tampilkan tabel ranking
print("\n" + "=" * 95)
print(f"{'Rank':<5} | {'Kecamatan':<18} | {'Populasi (WP)':<14} | {'RS (%)':<8} | {'PKM (%)':<8} | {'Damkar (%)':<10} | {'Polisi (%)':<10} | {'Indeks (%)':<10} | {'Kelas'}")
print("-" * 95)
for idx, r in df_hasil.iterrows():
    print(f"{r['rank_isochrone']:<5} | {r['NAME_3']:<18} | {r['worldpop_total']:<14,.0f} | {r['persen_cakupan_rumah_sakit']:<8.1f} | {r['persen_cakupan_puskesmas']:<8.1f} | {r['persen_cakupan_damkar']:<10.1f} | {r['persen_cakupan_polisi']:<10.1f} | {r['indeks_isochrone']:<10.1f} | {r['kelas_isochrone']}")
print("=" * 95)

# 7. UPDATE FILE kecamatan_aksesibilitas.geojson UNTUK WEBGIS
print("\n[6/6] Memperbarui file output/kecamatan_aksesibilitas.geojson...")
geo_file = os.path.join(OUTPUT_DIR, "kecamatan_aksesibilitas.geojson")
gdf_web = gpd.read_file(geo_file)

# Merge kolom-kolom baru
kolom_tambah = [
    "worldpop_total",
    "pop_tercover_damkar", "persen_cakupan_damkar",
    "pop_tercover_polisi", "persen_cakupan_polisi",
    "pop_tercover_puskesmas", "persen_cakupan_puskesmas",
    "pop_tercover_rumah_sakit", "persen_cakupan_rumah_sakit",
    "indeks_isochrone", "kelas_isochrone", "rank_isochrone"
]

# Drop if exists already to avoid duplicates
for col in kolom_tambah:
    if col in gdf_web.columns:
        gdf_web = gdf_web.drop(columns=[col])

gdf_web = gdf_web.merge(df_hasil[["GID_3"] + kolom_tambah], on="GID_3", how="left")

# Hitung ulang Indeks Final berbasis 50% Pemenuhan SNI + 50% Aksesibilitas Isochrone
gdf_web["indeks_final"] = (
    0.50 * gdf_web["skor_pemenuhan_sni"] + 
    0.50 * gdf_web["indeks_isochrone"]
).round(2)

min_f = gdf_web["indeks_final"].min()
max_f = gdf_web["indeks_final"].max()
int_f = (max_f - min_f) / 3
bf1 = min_f + int_f
bf2 = min_f + 2 * int_f

def klas_final_baru(v):
    if v <= bf1:
        return "Rendah"
    elif v <= bf2:
        return "Sedang"
    else:
        return "Tinggi"

gdf_web["kelas_final"] = gdf_web["indeks_final"].apply(klas_final_baru)

gdf_web.to_file(geo_file, driver="GeoJSON")
print("  ✓ Tersimpan: output/kecamatan_aksesibilitas.geojson (berhasil di-update dengan Indeks Final berbasis Isochrone)")
print("\nAnalisis Isochrone & WorldPop SELESAI DENGAN SUKSES!")
