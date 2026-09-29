import geopandas as gpd

# ==========================================
# 1. MEMBACA DATA
# ==========================================

admin = gpd.read_file("data/administrasi.geojson")
damkar = gpd.read_file("data/damkar.geojson")
jalan = gpd.read_file("data/jalan.geojson")
polisi = gpd.read_file("data/kantor_polisi.geojson")
puskesmas = gpd.read_file("data/puskesmas.geojson")
rumah_sakit = gpd.read_file("data/rumah_sakit.geojson")


# ==========================================
# 2. CEK CRS
# ==========================================

print("\n===== CRS DATA =====")

print("Administrasi :", admin.crs)
print("Damkar       :", damkar.crs)
print("Jalan        :", jalan.crs)
print("Polisi       :", polisi.crs)
print("Puskesmas    :", puskesmas.crs)
print("Rumah Sakit  :", rumah_sakit.crs)


# ==========================================
# 3. CEK JUMLAH DATA
# ==========================================

print("\n===== JUMLAH DATA =====")

print("Jumlah kecamatan :", len(admin))
print("Jumlah damkar    :", len(damkar))
print("Jumlah jalan     :", len(jalan))
print("Jumlah polisi    :", len(polisi))
print("Jumlah puskesmas :", len(puskesmas))
print("Jumlah rumah sakit :", len(rumah_sakit))


# ==========================================
# 4. CEK KOLOM
# ==========================================

print("\n===== KOLOM DATA ADMINISTRASI =====")
print(admin.columns.tolist())

print("\n===== KOLOM DAMKAR =====")
print(damkar.columns.tolist())

print("\n===== KOLOM JALAN =====")
print(jalan.columns.tolist())

print("\n===== KOLOM POLISI =====")
print(polisi.columns.tolist())

print("\n===== KOLOM PUSKESMAS =====")
print(puskesmas.columns.tolist())

print("\n===== KOLOM RUMAH SAKIT =====")
print(rumah_sakit.columns.tolist())