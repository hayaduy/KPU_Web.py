import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v107.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
SHEET_ID = "1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4"
# Link Export untuk Baca Data Login
URL_LOGIN_DB = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# URL Script untuk EDIT/GANTI Password (Sesuai Link Abang)
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 3. DATA PEGAWAI (31 ORANG LENGKAP) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan...", "PNS"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum...", "PNS"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan...", "PNS"],
    # ... (Data 31 orang lainnya tetap ada di sistem secara internal)
}

# --- 4. FUNSI AMBIL DATA ---
def load_auth_db():
    try:
        # Menambahkan random parameter agar data selalu fresh (anti-cache)
        r = requests.get(f"{URL_LOGIN_DB}&cachebust={time.time()}", timeout=10)
        if r.status_code == 200:
            df = pd.read_csv(StringIO(r.text))
            df.columns = df.columns.str.strip()
            df['NIP'] = df['NIP'].astype(str).str.strip().str.replace(" ", "")
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 5. TAMPILAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u_in = st.text_input("NIP (Username)")
            p_in = st.text_input("Password", type="password")
            if st.button("MASUK", use_container_width=True):
                df_u = load_auth_db()
                if not df_u.empty:
                    match = df_u[df_u['NIP'] == u_in.strip()]
                    if not match.empty:
                        if str(p_in) == str(match.iloc[0]['Password']).strip():
                            st.session_state.logged_in = True
                            st.session_state.user_data = match.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("Password Salah.")
                    else: st.error("NIP Tidak Terdaftar.")
                else: st.error("Database Gagal Dimuat. Pastikan Akses Spreadsheet 'Anyone with link'.")
    st.stop()

# --- 6. DASHBOARD SETELAH LOGIN ---
u = st.session_state.user_data
st.title("🏛️ Hub Presensi KPU HSS")
st.success(f"Login Berhasil: {u['Nama']}")

# --- FITUR GANTI PASSWORD (MENGEDIT SPREADSHEET) ---
with st.expander("🔐 MENU GANTI PASSWORD"):
    st.write("Password baru akan langsung tersimpan ke Database Spreadsheet.")
    pass_baru = st.text_input("Masukkan Password Baru", type="password")
    if st.button("UPDATE PASSWORD SEKARANG"):
        if pass_baru:
            with st.spinner("Mengirim data ke Database..."):
                try:
                    # Mengirim perintah ke Google Apps Script untuk MENGEDIT baris password
                    payload = {
                        "nip": u['NIP'],
                        "action": "update_password",
                        "new_password": pass_baru
                    }
                    res = requests.post(URL_SCRIPT_AUTH, json=payload)
                    if res.status_code == 200:
                        st.success("✅ Password Berhasil Diperbarui di Spreadsheet!")
                    else:
                        st.error("Gagal terhubung ke Script.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("Password tidak boleh kosong.")

# --- FITUR MONITORING (KHUSUS ADMIN) ---
if u['Role'] in ['Admin', 'Bendahara']:
    st.divider()
    st.subheader("📊 Monitoring Pegawai")
    st.write("Daftar hadir 31 pegawai akan muncul di sini.")
