import pandas as pd
import numpy as np


def load_and_preprocess_data(file_path="data jatim 2022 pendidikan.xlsx"):
    df = pd.read_excel(file_path)

    # Normalisasi nama kolom
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('/', '_')
    df = df.rename(columns={'kabupaten_kota': 'kabupaten_kota'})

    # Konversi luas wilayah jika berformat string
    df['luas_wilayah'] = df['luas_wilayah'].apply(
        lambda x: float(str(x).replace(',', '.')) if pd.notna(x) and isinstance(x, str) else x
    )

    # Hitung rasio kesenjangan
    df['rasio_murid_sd_per_guru_sd'] = df.apply(
        lambda row: row['jumlah_murid_sd'] / row['jumlah_guru_sd'] if row['jumlah_guru_sd'] > 0 else np.nan, axis=1
    )
    df['rasio_murid_smp_per_guru_smp'] = df.apply(
        lambda row: row['jumlah_murid_smp'] / row['jumlah_guru_smp'] if row['jumlah_guru_smp'] > 0 else np.nan, axis=1
    )
    df['rasio_murid_sd_per_sekolah_sd'] = df.apply(
        lambda row: row['jumlah_murid_sd'] / row['jumlah_sd'] if row['jumlah_sd'] > 0 else np.nan, axis=1
    )
    df['rasio_murid_smp_per_sekolah_smp'] = df.apply(
        lambda row: row['jumlah_murid_smp'] / row['jumlah_smp'] if row['jumlah_smp'] > 0 else np.nan, axis=1
    )

    return df


def get_province_stats(df):
    cols = [
        'rasio_murid_sd_per_guru_sd',
        'rasio_murid_smp_per_guru_smp',
        'rasio_murid_sd_per_sekolah_sd',
        'rasio_murid_smp_per_sekolah_smp',
        'kepadatan_penduduk'
    ]
    return df[cols].describe()


def get_quantiles(df, col):
    return {
        'p25': df[col].quantile(0.25),
        'p75': df[col].quantile(0.75),
        'mean': df[col].mean()
    }