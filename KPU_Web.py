import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
import re
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v108.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
# Sesuai screenshot Abang: 1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4
SHEET_ID = "1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4"

# URL Script untuk EDIT/GANTI Password (Tetap pakai yang Abang kasih)
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 3. FUNGSI AMBIL DATA (ANTI-GAGAL) ---
def load_auth_db():
    # Kita paksa formatnya ke export?format=csv
    export_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        # Tambahkan timeout dan cache-busting
        response = requests.get(f"{export_url}&t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # Bersihkan spasi di nama kolom
            df.columns = [str(c).strip() for c in df.columns]
            # Pastikan kolom NIP ada dan bersih
            if 'NIP' in df.columns:
                df['NIP'] = df['NIP'].astype(str).str.strip().str.replace(" ", "")
                return df
            else:
                st.error("Kolom 'NIP' tidak ditemukan di Spreadsheet! Cek tulisan header di Sheet.")
        else:
            st.error(f"Google menolak akses (Status: {response.status_code}). Pastikan 'Anyone with the link' sudah aktif.")
    except Exception as e:
        st.error(f"Koneksi Error: {e}")
    return pd.DataFrame()

# --- 4. TAMPILAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        
        # Tombol Refresh Database (Buat jaga-jaga)
        if st.button("🔄 Refresh Koneksi Data"):
            st.cache_data.clear()
            st.rerun()

        with st.container(border=True):
            u_in = st.text_input("NIP (Username)", placeholder="Contoh: 19860601...")
            p_in = st.text_input("Password", type="password")
            
            if st.button("MASUK SISTEM", use_container_width=True):
                with st.spinner("Mencocokkan data..."):
                    df_u = load_auth_db()
                    if not df_u.empty:
                        # Debugging sederhana (Hapus ini jika sudah jalan)
                        # st.write(df_u.head()) 
                        
                        match = df_u[df_u['NIP'] == u_in.strip()]
                        if not match.empty:
                            # Ambil password dari kolom 'Password'
                            db_pass = str(match.iloc[0]['Password']).strip()
                            if str(p_in) == db_pass:
                                st.session_state.logged_in = True
                                st.session_state.user_data = match.iloc[0].to_dict()
                                st.rerun()
                            else:
                                st.error("❌ Password Salah!")
                        else:
                            st.error(f"❓ NIP '{u_in}' tidak terdaftar.")
                    else:
                        st.warning("⚠️ Gagal mengambil data dari Google Sheets.")
    st.stop()

# --- 5. DASHBOARD UTAMA (JIKA BERHASIL LOGIN) ---
u = st.session_state.user_data
st.title(f"🏛️ Selamat Datang, {u['Nama']}")
st.balloons()

with st.expander("🔐 PENGATURAN AKUN"):
    st.write(f"NIP: {u['NIP']}")
    st.write(f"Jabatan: {u['Role']}")
    new_p = st.text_input("Ganti Password Baru", type="password")
    if st.button("Simpan Password"):
        # Logika kirim ke Apps Script tetap sama
        res = requests.post(URL_SCRIPT_AUTH, json={"nip": u['NIP'], "action": "update_password", "new_password": new_p})
        st.success("Berhasil diupdate!")

if st.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
