import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from data_processing import load_and_preprocess_data, get_province_stats, get_quantiles

plt.style.use('seaborn-v0_8-darkgrid')

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Rekomendasi Kebutuhan Pendidikan Daerah", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f5;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        color: #2F80ED;
        text-align: center;
        font-size: 2.2em;
        margin-bottom: 20px;
    }
    h2, h3 {
        color: #4A90E2;
    }
    .stSelectbox, .stButton > button {
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background-color: #2F80ED;
        color: white;
        padding: 12px 25px;
        font-size: 18px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #1A6DD5;
        transform: translateY(-2px);
    }
    .stAlert {
        border-radius: 8px;
        font-size: 1.1em;
    }
    .stMarkdown {
        line-height: 1.6;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow-x: auto;
    }
    .sidebar .stSidebar {
        background-color: #e6f7ff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Sistem Rekomendasi Kebutuhan Pendidikan Daerah Jawa Timur")

st.markdown("""
Sistem ini dirancang untuk memberikan gambaran cepat mengenai kondisi dan kebutuhan pendidikan di setiap Kabupaten/Kota di Jawa Timur. Anda dapat memilih wilayah tertentu untuk melihat profil detail terkait ketersediaan guru, fasilitas sekolah, dan kepadatan murid.

---
""")


# Load data dengan cache
@st.cache_data
def cached_load(file_path="data jatim 2022 pendidikan.xlsx"):
    try:
        return load_and_preprocess_data(file_path)
    except FileNotFoundError:
        st.error(f"Maaf, file data '{file_path}' tidak ditemukan. Pastikan file Excel berada di folder yang sama dengan aplikasi ini.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi masalah saat memuat atau memproses data: {e}. Mohon hubungi administrator.")
        st.stop()


df_data = cached_load()

# Dropdown pemilihan wilayah
st.header("🔍 Pilih Kabupaten/Kota untuk Melihat Profil Kebutuhan")

kabupaten_kota_list = sorted(df_data['kabupaten_kota'].unique().tolist())
selected_kabupaten_kota = st.selectbox(
    "Pilih Kabupaten/Kota:",
    kabupaten_kota_list
)

if st.button("Lihat Profil Kebutuhan"):
    if selected_kabupaten_kota:
        selected_row = df_data[df_data['kabupaten_kota'] == selected_kabupaten_kota].iloc[0]

        st.write("---")
        st.header(f"Profil Kebutuhan Pendidikan di {selected_kabupaten_kota}")

        # Tabel ringkasan
        st.subheader("Data Umum Pendidikan:")
        summary_data = {
            "Indikator": [
                "Jumlah SD", "Jumlah SMP",
                "Jumlah Murid SD", "Jumlah Murid SMP",
                "Jumlah Guru SD", "Jumlah Guru SMP",
                "Kepadatan Penduduk (jiwa/km²)", "Luas Wilayah (km²)"
            ],
            f"Nilai di {selected_kabupaten_kota}": [
                f"{selected_row['jumlah_sd']:,}",
                f"{selected_row['jumlah_smp']:,}",
                f"{selected_row['jumlah_murid_sd']:,}",
                f"{selected_row['jumlah_murid_smp']:,}",
                f"{selected_row['jumlah_guru_sd']:,}",
                f"{selected_row['jumlah_guru_smp']:,}",
                f"{selected_row['kepadatan_penduduk']:,}",
                f"{selected_row['luas_wilayah']:.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(summary_data).set_index("Indikator"))
        st.markdown("---")

        st.subheader("Analisis Kebutuhan & Saran Aksi:")

        # Statistik provinsi untuk perbandingan
        stats = get_province_stats(df_data)

        # Guru SD
        st.markdown("#### **Ketersediaan Guru SD**")
        ratio_sd_guru = selected_row['rasio_murid_sd_per_guru_sd']
        if pd.notna(ratio_sd_guru):
            q = get_quantiles(df_data, 'rasio_murid_sd_per_guru_sd')
            st.write(f"- Rasio Murid SD per Guru SD di {selected_kabupaten_kota}: **{ratio_sd_guru:.2f}**")
            st.write(f"  (Rata-rata di Provinsi Jawa Timur: {q['mean']:.2f})")
            if ratio_sd_guru > q['p75']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat tinggi**, jauh di atas rata-rata provinsi. Ini mengindikasikan **kekurangan guru SD yang signifikan** atau **kelas yang terlalu padat**.")
                st.markdown("  * **Saran Aksi:** Prioritaskan **penambahan tenaga guru SD** atau program **pemerataan penempatan guru** dari wilayah surplus.")
            elif ratio_sd_guru < q['p25']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat rendah**, di bawah rata-rata provinsi. Kondisi guru SD di sini **cukup ideal** atau melebihi kebutuhan.")
                st.markdown("  * **Saran Aksi:** Pertahankan kondisi. Jika ada surplus guru, pertimbangkan program mutasi ke wilayah yang lebih membutuhkan.")
            else:
                st.markdown("  * **Kesimpulan:** Rasio ini **normal**, relatif seimbang dengan kondisi provinsi.")
                st.markdown("  * **Saran Aksi:** Monitor kondisi secara berkala. Fokuskan sumber daya pada area lain yang lebih kritis.")
        else:
            st.write("- Rasio Murid SD per Guru SD: **Data tidak tersedia** (kemungkinan jumlah guru SD adalah 0).")
            st.markdown("  * **Kesimpulan:** Situasi ini **sangat kritis**. Perlu **verifikasi data segera**.")
            st.markdown("  * **Saran Aksi:** Ini adalah **prioritas sangat tinggi** untuk alokasi guru SD. Lakukan investigasi mengapa data guru kosong.")

        # Guru SMP
        st.markdown("#### **Ketersediaan Guru SMP**")
        ratio_smp_guru = selected_row['rasio_murid_smp_per_guru_smp']
        if pd.notna(ratio_smp_guru):
            q = get_quantiles(df_data, 'rasio_murid_smp_per_guru_smp')
            st.write(f"- Rasio Murid SMP per Guru SMP di {selected_kabupaten_kota}: **{ratio_smp_guru:.2f}**")
            st.write(f"  (Rata-rata di Provinsi Jawa Timur: {q['mean']:.2f})")
            if ratio_smp_guru > q['p75']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat tinggi**, mengindikasikan **kekurangan guru SMP yang signifikan** atau **kelas yang terlalu padat**.")
                st.markdown("  * **Saran Aksi:** Prioritaskan **penambahan tenaga guru SMP** atau program **pemerataan penempatan guru**.")
            elif ratio_smp_guru < q['p25']:
                 st.markdown("  * **Kesimpulan:** Rasio ini **sangat rendah**, kondisi guru SMP di sini **cukup ideal**.")
                 st.markdown("  * **Saran Aksi:** Pertahankan kondisi. Jika ada surplus guru, pertimbangkan mutasi ke wilayah yang lebih membutuhkan.")
            else:
                st.markdown("  * **Kesimpulan:** Rasio ini **normal**, relatif seimbang dengan kondisi provinsi.")
                st.markdown("  * **Saran Aksi:** Monitor kondisi secara berkala. Fokuskan sumber daya pada area lain yang lebih kritis.")
        else:
            st.write("- Rasio Murid SMP per Guru SMP: **Data tidak tersedia** (kemungkinan jumlah guru SMP adalah 0).")
            st.markdown("  * **Kesimpulan:** Situasi ini **sangat kritis**. Perlu **verifikasi data segera**.")
            st.markdown("  * **Saran Aksi:** Ini adalah **prioritas sangat tinggi** untuk alokasi guru SMP. Lakukan investigasi mengapa data guru kosong.")

        # Fasilitas SD
        st.markdown("#### **Ketersediaan Fasilitas Sekolah SD**")
        ratio_sd_sekolah = selected_row['rasio_murid_sd_per_sekolah_sd']
        if pd.notna(ratio_sd_sekolah):
            q = get_quantiles(df_data, 'rasio_murid_sd_per_sekolah_sd')
            st.write(f"- Rasio Murid SD per Sekolah SD di {selected_kabupaten_kota}: **{ratio_sd_sekolah:.2f}**")
            st.write(f"  (Rata-rata di Provinsi Jawa Timur: {q['mean']:.2f})")
            if ratio_sd_sekolah > q['p75']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat tinggi**, mengindikasikan **sekolah SD yang sangat padat** atau **kekurangan fasilitas sekolah SD**.")
                st.markdown("  * **Saran Aksi:** Prioritaskan **pembangunan sekolah SD baru** atau **perluasan/penambahan ruang kelas** pada sekolah yang ada.")
            elif ratio_sd_sekolah < q['p25']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat rendah**, kapasitas sekolah SD di sini **cukup memadai**.")
                st.markdown("  * **Saran Aksi:** Pertahankan kondisi atau alihkan fokus sumber daya ke wilayah lain yang lebih membutuhkan.")
            else:
                st.markdown("  * **Kesimpulan:** Rasio ini **normal**, relatif seimbang dengan kondisi provinsi.")
                st.markdown("  * **Saran Aksi:** Monitor kondisi secara berkala. Fokuskan sumber daya pada area lain yang lebih kritis.")
        else:
            st.write("- Rasio Murid SD per Sekolah SD: **Data tidak tersedia** (kemungkinan jumlah SD adalah 0).")
            st.markdown("  * **Kesimpulan:** Situasi ini **sangat kritis**. Perlu **verifikasi data segera**.")
            st.markdown("  * **Saran Aksi:** Ini adalah **prioritas sangat tinggi** untuk pembangunan fasilitas sekolah SD. Lakukan investigasi mengapa data sekolah kosong.")

        # Fasilitas SMP
        st.markdown("#### **Ketersediaan Fasilitas Sekolah SMP**")
        ratio_smp_sekolah = selected_row['rasio_murid_smp_per_sekolah_smp']
        if pd.notna(ratio_smp_sekolah):
            q = get_quantiles(df_data, 'rasio_murid_smp_per_sekolah_smp')
            st.write(f"- Rasio Murid SMP per Sekolah SMP di {selected_kabupaten_kota}: **{ratio_smp_sekolah:.2f}**")
            st.write(f"  (Rata-rata di Provinsi Jawa Timur: {q['mean']:.2f})")
            if ratio_smp_sekolah > q['p75']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat tinggi**, mengindikasikan **sekolah SMP yang sangat padat** atau **kekurangan fasilitas sekolah SMP**.")
                st.markdown("  * **Saran Aksi:** Prioritaskan **pembangunan sekolah SMP baru** atau **perluasan/penambahan ruang kelas** pada sekolah yang ada.")
            elif ratio_smp_sekolah < q['p25']:
                st.markdown("  * **Kesimpulan:** Rasio ini **sangat rendah**, kapasitas sekolah SMP di sini **cukup memadai**.")
                st.markdown("  * **Saran Aksi:** Pertahankan kondisi atau alihkan fokus sumber daya ke wilayah lain yang lebih membutuhkan.")
            else:
                st.markdown("  * **Kesimpulan:** Rasio ini **normal**, relatif seimbang dengan kondisi provinsi.")
                st.markdown("  * **Saran Aksi:** Monitor kondisi secara berkala. Fokuskan sumber daya pada area lain yang lebih kritis.")
        else:
            st.write("- Rasio Murid SMP per Sekolah SMP: **Data tidak tersedia** (kemungkinan jumlah SMP adalah 0).")
            st.markdown("  * **Kesimpulan:** Situasi ini **sangat kritis**. Perlu **verifikasi data segera**.")
            st.markdown("  * **Saran Aksi:** Ini adalah **prioritas sangat tinggi** untuk pembangunan fasilitas sekolah SMP. Lakukan investigasi mengapa data sekolah kosong.")

        # Kepadatan penduduk
        st.markdown("#### **Kepadatan Penduduk**")
        kepadatan = selected_row['kepadatan_penduduk']
        q = get_quantiles(df_data, 'kepadatan_penduduk')
        st.write(f"- Kepadatan Penduduk: **{kepadatan:,.0f} jiwa/km²**")
        st.write(f"  (Rata-rata di Provinsi Jawa Timur: {q['mean']:,.0f} jiwa/km²)")
        if kepadatan > q['p75']:
            st.markdown("  * **Kesimpulan:** Kepadatan penduduk **sangat tinggi**, berpotensi menciptakan tekanan demografi besar pada fasilitas pendidikan.")
            st.markdown("  * **Saran Aksi:** Perencanaan pendidikan jangka panjang harus mempertimbangkan **pertumbuhan populasi** dan **penyediaan layanan pendidikan yang memadai** untuk masa depan, termasuk pemetaan zona sekolah.")
        elif kepadatan < q['p25']:
            st.markdown("  * **Kesimpulan:** Kepadatan penduduk **rendah**, tekanan demografi pada fasilitas pendidikan tidak terlalu tinggi.")
            st.markdown("  * **Saran Aksi:** Pertahankan kondisi. Fokuskan pada kualitas pendidikan yang sudah ada.")
        else:
            st.markdown("  * **Kesimpulan:** Kepadatan penduduk **normal**, relatif seimbang dengan kondisi provinsi.")
            st.markdown("  * **Saran Aksi:** Monitor pertumbuhan penduduk dan kebutuhan pendidikan di masa depan.")

        st.markdown("---")

        # Visualisasi perbandingan wilayah vs rata-rata provinsi
        st.subheader(f"Perbandingan Kesenjangan di {selected_kabupaten_kota} vs. Rata-rata Provinsi")

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        labels_guru = ['Murid SD/Guru SD', 'Murid SMP/Guru SMP']
        values_guru_kab = [selected_row['rasio_murid_sd_per_guru_sd'], selected_row['rasio_murid_smp_per_guru_smp']]
        avg_values_guru_prov = [stats.loc['mean', 'rasio_murid_sd_per_guru_sd'], stats.loc['mean', 'rasio_murid_smp_per_guru_smp']]

        labels_sekolah = ['Murid SD/Sekolah SD', 'Murid SMP/Sekolah SMP']
        values_sekolah_kab = [selected_row['rasio_murid_sd_per_sekolah_sd'], selected_row['rasio_murid_smp_per_sekolah_smp']]
        avg_values_sekolah_prov = [stats.loc['mean', 'rasio_murid_sd_per_sekolah_sd'], stats.loc['mean', 'rasio_murid_smp_per_sekolah_smp']]

        bar_width = 0.35
        index_guru = np.arange(len(labels_guru))
        index_sekolah = np.arange(len(labels_sekolah))

        # Bar chart rasio guru
        axes[0].bar(index_guru - bar_width/2, values_guru_kab, bar_width, label=selected_kabupaten_kota, color='#4E6688')
        axes[0].bar(index_guru + bar_width/2, avg_values_guru_prov, bar_width, label='Rata-rata Provinsi', color='#71C0BB', alpha=0.7)
        axes[0].set_xlabel("Jenis Rasio Guru")
        axes[0].set_ylabel("Rasio (Murid/Guru)")
        axes[0].set_title(f"Rasio Murid per Guru")
        axes[0].set_xticks(index_guru)
        axes[0].set_xticklabels(labels_guru, rotation=0)
        axes[0].legend()
        max_y_guru = max(filter(np.isfinite, values_guru_kab + avg_values_guru_prov), default=1)
        axes[0].set_ylim(0, max_y_guru * 1.2 if max_y_guru > 0 else 10)

        # Bar chart rasio sekolah
        axes[1].bar(index_sekolah - bar_width/2, values_sekolah_kab, bar_width, label=selected_kabupaten_kota, color='#5459AC')
        axes[1].bar(index_sekolah + bar_width/2, avg_values_sekolah_prov, bar_width, label='Rata-rata Provinsi', color='#648DB3', alpha=0.7)
        axes[1].set_xlabel("Jenis Rasio Sekolah")
        axes[1].set_ylabel("Rasio (Murid/Sekolah)")
        axes[1].set_title(f"Rasio Murid per Sekolah")
        axes[1].set_xticks(index_sekolah)
        axes[1].set_xticklabels(labels_sekolah, rotation=0)
        axes[1].legend()
        max_y_sekolah = max(filter(np.isfinite, values_sekolah_kab + avg_values_sekolah_prov), default=1)
        axes[1].set_ylim(0, max_y_sekolah * 1.2 if max_y_sekolah > 0 else 800)

        st.pyplot(fig)
        st.markdown("---")

    else:
        st.warning("Mohon pilih Kabupaten/Kota terlebih dahulu.")

# Sidebar info
st.sidebar.header("Tentang Aplikasi & Sumber Data")
st.sidebar.markdown("""
Aplikasi ini dikembangkan untuk membantu analisis cepat kebutuhan pendidikan di daerah.
Ini menggunakan data pendidikan dan demografi **Kabupaten/Kota Jawa Timur tahun 2022**.

**Sumber Data:** BPS Jawa Timur

**Cara Menjalankan Aplikasi Ini:**
1.  Pastikan Anda memiliki file `data jatim 2022 pendidikan.xlsx` di folder yang sama.
2.  Buka Terminal/Command Prompt di folder tersebut.
3.  Jalankan perintah: `python -m streamlit run app.py`
""")
st.sidebar.info("Aplikasi ini cocok untuk **pengambilan keputusan awal** dan **pemetaan kebutuhan**, bukan sebagai alat rekomendasi yang kompleks.")