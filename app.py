# File: engine_monitoring_app/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# --- CONFIGURABLE ---
DATA_FILE = 'data/mesin_log.csv'
OUTPUT_FOLDER = 'output'

# --- FUNCTION: Load or Initialize Data ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=['Tanggal'])
    else:
        return pd.DataFrame(columns=[
            'Tanggal', 'Kapal', 'Nama Mesin', 'BBM (L/h)', 'Pelumas (L/h)', 'RPM', 'Jam Kerja',
            'Suhu Mesin (°C)', 'Tekanan Oli (bar)', 'Beban Mesin (%)', 'Vibrasi (mm/s)', 'Alarm/Error'
        ])

# --- FUNCTION: Save Data ---
def save_data(df: pd.DataFrame):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, index=False)

# --- FUNCTION: Generate Dummy Data ---
def generate_dummy_data():
    kapal_list = ["Sebuku", "Legundi", "Jatra", "Portlink", "Batu Mandi"]
    mesin_list = ["Mesin 1", "Mesin 2"]
    tanggal_range = pd.date_range(start="2024-04-01", periods=14)

    data_simulasi = []
    np.random.seed(42)

    for kapal in kapal_list:
        for mesin in mesin_list:
            for tanggal in tanggal_range:
                bbm = np.random.uniform(200, 500)
                pelumas = np.random.uniform(5, 15)
                rpm = np.random.randint(1400, 1600)
                jam_kerja = np.random.uniform(3, 20)
                suhu = np.random.uniform(70, 105)
                tekanan_oli = np.random.uniform(2.5, 5)
                beban = np.random.uniform(60, 95)
                vibrasi = np.random.uniform(0.5, 2.0)
                alarm = "-" if suhu < 100 and tekanan_oli > 3 else "Warning"

                data_simulasi.append([
                    tanggal, kapal, mesin, bbm, pelumas, rpm, jam_kerja,
                    suhu, tekanan_oli, beban, vibrasi, alarm
                ])

    columns = [
        'Tanggal', 'Kapal', 'Nama Mesin', 'BBM (L/h)', 'Pelumas (L/h)', 'RPM',
        'Jam Kerja', 'Suhu Mesin (°C)', 'Tekanan Oli (bar)', 'Beban Mesin (%)',
        'Vibrasi (mm/s)', 'Alarm/Error'
    ]
    return pd.DataFrame(data_simulasi, columns=columns)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Monitoring Performa Mesin Kapal", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>🚢 Monitoring Performa Mesin Kapal ⚙️📈</h1>
    <p style='text-align: center;'>Aplikasi untuk memantau konsumsi BBM, pelumas, RPM, jam kerja, suhu mesin, tekanan oli, dan performa mesin kapal secara realtime.</p>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Menu", ("Home", "Input Data", "Upload Data", "Dashboard"))
data = load_data()

if menu == "Home":
    st.subheader("🏠 Selamat Datang di Aplikasi Monitoring")
    st.write("Dengan aplikasi ini, Anda dapat memantau performa mesin kapal secara efektif dan efisien.\n")
    st.markdown("""
    **Fitur-fitur utama:**
    - 📥 Input data harian mesin secara manual
    - 📤 Upload data performa mesin dari file Excel
    - 📊 Visualisasi trend konsumsi BBM, RPM, Suhu, Tekanan Oli
    - 📈 Download laporan performa mesin per kapal dan mesin
    - 🚨 Peringatan otomatis untuk kondisi mesin abnormal
    """)
    st.success("Silakan pilih menu di sidebar untuk mulai menggunakan aplikasi.")

    if st.button("🛠️ Generate Dummy Data untuk Testing"):
        dummy_data = generate_dummy_data()
        data = pd.concat([data, dummy_data], ignore_index=True)
        save_data(data)
        st.success("Data dummy berhasil dibuat dan disimpan!")

elif menu == "Dashboard":
    st.subheader("📊 Dashboard Monitoring")
    if data.empty:
        st.warning("Belum ada data mesin.")
    else:
        mesin_selected = st.selectbox("Pilih Mesin", data['Nama Mesin'].unique())
        kapal_options = data['Kapal'].unique().tolist()
        kapal_selected = st.multiselect("Pilih Kapal (bisa pilih lebih dari satu)", kapal_options, default=kapal_options)

        data_filtered = data[(data['Nama Mesin'] == mesin_selected) & (data['Kapal'].isin(kapal_selected))]

        col1, col2 = st.columns(2)
        with col1:
            fig_bbm = px.line(data_filtered, x='Tanggal', y='BBM (L/h)', color='Kapal', title="Konsumsi BBM Harian per Kapal")
            st.plotly_chart(fig_bbm, use_container_width=True)

        with col2:
            fig_rpm = px.line(data_filtered, x='Tanggal', y='RPM', color='Kapal', title="RPM Harian per Kapal")
            st.plotly_chart(fig_rpm, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig_suhu = px.line(data_filtered, x='Tanggal', y='Suhu Mesin (°C)', color='Kapal', title="Suhu Mesin Harian per Kapal")
            st.plotly_chart(fig_suhu, use_container_width=True)

        with col4:
            fig_tekanan = px.line(data_filtered, x='Tanggal', y='Tekanan Oli (bar)', color='Kapal', title="Tekanan Oli Harian per Kapal")
            st.plotly_chart(fig_tekanan, use_container_width=True)

        st.dataframe(data_filtered.sort_values('Tanggal', ascending=False), use_container_width=True)

        with st.spinner('Mempersiapkan file laporan...'):
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            laporan_path = os.path.join(OUTPUT_FOLDER, f'laporan_summary_{mesin_selected}.xlsx')
            data_filtered.to_excel(laporan_path, index=False)
            with open(laporan_path, 'rb') as f:
                st.download_button("📥 Download Laporan", f, file_name=f"laporan_summary_{mesin_selected}.xlsx")

# --- FOOTER ---
st.markdown("""
    <hr style='margin-top: 50px;'>
    <p style='text-align: center; font-size: small;'>Created by Qashidi | Powered by Streamlit 🚀</p>
""", unsafe_allow_html=True)
