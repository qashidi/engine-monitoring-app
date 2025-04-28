# File: engine_monitoring_app/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

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

elif menu == "Input Data":
    st.subheader("📥 Input Data Mesin Manual")
    with st.form("Input Form"):
        tanggal = st.date_input("Tanggal")
        kapal = st.selectbox("Nama Kapal", ["Sebuku", "Legundi", "Jatra", "Portlink", "Batu Mandi"])
        nama_mesin = st.selectbox("Nama Mesin", ["Mesin 1", "Mesin 2"])
        bbm = st.number_input("Konsumsi BBM (L/h)", min_value=0.0)
        pelumas = st.number_input("Konsumsi Pelumas (L/h)", min_value=0.0)
        rpm = st.number_input("RPM", min_value=0)
        jam_kerja = st.number_input("Jam Kerja (jam)", min_value=0.0)
        suhu = st.number_input("Suhu Mesin (°C)", min_value=0.0)
        tekanan_oli = st.number_input("Tekanan Oli (bar)", min_value=0.0)
        beban = st.number_input("Beban Mesin (%)", min_value=0.0, max_value=150.0)
        vibrasi = st.number_input("Vibrasi (mm/s)", min_value=0.0)
        alarm = st.text_input("Alarm/Error (optional)")

        submitted = st.form_submit_button("Simpan Data")

        if submitted:
            new_row = pd.DataFrame({
                'Tanggal': [tanggal],
                'Kapal': [kapal],
                'Nama Mesin': [nama_mesin],
                'BBM (L/h)': [bbm],
                'Pelumas (L/h)': [pelumas],
                'RPM': [rpm],
                'Jam Kerja': [jam_kerja],
                'Suhu Mesin (°C)': [suhu],
                'Tekanan Oli (bar)': [tekanan_oli],
                'Beban Mesin (%)': [beban],
                'Vibrasi (mm/s)': [vibrasi],
                'Alarm/Error': [alarm]
            })
            data = pd.concat([data, new_row], ignore_index=True)
            save_data(data)
            st.success("Data berhasil disimpan!")

elif menu == "Upload Data":
    st.subheader("📤 Upload Data Mesin dari File Excel")
    uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df_upload = pd.read_excel(uploaded_file, parse_dates=['Tanggal'])
            required_columns = {'Tanggal', 'Kapal', 'Nama Mesin', 'BBM (L/h)', 'Pelumas (L/h)', 'RPM',
                                 'Jam Kerja', 'Suhu Mesin (°C)', 'Tekanan Oli (bar)', 'Beban Mesin (%)',
                                 'Vibrasi (mm/s)', 'Alarm/Error'}
            if required_columns.issubset(df_upload.columns):
                data = pd.concat([data, df_upload], ignore_index=True)
                save_data(data)
                st.success("Data berhasil di-upload dan disimpan!")
            else:
                st.error("Format kolom file tidak sesuai template!")
        except Exception as e:
            st.error(f"Error membaca file: {e}")

elif menu == "Dashboard":
    st.subheader("📊 Dashboard Monitoring")
    if data.empty:
        st.warning("Belum ada data mesin.")
    else:
        kapal_selected = st.selectbox("Pilih Kapal", data['Kapal'].unique())
        data_kapal = data[data['Kapal'] == kapal_selected]

        mesin_selected = st.selectbox("Pilih Mesin", data_kapal['Nama Mesin'].unique())
        data_filtered = data_kapal[data_kapal['Nama Mesin'] == mesin_selected]

        col1, col2 = st.columns(2)
        with col1:
            fig_bbm = px.line(data_filtered, x='Tanggal', y='BBM (L/h)', title="Konsumsi BBM Harian")
            st.plotly_chart(fig_bbm, use_container_width=True)

        with col2:
            fig_rpm = px.line(data_filtered, x='Tanggal', y='RPM', title="RPM Harian")
            st.plotly_chart(fig_rpm, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig_suhu = px.line(data_filtered, x='Tanggal', y='Suhu Mesin (°C)', title="Suhu Mesin Harian")
            st.plotly_chart(fig_suhu, use_container_width=True)

        with col4:
            fig_tekanan = px.line(data_filtered, x='Tanggal', y='Tekanan Oli (bar)', title="Tekanan Oli Harian")
            st.plotly_chart(fig_tekanan, use_container_width=True)

        st.dataframe(data_filtered.sort_values('Tanggal', ascending=False), use_container_width=True)

        with st.spinner('Mempersiapkan file laporan...'):
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            laporan_path = os.path.join(OUTPUT_FOLDER, f'laporan_{kapal_selected}_{mesin_selected}.xlsx')
            data_filtered.to_excel(laporan_path, index=False)
            with open(laporan_path, 'rb') as f:
                st.download_button("📥 Download Laporan", f, file_name=f"laporan_{kapal_selected}_{mesin_selected}.xlsx")

# --- FOOTER ---
st.markdown("""
    <hr style='margin-top: 50px;'>
    <p style='text-align: center; font-size: small;'>Created by Qashidi | Powered by Streamlit 🚀</p>
""", unsafe_allow_html=True)
