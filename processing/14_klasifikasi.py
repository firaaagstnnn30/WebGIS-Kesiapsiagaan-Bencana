import pandas as pd


# ============================================================
# 1. PATH
# ============================================================

INPUT_FILE = "output/indeks_aksesibilitas.csv"

OUTPUT_FILE = "output/indeks_aksesibilitas_klasifikasi.csv"


# ============================================================
# 2. BACA DATA
# ============================================================

print("\n========================================")
print("MEMBACA INDEKS AKSESIBILITAS")
print("========================================")

df = pd.read_csv(INPUT_FILE)


# ============================================================
# 3. CARI NILAI MINIMUM DAN MAKSIMUM
# ============================================================

xmin = df["indeks_aksesibilitas"].min()
xmax = df["indeks_aksesibilitas"].max()


# ============================================================
# 4. HITUNG INTERVAL KELAS
# ============================================================

jumlah_kelas = 3

interval = (xmax - xmin) / jumlah_kelas


batas_1 = xmin + interval
batas_2 = xmin + (2 * interval)


# ============================================================
# 5. TAMPILKAN BATAS KELAS
# ============================================================

print("\n========================================")
print("BATAS KLASIFIKASI")
print("========================================")

print("Minimum :", round(xmin, 3))
print("Maximum :", round(xmax, 3))
print("Interval:", round(interval, 3))

print("\nRendah  :", round(xmin, 3), "-", round(batas_1, 3))
print("Sedang  :", round(batas_1, 3), "-", round(batas_2, 3))
print("Tinggi  :", round(batas_2, 3), "-", round(xmax, 3))


# ============================================================
# 6. KLASIFIKASI
# ============================================================

def klasifikasi(nilai):

    if nilai <= batas_1:
        return "Rendah"

    elif nilai <= batas_2:
        return "Sedang"

    else:
        return "Tinggi"


df["kelas_aksesibilitas"] = (
    df["indeks_aksesibilitas"]
    .apply(klasifikasi)
)


# ============================================================
# 7. URUTKAN
# ============================================================

df = df.sort_values(
    "indeks_aksesibilitas",
    ascending=False
)


# ============================================================
# 8. TAMPILKAN HASIL
# ============================================================

print("\n========================================")
print("HASIL KLASIFIKASI")
print("========================================")

print(
    df[
        [
            "NAME_3",
            "indeks_aksesibilitas",
            "kelas_aksesibilitas"
        ]
    ].to_string(index=False)
)


# ============================================================
# 9. JUMLAH KECAMATAN PER KELAS
# ============================================================

print("\n========================================")
print("JUMLAH KECAMATAN PER KELAS")
print("========================================")

print(
    df["kelas_aksesibilitas"]
    .value_counts()
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