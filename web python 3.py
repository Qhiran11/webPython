import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Smart IoT Dashboard",
    page_icon="⚡",
    layout="wide"
)

# --- CSS AGAR TAMPILAN LEBIH BERSIH ---
st.markdown("""
<style>
    .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

# --- FUNGSI LOAD DATA ---
def get_data():
    # GANTI LINK CSV ANDA DI SINI
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSiOyd7cKc7lXbJlYl7A7JIaOHlhDyhVQghGjNGbbHZxI9TTi7pnwr7edIeXdrrhp60vBcky5BZ3Ojq/pub?gid=0&single=true&output=csv"
    
    try:
        # Tambahkan parameter on_bad_lines agar tidak error jika ada data korup
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
        df['Waktu'] = pd.to_datetime(df['Waktu'])
        df = df.sort_values(by='Waktu')
        return df
    except Exception as e:
        return None

# --- STATE MANAGEMENT (INGATAN PYTHON) ---
# Kita butuh variabel untuk menyimpan waktu data terakhir
if 'last_check_time' not in st.session_state:
    st.session_state['last_check_time'] = None

# --- LAYOUT UTAMA ---
st.title("⚡ Real-time Smart Dashboard")
st.caption("Dashboard hanya akan refresh visual jika ada data baru masuk.")

# Buat wadah kosong (Placeholder) yang akan kita isi ulang terus menerus
dashboard_placeholder = st.empty()

# --- LOOPING UTAMA (PENGGANTI AUTO REFRESH BIASA) ---
while True:
    # 1. Ambil data diam-diam
    df = get_data()
    
    if df is not None and not df.empty:
        # Ambil waktu dari data paling baru (baris terakhir)
        latest_data_time = df.iloc[-1]['Waktu']
        
        # 2. LOGIKA CEK PERUBAHAN
        # Jika waktu data terbaru BEDA dengan yang kita ingat -> Update Tampilan
        if latest_data_time != st.session_state['last_check_time']:
            
            # Update ingatan kita
            st.session_state['last_check_time'] = latest_data_time
            
            # --- RENDER TAMPILAN DI DALAM PLACEHOLDER ---
            with dashboard_placeholder.container():
                latest_data = df.iloc[-1]
                
                # --- STATUS UPDATE ---
                st.success(f"Data Baru Diterima! Update terakhir: {latest_data_time.strftime('%H:%M:%S')}")

                # --- METRICS ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🌡️ Suhu", f"{latest_data['suhu rumah']} °C")
                
                delta_hujan = "Basah" if latest_data['Rain Module'] < 500 else "Kering"
                col2.metric("🌧️ Hujan", latest_data['Rain Module'], delta=delta_hujan)
                
                col3.metric("💡 Cahaya", latest_data['LDR'])
                col4.metric("🆔 RFID", latest_data['RFID'])
                
                st.markdown("---")

                # --- GRAFIK ---
                c_kiri, c_kanan = st.columns(2)
                
                with c_kiri:
                    fig_temp = px.line(df.tail(20), x='Waktu', y='suhu rumah', title='20 Data Terakhir: Suhu', markers=True)
                    st.plotly_chart(fig_temp, use_container_width=True)
                
                with c_kanan:
                    fig_ldr = px.area(df.tail(20), x='Waktu', y='LDR', title='20 Data Terakhir: Cahaya', color_discrete_sequence=['gold'])
                    st.plotly_chart(fig_ldr, use_container_width=True)

        else:
            # JIKA DATA SAMA (Tidak ada perubahan)
            # Kita tidak melakukan update visual apa-apa
            # Tapi kita bisa kasih indikator kecil (opsional)
            pass 
            
    # 3. JEDA PENGECEKAN
    # Tunggu 3 detik sebelum mengecek ke Google Sheet lagi
    # Ini penting agar tidak terkena limit Google (Error 429)
    time.sleep(3)