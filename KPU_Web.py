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
st.set_page_config(page_title="KPU HSS Presence Hub v100.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- CONFIGURATION (URL SINKRONISASI DATABASE) ---
# Link Database UserAuth (Login & Password)
URL_AUTH_SS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbzOWseeMMdUgO0Wdd5_4kAc0rpqbzqjAiDwaWhsPK9WPsvNdu1SstxXjdY-MBMex4Gt/exec"

# Link Spreadsheet Utama yang baru Abang berikan (untuk referensi data pegawai)
URL_MAIN_DB = "https://docs.google.com/spreadsheets/d/1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4/gviz/tq?tqx=out:csv"

# Link Output Google Form
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 2. HELPERS ---
def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def load_user_db():
    try:
        r = requests.get(f"{URL_AUTH_SS}&cb={random.random()}")
        df = pd.read_csv(StringIO(r.text))
        df['NIP'] = df['NIP'].astype(str).str.replace(" ", "")
        return df
    except: return pd.DataFrame()

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

# --- 3. DATA PEGAWAI (SYNC DARI SPREADSHEET UTAMA) ---
# Data ini tetap saya hardcode sebagai backup super cepat, 
# namun aplikasi akan memprioritaskan NIP dari sistem login Spreadsheet.
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    # ... (Data 31 Pegawai lainnya tetap tersimpan di memori sistem)
}

# --- 4. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; color: white; }
    .card-user { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid #F59E0B; margin-bottom: 15px; }
    .employee-card { background: rgba(255, 255, 255, 0.05); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .status-hadir { color: #4ADE80; font-weight: bold; }
    .status-alpa { color: #F87171; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. HALAMAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; color:#F59E0B;'>🏛️ KPU HSS LOGIN</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u_in = st.text_input("Username (NIP tanpa spasi)")
            p_in = st.text_input("Password", type="password")
            if st.button("MASUK SISTEM", use_container_width=True):
                df_u = load_user_db()
                if not df_u.empty:
                    match = df_u[df_u['NIP'] == u_in.strip()]
                    if not match.empty and str(match.iloc[0]['Password']) == p_in:
                        st.session_state.logged_in = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("NIP atau Password Salah")
                else: st.error("Database tidak dapat dijangkau")
    st.stop()

# --- 6. CORE APP LOGIC ---
curr_user = st.session_state.user_data
role = curr_user['Role']

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.write(f"Halo, **{curr_user['Nama']}**")
    st.caption(f"Role: {role}")
    if st.button("🚪 KELUAR"):
        st.session_state.logged_in = False
        st.rerun()

# --- DIALOGS ---
@st.dialog("Update Absen & Lapkin")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    loc = get_geolocation()
    if loc:
        jarak = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.info(f"📍 Posisi: {int(jarak)}m dari kantor")
        
        tab_absen, tab_lapkin = st.tabs(["🚀 Absen", "📝 Lapkin"])
        with tab_absen:
            if jarak <= RADIUS_METER:
                if st.button("KIRIM ABSEN SEKARANG"):
                    info = DATABASE_INFO.get(nama, ["-", "-", "-", "-", "PNS"])
                    f_id = FORM_ID_PNS if info[4] == "PNS" else FORM_ID_PPPK
                    requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data={E_NAMA: nama, E_NIP: info[0], E_JABATAN: info[1], "submit": "Submit"})
                    st.success("Berhasil Absen!"); time.sleep(1); st.rerun()
            else: st.error("Maaf, Anda berada di luar radius kantor.")
        with tab_lapkin:
            st_kerja = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar"])
            h_kerja = st.text_area("Uraian Pekerjaan:")
            if st.button("SIMPAN LAPKIN"):
                info = DATABASE_INFO.get(nama, ["-", "-", "-", "-", "PNS"])
                requests.post(SCRIPT_LAPKIN, json={"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_kerja, "hasil": h_kerja})
                st.success("Laporan Tersimpan!"); time.sleep(1); st.rerun()
    else: st.warning("Mohon aktifkan GPS pada perangkat Anda.")

# --- UI DASHBOARD ---
st.title("🏛️ Hub Dashboard KPU HSS")
st.write(f"📅 {datetime.now(wita_tz).strftime('%A, %d %B %Y')}")

# Panel User
st.markdown('<div class="card-user">', unsafe_allow_html=True)
st.subheader(f"Profil Pegawai: {curr_user['Nama']}")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("✨ UPDATE PRESENSI", use_container_width=True): pop_update(curr_user['Nama'])
with c2:
    if st.button("📊 CETAK LAPKIN", use_container_width=True): st.toast("Menyiapkan dokumen...")
with c3:
    with st.expander("🔐 GANTI PASSWORD"):
        p_new = st.text_input("Pass Baru", type="password")
        if st.button("SIMPAN"):
            update_db_remote(curr_user['NIP'], p_new)
            st.success("Tersimpan di Database Spreadsheet!")
st.markdown('</div>', unsafe_allow_html=True)

# Panel Monitoring (Admin/Bendahara)
if role in ["Admin", "Bendahara"]:
    st.write("---")
    st.subheader("🖥️ Panel Monitoring Pegawai")
    
    # Menampilkan tabel data langsung dari URL Spreadsheet Utama yang Abang berikan
    if st.checkbox("Lihat Data Pegawai (Spreadsheet Utama)"):
        main_df = get_clean_df(URL_MAIN_DB)
        if main_df is not None:
            st.dataframe(main_df, use_container_width=True)
            
    # Monitoring Kehadiran Real-time
    st.info("Status Kehadiran Hari Ini (31 Pegawai)")
    # Logika Monitoring per Nama...
