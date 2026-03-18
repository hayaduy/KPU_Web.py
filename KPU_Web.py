import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v110.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
SHEET_ID = "1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# --- 3. FUNGSI AMBIL DATA (SISTEM POSISI KOLOM) ---
def load_auth_db():
    export_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        response = requests.get(f"{export_url}&t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            # Baca tanpa header dulu untuk menghindari KeyError
            df = pd.read_csv(StringIO(response.text))
            
            # PAKSA PENAMAAN ULANG BERDASARKAN URUTAN (A, B, C, D)
            # Asumsi: Kolom 0=Nama, 1=NIP, 2=Password, 3=Role
            new_cols = ['Nama', 'NIP', 'Password', 'Role']
            
            # Jika jumlah kolom di sheet lebih banyak, kita sesuaikan
            current_cols_count = len(df.columns)
            if current_cols_count >= 4:
                df.columns = new_cols + list(df.columns[4:])
            else:
                st.error(f"Spreadsheet Abang cuma punya {current_cols_count} kolom. Minimal harus ada 4 (Nama, NIP, Pass, Role).")
                return pd.DataFrame()

            # Bersihkan data NIP & Password
            df['NIP'] = df['NIP'].astype(str).str.strip().str.replace(" ", "")
            df['Password'] = df['Password'].astype(str).str.strip()
            return df
        else:
            st.error("Gagal konek ke Google Sheets.")
    except Exception as e:
        st.error(f"Error Sistem: {e}")
    return pd.DataFrame()

# --- 4. TAMPILAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            u_in = st.text_input("Username / NIP", help="Masukkan NIP sesuai di Spreadsheet")
            p_in = st.text_input("Password", type="password")
            
            if st.button("MASUK SISTEM", use_container_width=True):
                with st.spinner("Menghubungkan ke Database..."):
                    df_u = load_auth_db()
                    if not df_u.empty:
                        # Cari NIP yang cocok
                        match = df_u[df_u['NIP'] == u_in.strip()]
                        if not match.empty:
                            db_pass = str(match.iloc[0]['Password'])
                            if str(p_in) == db_pass:
                                st.session_state.logged_in = True
                                st.session_state.user_data = match.iloc[0].to_dict()
                                st.rerun()
                            else:
                                st.error("❌ Password Salah!")
                        else:
                            st.error(f"❓ NIP '{u_in}' tidak terdaftar.")
                    else:
                        st.warning("⚠️ Database kosong atau tidak bisa dibaca.")
    st.stop()

# --- 5. DASHBOARD BERHASIL ---
u = st.session_state.user_data
st.title(f"🏛️ Selamat Datang, {u['Nama']}")
st.success(f"Anda login sebagai {u['Role']}")

if st.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
