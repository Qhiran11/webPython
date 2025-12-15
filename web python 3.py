import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh # <-- Import baru

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="IoT Monitoring Dashboard",
    page_icon="🤖",
    layout="wide"
)

# --- FUNGSI LOAD DATA ---
def get_data():
    # GANTI LINK INI DENGAN LINK CSV ANDA DARI LANGKAH 1
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSiOyd7cKc7lXbJlYl7A7JIaOHlhDyhVQghGjNGbbHZxI9TTi7pnwr7edIeXdrrhp60vBcky5BZ3Ojq/pub?gid=0&single=true&output=csv"
    
    try:
        # Membaca CSV langsung dari URL
        df = pd.read_csv(sheet_url)
        
        # Bersihkan nama kolom (hapus spasi di awal/akhir)
        df.columns = df.columns.str.strip()
        
        # Konversi kolom 'Waktu' ke format datetime agar bisa diurutkan
        df['Waktu'] = pd.to_datetime(df['Waktu'])
        
        # Urutkan berdasarkan waktu (data terbaru di paling bawah/atas tergantung selera)
        df = df.sort_values(by='Waktu')
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return None

# --- JUDUL DASHBOARD ---
st.title("🎛️ Real-time Sensor Dashboard")
st.markdown("Monitoring data sensor dari Google Sheets secara real-time")

# --- AUTO REFRESH LOGIC ---
# Checkbox untuk mengaktifkan update otomatis
count = st_autorefresh(interval=5000, limit=None, key="mysensor")

# --- TAMPILKAN DATA ---
df = get_data()

if df is not None and not df.empty:
    # Ambil data baris terakhir (data sensor paling baru)
    latest_data = df.iloc[-1]

    # --- BAGIAN 1: KARTU METRIK (Indikator Utama) ---
    st.markdown("### 📡 Status Terkini")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="🌡️ Suhu Rumah", value=f"{latest_data['suhu rumah']} °C")
    
    with col2:
        # Logika Rain Module: 0 biasanya tidak hujan, >0 hujan (sesuaikan dengan sensor Anda)
        status_hujan = "Hujan! 🌧️" if latest_data['Rain Module'] < 500 else "Cerah ☀️" 
        # *Catatan: Nilai sensor hujan analog biasanya terbalik (makin kecil makin basah) atau sebaliknya, sesuaikan logika if-nya.
        st.metric(label="🌧️ Sensor Hujan", value=latest_data['Rain Module'], delta=status_hujan)

    with col3:
        st.metric(label="💡 Cahaya (LDR)", value=f"{latest_data['LDR']}")

    with col4:
        st.metric(label="🆔 RFID Terakhir", value=f"{latest_data['RFID']}")

    st.markdown("---")

    # --- BAGIAN 2: GRAFIK VISUALISASI ---
    col_kiri, col_kanan = st.columns(2)

    with col_kiri:
        st.subheader("Grafik Suhu Rumah")
        # Menggunakan Plotly untuk grafik interaktif
        fig_temp = px.line(df, x='Waktu', y='suhu rumah', markers=True, title='Riwayat Suhu')
        fig_temp.update_layout(height=350)
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_kanan:
        st.subheader("Grafik Cahaya (LDR)")
        fig_ldr = px.area(df, x='Waktu', y='LDR', color_discrete_sequence=['orange'], title='Intensitas Cahaya')
        fig_ldr.update_layout(height=350)
        st.plotly_chart(fig_ldr, use_container_width=True)

    # --- BAGIAN 3: TABEL DATA MENTAH ---
    with st.expander("Lihat Data Mentah (Tabel)"):
        st.dataframe(df.sort_values(by='Waktu', ascending=False)) # Tampilkan yang terbaru di atas

else:
    st.warning("Menunggu data masuk...")
