import geopandas as gpd
import pandas as pd


# ============================================================
# 1. PATH
# ============================================================

ADMIN_FILE = "data/administrasi.geojson"

HASIL_FILE = "output/indeks_aksesibilitas_klasifikasi.csv"

OUTPUT_FILE = "output/kecamatan_aksesibilitas.geojson"


# ============================================================
# 2. BACA DATA
# ============================================================

print("\n========================================")
print("MEMBACA DATA")
print("========================================")

admin = gpd.read_file(ADMIN_FILE)

hasil = pd.read_csv(HASIL_FILE)

print("Jumlah polygon kecamatan :", len(admin))
print("Jumlah hasil analisis    :", len(hasil))


# ============================================================
# 3. CEK GID_3
# ============================================================

print("\n========================================")
print("CEK ID KECAMATAN")
print("========================================")

print("GID admin:")
print(admin["GID_3"].tolist())

print("\nGID hasil:")
print(hasil["GID_3"].tolist())


# ============================================================
# 4. JOIN BERDASARKAN GID_3
# ============================================================

admin_hasil = admin.merge(
    hasil,
    on="GID_3",
    how="left"
)


# ============================================================
# 5. CEK HASIL JOIN
# ============================================================

print("\n========================================")
print("HASIL JOIN")
print("========================================")

print(
    admin_hasil[
        [
            "NAME_3_x",
            "NAME_3_y",
            "indeks_aksesibilitas",
            "kelas_aksesibilitas"
        ]
    ].to_string(index=False)
)


# ============================================================
# 6. CEK DATA YANG TIDAK TERGABUNG
# ============================================================

jumlah_kosong = (
    admin_hasil["indeks_aksesibilitas"]
    .isna()
    .sum()
)

print("\nJumlah kecamatan tanpa indeks:", jumlah_kosong)


# ============================================================
# 7. HAPUS KOLOM NAME DUPLIKAT
# ============================================================

if "NAME_3_y" in admin_hasil.columns:

    admin_hasil = admin_hasil.drop(
        columns=["NAME_3_y"]
    )

    admin_hasil = admin_hasil.rename(
        columns={
            "NAME_3_x": "NAME_3"
        }
    )


# ============================================================
# 8. SIMPAN GEOJSON
# ============================================================

admin_hasil.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)


# ============================================================
# 9. HASIL AKHIR
# ============================================================

print("\n========================================")
print("SELESAI")
print("========================================")

print(
    "GeoJSON disimpan ke:"
)

print(OUTPUT_FILE)

print(
    "\nJumlah polygon:",
    len(admin_hasil)
)

print(
    "Jumlah polygon dengan indeks:",
    admin_hasil[
        "indeks_aksesibilitas"
    ].notna().sum()
)