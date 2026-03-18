import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v109.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
SHEET_ID = "1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# --- 3. FUNGSI AMBIL DATA (SMART COLUMN MATCHING) ---
def load_auth_db():
    export_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        response = requests.get(f"{export_url}&t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            
            # --- STANDARISASI KOLOM (PENTING!) ---
            # Kita ubah semua nama kolom jadi huruf kecil dan cari keywordnya
            cols = {col.lower(): col for col in df.columns}
            
            # Cari kolom NIP (bisa 'nip', 'nip/username', dll)
            col_nip = next((v for k, v in cols.items() if 'nip' in k), None)
            # Cari kolom Nama (bisa 'nama', 'nama pegawai', dll)
            col_nama = next((v for k, v in cols.items() if 'nama' in k), None)
            # Cari kolom Password
            col_pass = next((v for k, v in cols.items() if 'pass' in k), None)
            
            if col_nip and col_pass:
                # Rename biar seragam di dalam sistem
                df = df.rename(columns={col_nip: 'NIP', col_nama: 'Nama', col_pass: 'Password'})
                df['NIP'] = df['NIP'].astype(str).str.strip().str.replace(" ", "")
                return df
            else:
                st.error(f"Kolom tidak sesuai! Pastikan ada kolom 'NIP' dan 'Password'. Kolom saat ini: {list(df.columns)}")
        else:
            st.error("Gagal akses Google Sheets. Pastikan 'Anyone with link' aktif.")
    except Exception as e:
        st.error(f"Koneksi Error: {e}")
    return pd.DataFrame()

# --- 4. TAMPILAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            u_in = st.text_input("NIP / Username")
            p_in = st.text_input("Password", type="password")
            
            if st.button("MASUK SISTEM", use_container_width=True):
                df_u = load_auth_db()
                if not df_u.empty:
                    # Cari baris yang NIP-nya cocok
                    match = df_u[df_u['NIP'] == u_in.strip()]
                    if not match.empty:
                        # Ambil password dan bersihkan
                        db_pass = str(match.iloc[0]['Password']).strip()
                        if str(p_in) == db_pass:
                            st.session_state.logged_in = True
                            # Simpan data user ke session
                            st.session_state.user_data = match.iloc[0].to_dict()
                            st.rerun()
                        else:
                            st.error("❌ Password Salah!")
                    else:
                        st.error(f"❓ NIP '{u_in}' tidak ditemukan.")
    st.stop()

# --- 5. DASHBOARD (JIKA BERHASIL) ---
u = st.session_state.user_data
st.title(f"🏛️ Halo, {u['Nama']}")
st.write(f"NIP: {u['NIP']} | Role: {u.get('Role', 'Pegawai')}")

if st.button("✨ UPDATE HARIAN (ABSEN/LAPKIN)"):
    st.info("Fitur Presensi GPS sedang aktif...")

if st.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
