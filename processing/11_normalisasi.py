import pandas as pd
import geopandas as gpd
import numpy as np

# ============================================================
# 1. PATH
# ============================================================

INPUT_CSV = "output/hasil_shortest_path_fixed.csv"

OUTPUT_CSV = "output/hasil_skor_aksesibilitas.csv"


# ============================================================
# 2. BACA DATA
# ============================================================

print("\n========================================")
print("MEMBACA DATA JARAK")
print("========================================")

df = pd.read_csv(INPUT_CSV)

print("\nJumlah kecamatan:", len(df))

print("\nData awal:")
print(df.to_string(index=False))


# ============================================================
# 3. DAFTAR INDIKATOR JARAK
# ============================================================

indikator_jarak = {
    "jarak_damkar_km": "skor_damkar",
    "jarak_rs_km": "skor_rs",
    "jarak_puskesmas_km": "skor_puskesmas",
    "jarak_polisi_km": "skor_polisi"
}


# ============================================================
# 4. FUNGSI NORMALISASI JARAK
# ============================================================

def normalisasi_jarak(series):

    xmin = series.min()
    xmax = series.max()

    if xmax == xmin:
        return pd.Series(
            [2] * len(series),
            index=series.index
        )

    skor = 1 + 2 * (
        (xmax - series) /
        (xmax - xmin)
    )

    return skor


# ============================================================
# 5. HITUNG SKOR SETIAP FASILITAS
# ============================================================

print("\n========================================")
print("NORMALISASI JARAK")
print("========================================")

for kolom, kolom_skor in indikator_jarak.items():

    print(f"\nIndikator: {kolom}")

    print("Minimum:", df[kolom].min())
    print("Maximum:", df[kolom].max())

    df[kolom_skor] = normalisasi_jarak(
        df[kolom]
    )

    print(
        df[
            ["NAME_3", kolom, kolom_skor]
        ].to_string(index=False)
    )


# ============================================================
# 6. BULATKAN SKOR
# ============================================================

kolom_skor = [
    "skor_damkar",
    "skor_rs",
    "skor_puskesmas",
    "skor_polisi"
]

df[kolom_skor] = df[kolom_skor].round(3)


# ============================================================
# 7. SIMPAN HASIL
# ============================================================

df.to_csv(
    OUTPUT_CSV,
    index=False
)


# ============================================================
# 8. TAMPILKAN HASIL AKHIR
# ============================================================

print("\n========================================")
print("HASIL NORMALISASI")
print("========================================")

print(
    df[
        [
            "NAME_3",
            "jarak_damkar_km",
            "skor_damkar",
            "jarak_rs_km",
            "skor_rs",
            "jarak_puskesmas_km",
            "skor_puskesmas",
            "jarak_polisi_km",
            "skor_polisi"
        ]
    ].to_string(index=False)
)

print("\n========================================")
print("SELESAI")
print("========================================")

print(
    f"Hasil disimpan ke: {OUTPUT_CSV}"
)