import geopandas as gpd
import pandas as pd
import os

# ============================================================
# 1. PENGATURAN FILE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_ADMIN = os.path.join(
    BASE_DIR, "..", "data", "administrasi.geojson"
)

FILE_DAMKAR = os.path.join(
    BASE_DIR, "..", "data", "damkar.geojson"
)

FILE_POLISI = os.path.join(
    BASE_DIR, "..", "data", "kantor_polisi.geojson"
)

FILE_PUSKESMAS = os.path.join(
    BASE_DIR, "..", "data", "puskesmas.geojson"
)

FILE_RUMAH_SAKIT = os.path.join(
    BASE_DIR, "..", "data", "rumah_sakit.geojson"
)

FILE_KEBUTUHAN = os.path.join(
    BASE_DIR, "..", "output", "kebutuhan_fasilitas_sni.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "..", "output"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. BACA DATA
# ============================================================

print("=" * 70)
print("EVALUASI PEMENUHAN FASILITAS DARURAT KOTA SEMARANG")
print("=" * 70)

admin = gpd.read_file(FILE_ADMIN)
damkar = gpd.read_file(FILE_DAMKAR)
polisi = gpd.read_file(FILE_POLISI)
puskesmas = gpd.read_file(FILE_PUSKESMAS)
rumah_sakit = gpd.read_file(FILE_RUMAH_SAKIT)

kebutuhan = pd.read_csv(FILE_KEBUTUHAN)


print("\nDATA YANG DIBACA")
print("-" * 70)
print("Kecamatan   :", len(admin))
print("Damkar      :", len(damkar))
print("Polisi      :", len(polisi))
print("Puskesmas   :", len(puskesmas))
print("Rumah Sakit :", len(rumah_sakit))


# ============================================================
# 3. SAMAKAN CRS
# ============================================================

if admin.crs is None:
    raise ValueError("CRS administrasi tidak tersedia.")

damkar = damkar.to_crs(admin.crs)
polisi = polisi.to_crs(admin.crs)
puskesmas = puskesmas.to_crs(admin.crs)
rumah_sakit = rumah_sakit.to_crs(admin.crs)


# ============================================================
# 4. FUNGSI MENGHITUNG JUMLAH FASILITAS PER KECAMATAN
# ============================================================

def hitung_fasilitas_per_kecamatan(
    admin_data,
    fasilitas_data,
    nama_kolom_hasil
):
    batas = admin_data[["GID_3", "geometry"]].copy()
    fasilitas_data = fasilitas_data[
        fasilitas_data.geometry.notna()
    ].copy()

    hasil_join = gpd.sjoin(
        fasilitas_data,
        batas,
        how="left",
        predicate="within"
    )

    jumlah = (
        hasil_join
        .dropna(subset=["GID_3"])
        .groupby("GID_3")
        .size()
        .reset_index(name=nama_kolom_hasil)
    )

    return jumlah


# ============================================================
# 5. HITUNG FASILITAS EKSISTING
# ============================================================

jumlah_damkar = hitung_fasilitas_per_kecamatan(
    admin, damkar, "eksisting_damkar"
)

jumlah_polisi = hitung_fasilitas_per_kecamatan(
    admin, polisi, "eksisting_kantor_polisi"
)

jumlah_puskesmas = hitung_fasilitas_per_kecamatan(
    admin, puskesmas, "eksisting_puskesmas"
)

jumlah_rs = hitung_fasilitas_per_kecamatan(
    admin, rumah_sakit, "eksisting_rumah_sakit"
)


# ============================================================
# 6. GABUNGKAN DENGAN KEBUTUHAN
# ============================================================

hasil = kebutuhan.copy()

hasil = hasil.merge(jumlah_damkar, on="GID_3", how="left")
hasil = hasil.merge(jumlah_polisi, on="GID_3", how="left")
hasil = hasil.merge(jumlah_puskesmas, on="GID_3", how="left")
hasil = hasil.merge(jumlah_rs, on="GID_3", how="left")


# ============================================================
# 7. ISI FASILITAS YANG TIDAK ADA DENGAN NILAI 0
# ============================================================

kolom_eksisting = [
    "eksisting_damkar",
    "eksisting_kantor_polisi",
    "eksisting_puskesmas",
    "eksisting_rumah_sakit"
]

for kolom in kolom_eksisting:
    hasil[kolom] = hasil[kolom].fillna(0).astype(int)


# ============================================================
# 8. HITUNG PERSENTASE PEMENUHAN
# ============================================================

hasil["pemenuhan_damkar_persen"] = (
    hasil["eksisting_damkar"] / hasil["kebutuhan_pos_damkar"] * 100
)

hasil["pemenuhan_polisi_persen"] = (
    hasil["eksisting_kantor_polisi"] / hasil["kebutuhan_kantor_polisi"] * 100
)

hasil["pemenuhan_puskesmas_persen"] = (
    hasil["eksisting_puskesmas"] / hasil["kebutuhan_puskesmas"] * 100
)

hasil["pemenuhan_rs_persen"] = (
    hasil["eksisting_rumah_sakit"] / hasil["kebutuhan_rumah_sakit"] * 100
)


# ============================================================
# 9. STATUS PEMENUHAN PER FASILITAS & STATUS UMUM
# ============================================================

hasil["status_damkar"] = hasil.apply(
    lambda r: "Memenuhi" if r["eksisting_damkar"] >= r["kebutuhan_pos_damkar"] else "Belum Memenuhi", axis=1
)

hasil["status_polisi"] = hasil.apply(
    lambda r: "Memenuhi" if r["eksisting_kantor_polisi"] >= r["kebutuhan_kantor_polisi"] else "Belum Memenuhi", axis=1
)

hasil["status_puskesmas"] = hasil.apply(
    lambda r: "Memenuhi" if r["eksisting_puskesmas"] >= r["kebutuhan_puskesmas"] else "Belum Memenuhi", axis=1
)

hasil["status_rs"] = hasil.apply(
    lambda r: "Memenuhi" if r["eksisting_rumah_sakit"] >= r["kebutuhan_rumah_sakit"] else "Belum Memenuhi", axis=1
)

hasil["status_pemenuhan_umum"] = hasil.apply(
    lambda r: "Sudah Memenuhi" if (
        r["eksisting_damkar"] >= r["kebutuhan_pos_damkar"] and
        r["eksisting_kantor_polisi"] >= r["kebutuhan_kantor_polisi"] and
        r["eksisting_puskesmas"] >= r["kebutuhan_puskesmas"] and
        r["eksisting_rumah_sakit"] >= r["kebutuhan_rumah_sakit"]
    ) else "Belum Memenuhi", axis=1
)


# ============================================================
# 10. RINCIAN KEKURANGAN FASILITAS
# ============================================================

def hitung_rincian_kekurangan(row):
    kekurangan = []
    
    kurang_damkar = int(row["kebutuhan_pos_damkar"] - row["eksisting_damkar"])
    if kurang_damkar > 0:
        kekurangan.append(f"Kurang {kurang_damkar} Pos Damkar")
        
    kurang_polisi = int(row["kebutuhan_kantor_polisi"] - row["eksisting_kantor_polisi"])
    if kurang_polisi > 0:
        kekurangan.append(f"Kurang {kurang_polisi} Kantor Polisi")
        
    kurang_puskesmas = int(row["kebutuhan_puskesmas"] - row["eksisting_puskesmas"])
    if kurang_puskesmas > 0:
        kekurangan.append(f"Kurang {kurang_puskesmas} Puskesmas")
        
    kurang_rs = int(row["kebutuhan_rumah_sakit"] - row["eksisting_rumah_sakit"])
    if kurang_rs > 0:
        kekurangan.append(f"Kurang {kurang_rs} Rumah Sakit")
        
    if not kekurangan:
        return "Sudah Memenuhi Kebutuhan"
    else:
        return ", ".join(kekurangan)

hasil["rincian_kekurangan"] = hasil.apply(hitung_rincian_kekurangan, axis=1)


# ============================================================
# 11. RATA-RATA PEMENUHAN
# ============================================================

hasil["rata_rata_pemenuhan_persen"] = (
    hasil[
        [
            "pemenuhan_damkar_persen",
            "pemenuhan_polisi_persen",
            "pemenuhan_puskesmas_persen",
            "pemenuhan_rs_persen"
        ]
    ]
    .mean(axis=1)
)


# ============================================================
# 12. PEMBULATAN ANGKA
# ============================================================

kolom_persen = [
    "pemenuhan_damkar_persen",
    "pemenuhan_polisi_persen",
    "pemenuhan_puskesmas_persen",
    "pemenuhan_rs_persen",
    "rata_rata_pemenuhan_persen"
]

for kolom in kolom_persen:
    hasil[kolom] = hasil[kolom].round(2)


# ============================================================
# 13. TAMPILKAN HASIL
# ============================================================

print("\n")
print("HASIL EVALUASI PEMENUHAN FASILITAS")
print("-" * 120)

kolom_tampil = [
    "NAME_3",
    "Penduduk",
    "status_pemenuhan_umum",
    "rincian_kekurangan"
]

print(hasil[kolom_tampil].to_string(index=False))


# ============================================================
# 14. SIMPAN HASIL
# ============================================================

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "evaluasi_pemenuhan_fasilitas.csv"
)

hasil.to_csv(
    OUTPUT_CSV,
    index=False
)

print("\nOutput disimpan ke:", OUTPUT_CSV)