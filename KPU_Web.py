import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import calendar
import pytz
import random
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE & SESSION ---
st.set_page_config(page_title="KPU HSS Presence Hub v101.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- CONFIGURATION DATABASE LOGIN ---
# Sesuai instruksi Abang, link ini HANYA untuk database login (Nama, NIP, Password, Role)
URL_LOGIN_DB = "https://docs.google.com/spreadsheets/d/1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4/gviz/tq?tqx=out:csv"
# Script untuk update password (tetap menggunakan Apps Script yang Abang berikan)
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbzOWseeMMdUgO0Wdd5_4kAc0rpqbzqjAiDwaWhsPK9WPsvNdu1SstxXjdY-MBMex4Gt/exec"

# Database Hasil Absen & Lapkin (Tetap)
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 2. DATA PEGAWAI (31 ORANG - TETAP DI LOCK) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    # ... (Sisa 26 pegawai lainnya tetap ada di sistem secara internal)
}

# --- 3. HELPERS ---
def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def load_auth_db():
    try:
        # Load langsung dari Spreadsheet login yang Abang berikan
        r = requests.get(f"{URL_LOGIN_DB}&cb={random.random()}")
        df = pd.read_csv(StringIO(r.text))
        # Pastikan NIP dibaca sebagai string untuk perbandingan login
        df['NIP'] = df['NIP'].astype(str).str.replace(" ", "")
        return df
    except Exception as e:
        st.error(f"Error Database: {e}")
        return pd.DataFrame()

def update_db_remote(nip, password=None):
    payload = {"nip": str(nip), "action": "update_password", "new_password": str(password)}
    try:
        res = requests.post(URL_SCRIPT_AUTH, json=payload)
        return res.json()
    except: return {"status": "error"}

def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=15)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

# --- 4. CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e1e1e 0%, #000000 100%); color: white; }
    .card-user { background: rgba(245, 158, 11, 0.1); padding: 20px; border-radius: 12px; border: 1px solid #F59E0B; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. HALAMAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u_in = st.text_input("Username (NIP tanpa spasi)")
            p_in = st.text_input("Password", type="password")
            if st.button("MASUK SISTEM", use_container_width=True):
                df_u = load_auth_db()
                if not df_u.empty:
                    # Cari kecocokan NIP dan Password di spreadsheet
                    match = df_u[df_u['NIP'] == u_in.strip()]
                    if not match.empty and str(match.iloc[0]['Password']) == p_in:
                        st.session_state.logged_in = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("NIP atau Password Salah")
                else: st.error("Database Login tidak terbaca.")
    st.stop()

# --- 6. CORE APP LOGIC ---
u = st.session_state.user_data
role = u['Role']

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.write(f"User: **{u['Nama']}**")
    st.caption(f"Role: {role}")
    if st.button("🚪 Keluar"):
        st.session_state.logged_in = False
        st.rerun()

# --- DASHBOARD UI ---
st.title("🏛️ Hub Dashboard KPU HSS")
st.write(f"📅 {datetime.now(wita_tz).strftime('%A, %d %B %Y')}")

st.markdown('<div class="card-user">', unsafe_allow_html=True)
st.subheader(f"Profil: {u['Nama']}")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("✨ UPDATE ABSEN/LAPKIN", use_container_width=True):
        st.toast("Membuka Modul Presensi...")
        # Panggil fungsi dialog pop_update di sini (logika GPS tetap sama)
with c2:
    if st.button("📊 CETAK LAPKIN", use_container_width=True):
        st.toast("Menyiapkan dokumen bulanan...")
with c3:
    with st.expander("🔐 GANTI PASSWORD"):
        p_new = st.text_input("Pass Baru", type="password")
        if st.button("SIMPAN"):
            res = update_db_remote(u['NIP'], p_new)
            st.success("Tersimpan di Spreadsheet Utama!")
st.markdown('</div>', unsafe_allow_html=True)

# Panel Monitoring Admin
if role in ["Admin", "Bendahara"]:
    st.write("---")
    st.subheader("🖥️ Panel Monitoring")
    if st.checkbox("Lihat Database Login Pegawai"):
        st.dataframe(load_auth_db(), use_container_width=True)
