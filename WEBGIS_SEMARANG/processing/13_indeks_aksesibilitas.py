import pandas as pd


# ============================================================
# 1. PATH
# ============================================================

INPUT_FILE = "output/hasil_road_density.csv"

OUTPUT_FILE = "output/indeks_aksesibilitas.csv"


# ============================================================
# 2. BACA DATA
# ============================================================

print("\n========================================")
print("MEMBACA DATA SKOR")
print("========================================")

df = pd.read_csv(INPUT_FILE)

print("Jumlah kecamatan:", len(df))


# ============================================================
# 3. CEK KOLOM
# ============================================================

kolom_indikator = [
    "skor_damkar",
    "skor_rs",
    "skor_puskesmas",
    "skor_polisi",
    "skor_jalan"
]

print("\nKolom indikator:")

for kolom in kolom_indikator:
    print("-", kolom)


# ============================================================
# 4. BOBOT
# ============================================================

BOBOT_DAMKAR = 0.20
BOBOT_RS = 0.20
BOBOT_PUSKESMAS = 0.20
BOBOT_POLISI = 0.20
BOBOT_JALAN = 0.20


# ============================================================
# 5. HITUNG NILAI TERBOBOT
# ============================================================

df["nilai_damkar"] = (
    df["skor_damkar"]
    * BOBOT_DAMKAR
)

df["nilai_rs"] = (
    df["skor_rs"]
    * BOBOT_RS
)

df["nilai_puskesmas"] = (
    df["skor_puskesmas"]
    * BOBOT_PUSKESMAS
)

df["nilai_polisi"] = (
    df["skor_polisi"]
    * BOBOT_POLISI
)

df["nilai_jalan"] = (
    df["skor_jalan"]
    * BOBOT_JALAN
)


# ============================================================
# 6. HITUNG INDEKS AKSESIBILITAS
# ============================================================

df["indeks_aksesibilitas"] = (
    df["nilai_damkar"]
    + df["nilai_rs"]
    + df["nilai_puskesmas"]
    + df["nilai_polisi"]
    + df["nilai_jalan"]
)


# ============================================================
# 7. BULATKAN
# ============================================================

df["indeks_aksesibilitas"] = (
    df["indeks_aksesibilitas"]
    .round(3)
)


# ============================================================
# 8. TAMPILKAN HASIL
# ============================================================

print("\n========================================")
print("HASIL INDEKS AKSESIBILITAS")
print("========================================")

print(
    df[
        [
            "NAME_3",
            "skor_damkar",
            "skor_rs",
            "skor_puskesmas",
            "skor_polisi",
            "skor_jalan",
            "indeks_aksesibilitas"
        ]
    ]
    .sort_values(
        "indeks_aksesibilitas",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# 9. STATISTIK INDEKS
# ============================================================

print("\n========================================")
print("STATISTIK INDEKS")
print("========================================")

print(
    "Minimum :",
    df["indeks_aksesibilitas"].min()
)

print(
    "Maximum :",
    df["indeks_aksesibilitas"].max()
)

print(
    "Mean    :",
    df["indeks_aksesibilitas"].mean()
)


# ============================================================
# 10. SIMPAN
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n========================================")
print("SELESAI")
print("========================================")

print(
    "Hasil disimpan ke:",
    OUTPUT_FILE
)