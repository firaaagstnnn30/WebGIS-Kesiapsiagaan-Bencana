import pandas as pd
import os

# ============================================================
# 1. PENGATURAN FILE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PEMENUHAN = os.path.join(
    BASE_DIR,
    "..",
    "output",
    "evaluasi_pemenuhan_fasilitas.csv"
)

FILE_AKSES = os.path.join(
    BASE_DIR,
    "..",
    "output",
    "indeks_aksesibilitas.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "output"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. BACA DATA
# ============================================================

print("=" * 75)
print("INDEKS FINAL EVALUASI FASILITAS DAN AKSESIBILITAS")
print("=" * 75)

pemenuhan = pd.read_csv(FILE_PEMENUHAN)

akses = pd.read_csv(FILE_AKSES)

print("\nData pemenuhan :", len(pemenuhan), "kecamatan")
print("Data aksesibilitas :", len(akses), "kecamatan")


# ============================================================
# 3. CEK KOLOM
# ============================================================

kolom_pemenuhan = [
    "GID_3",
    "NAME_3",
    "pemenuhan_damkar_persen",
    "pemenuhan_polisi_persen",
    "pemenuhan_puskesmas_persen",
    "pemenuhan_rs_persen"
]

for kolom in kolom_pemenuhan:
    if kolom not in pemenuhan.columns:
        raise ValueError(
            f"Kolom '{kolom}' tidak ditemukan pada "
            "evaluasi_pemenuhan_fasilitas.csv"
        )

if "GID_3" not in akses.columns:
    raise ValueError(
        "Kolom 'GID_3' tidak ditemukan pada indeks_aksesibilitas.csv"
    )

if "indeks_aksesibilitas" not in akses.columns:
    raise ValueError(
        "Kolom 'indeks_aksesibilitas' tidak ditemukan pada "
        "indeks_aksesibilitas.csv"
    )


# ============================================================
# 4. BATASI PEMENUHAN MAKSIMUM 100%
# ============================================================

pemenuhan["skor_damkar_sni"] = (
    pemenuhan["pemenuhan_damkar_persen"].clip(upper=100)
)

pemenuhan["skor_polisi_sni"] = (
    pemenuhan["pemenuhan_polisi_persen"].clip(upper=100)
)

pemenuhan["skor_puskesmas_sni"] = (
    pemenuhan["pemenuhan_puskesmas_persen"].clip(upper=100)
)

pemenuhan["skor_rs_sni"] = (
    pemenuhan["pemenuhan_rs_persen"].clip(upper=100)
)


# ============================================================
# 5. HITUNG SKOR PEMENUHAN SNI
# ============================================================

pemenuhan["skor_pemenuhan_sni"] = (
    pemenuhan[
        [
            "skor_damkar_sni",
            "skor_polisi_sni",
            "skor_puskesmas_sni",
            "skor_rs_sni"
        ]
    ]
    .mean(axis=1)
)


# ============================================================
# 6. GABUNGKAN DENGAN INDEKS AKSESIBILITAS
# ============================================================

hasil = pemenuhan.merge(
    akses[
        [
            "GID_3",
            "indeks_aksesibilitas"
        ]
    ],
    on="GID_3",
    how="left"
)


# ============================================================
# 7. CEK DATA AKSESIBILITAS
# ============================================================

if hasil["indeks_aksesibilitas"].isna().any():

    print("\nPERINGATAN:")
    print("Ada kecamatan yang tidak memiliki indeks aksesibilitas.")

    print(
        hasil.loc[
            hasil["indeks_aksesibilitas"].isna(),
            ["GID_3", "NAME_3"]
        ]
    )

    raise ValueError(
        "Periksa kecocokan GID_3 antara kedua file."
    )


# ============================================================
# 8. KONVERSI SKOR AKSESIBILITAS MENJADI 0-100
# ============================================================

# Indeks aksesibilitas sebelumnya berada pada skala 1-3.
#
# 1 = nilai aksesibilitas terendah
# 3 = nilai aksesibilitas tertinggi

hasil["skor_aksesibilitas_100"] = (
    (hasil["indeks_aksesibilitas"] - 1)
    / 2
    * 100
)


# ============================================================
# 9. BOBOT
# ============================================================

BOBOT_SNI = 0.50
BOBOT_AKSES = 0.50


# ============================================================
# 10. HITUNG INDEKS FINAL
# ============================================================

hasil["indeks_final"] = (
    hasil["skor_pemenuhan_sni"] * BOBOT_SNI
    +
    hasil["skor_aksesibilitas_100"] * BOBOT_AKSES
)


# ============================================================
# 11. KLASIFIKASI
# ============================================================

# Klasifikasi menggunakan equal interval berdasarkan
# rentang nilai indeks final hasil penelitian.
#
# Catatan:
# batas kelas ini merupakan metode klasifikasi penelitian,
# BUKAN batas resmi SNI.

nilai_min = hasil["indeks_final"].min()
nilai_max = hasil["indeks_final"].max()

interval = (nilai_max - nilai_min) / 3


batas_1 = nilai_min + interval
batas_2 = nilai_min + (2 * interval)


def klasifikasi(nilai):

    if nilai <= batas_1:
        return "Rendah"

    elif nilai <= batas_2:
        return "Sedang"

    else:
        return "Tinggi"


hasil["kelas_final"] = hasil["indeks_final"].apply(
    klasifikasi
)


# ============================================================
# 12. PEMBULATAN
# ============================================================

kolom_bulat = [
    "skor_damkar_sni",
    "skor_polisi_sni",
    "skor_puskesmas_sni",
    "skor_pemenuhan_sni",
    "indeks_aksesibilitas",
    "skor_aksesibilitas_100",
    "indeks_final"
]

for kolom in kolom_bulat:
    hasil[kolom] = hasil[kolom].round(2)


# ============================================================
# 13. TAMPILKAN HASIL
# ============================================================

print("\n")
print("HASIL INDEKS FINAL")
print("-" * 110)

kolom_tampil = [
    "NAME_3",

    "skor_damkar_sni",
    "skor_polisi_sni",
    "skor_puskesmas_sni",

    "skor_pemenuhan_sni",

    "indeks_aksesibilitas",
    "skor_aksesibilitas_100",

    "indeks_final",
    "kelas_final"
]

print(
    hasil[
        kolom_tampil
    ]
    .sort_values(
        "indeks_final",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# 14. INFORMASI BATAS KELAS
# ============================================================

print("\n")
print("=" * 75)
print("BATAS KLASIFIKASI")
print("=" * 75)

print(f"Nilai minimum : {nilai_min:.2f}")
print(f"Nilai maksimum : {nilai_max:.2f}")
print(f"Interval kelas : {interval:.2f}")

print(f"\nRendah : {nilai_min:.2f} - {batas_1:.2f}")
print(f"Sedang : {batas_1:.2f} - {batas_2:.2f}")
print(f"Tinggi : {batas_2:.2f} - {nilai_max:.2f}")


# ============================================================
# 15. JUMLAH KECAMATAN PER KELAS
# ============================================================

print("\n")
print("JUMLAH KECAMATAN PER KELAS")
print("-" * 75)

print(
    hasil["kelas_final"]
    .value_counts()
    .to_string()
)


# ============================================================
# 16. SIMPAN
# ============================================================

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "indeks_final_evaluasi.csv"
)

hasil.to_csv(
    OUTPUT_CSV,
    index=False
)


# ============================================================
# 17. SELESAI
# ============================================================

print("\n")
print("=" * 75)
print("SELESAI")
print("=" * 75)

print("\nOutput:")
print(OUTPUT_CSV)