# git untuk tambah remote : git remote add origin

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Smart IoT Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

# --- FIREBASE CONFIG ---
FIREBASE_URL = "https://iot-1-59a09-default-rtdb.asia-southeast1.firebasedatabase.app"
DEVICE_ID = "esp32_01"

# --- AMBIL DATA DARI FIREBASE ---
def get_data():
    try:
        url = f"{FIREBASE_URL}/devices/{DEVICE_ID}.json"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()
        if data is None:
            return None

        # Konversi ke DataFrame 1 baris (biar kompatibel dg plot)
        df = pd.DataFrame([{
            "Waktu": datetime.fromtimestamp(data["timestamp"]),
            "suhu": data["suhu"],
            "rainvalue": data["rainvalue"],
            "ldrValue": data["ldrValue"],
            "pintu": data["pintu"]
        }])

        return df

    except Exception:
        return None

# --- STATE MANAGEMENT ---
if "last_timestamp" not in st.session_state:
    st.session_state["last_timestamp"] = None

# --- UI ---
st.title("⚡ Real-time Smart Dashboard")
st.caption("Dashboard hanya update jika data Firebase berubah")

dashboard_placeholder = st.empty()

# --- LOOP UTAMA ---
while True:
    df = get_data()

    if df is not None and not df.empty:
        latest_timestamp = df.iloc[0]["Waktu"]

        if latest_timestamp != st.session_state["last_timestamp"]:
            st.session_state["last_timestamp"] = latest_timestamp

            with dashboard_placeholder.container():
                st.success(
                    f"Data Baru Diterima! "
                    f"Update terakhir: {latest_timestamp.strftime('%H:%M:%S')}"
                )

                latest = df.iloc[0]

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🌡️ Suhu", f"{latest['suhu']} °C")

                status_hujan = "Basah" if latest["rainvalue"] < 500 else "Kering"
                col2.metric("🌧️ Hujan", latest["rainvalue"], status_hujan)

                col3.metric("💡 Cahaya", latest["ldrValue"])
                col4.metric("🚪 Pintu", "Terbuka" if latest["pintu"] == 1 else "Tertutup")

                st.markdown("---")

                # Grafik (dummy history dari cache)
                history = st.session_state.get("history", pd.DataFrame())
                history = pd.concat([history, df]).tail(20)
                st.session_state["history"] = history

                c1, c2 = st.columns(2)

                with c1:
                    fig_temp = px.line(
                        history,
                        x="Waktu",
                        y="suhu",
                        title="20 Data Terakhir: Suhu",
                        markers=True
                    )
                    st.plotly_chart(fig_temp, use_container_width=True)

                with c2:
                    fig_ldr = px.area(
                        history,
                        x="Waktu",
                        y="ldrValue",
                        title="20 Data Terakhir: Cahaya"
                    )
                    st.plotly_chart(fig_ldr, use_container_width=True)

    time.sleep(3)
