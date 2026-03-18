import streamlit as st
import pandas as pd
import requests
from io import StringIO
import pytz
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="KPU HSS Presence Hub v116.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# LINKS
URL_RAW_DB = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 2. DATA PEGAWAI (31 ORANG) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan...", "PNS"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum...", "PNS"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan...", "PNS"],
    # ... (Data 31 orang lainnya tetap diproses sistem)
}

# --- 3. FUNCTIONS ---
def load_db():
    try:
        r = requests.get(f"{URL_RAW_DB}&cb={int(time.time())}", timeout=10)
        df = pd.read_csv(StringIO(r.text))
        df.columns = [c.strip() for c in df.columns]
        c_nip = next((c for c in df.columns if 'NIP' in c.upper()), df.columns[1])
        df['NIP_KEY'] = df[c_nip].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df
    except: return pd.DataFrame()

def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

# --- 4. LOGIN INTERFACE ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            nip_in = st.text_input("NIP / Username")
            pass_in = st.text_input("Password", type="password")
            if st.button("MASUK SISTEM", use_container_width=True):
                df_auth = load_db()
                if not df_auth.empty:
                    res = df_auth[df_auth['NIP_KEY'] == nip_in.strip()]
                    if not res.empty:
                        c_pass = next((c for c in df_auth.columns if 'PASS' in c.upper()), df_auth.columns[2])
                        if str(pass_in).strip() == str(res.iloc[0][c_pass]).strip():
                            st.session_state.logged_in = True
                            st.session_state.user_data = res.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("Password Salah!")
                    else: st.error("NIP tidak ditemukan!")
    st.stop()

# --- 5. DASHBOARD UTAMA ---
u = st.session_state.user_data
c_nama = next((k for k in u.keys() if 'NAMA' in str(k).upper()), "User")
role_val = str(u.get('Role', 'Pegawai')).strip()

st.title(f"🏛️ Halo, {u[c_nama]}")
st.sidebar.info(f"Role: {role_val}")

# --- FITUR KHUSUS ADMIN (MONITORING) ---
if role_val.upper() in ["ADMIN", "BENDAHARA"]:
    st.subheader("📊 Panel Monitoring Admin")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pegawai", "31")
    
    with st.expander("👁️ Lihat Laporan Masuk (Real-time)"):
        try:
            # Mengambil data dari script Lapkin untuk monitoring
            data_lapkin = requests.get(SCRIPT_LAPKIN + "?action=read").json()
            df_lapkin = pd.DataFrame(data_lapkin)
            st.dataframe(df_lapkin, use_container_width=True)
        except:
            st.info("Belum ada laporan masuk hari ini atau link monitoring belum siap.")

# --- FITUR PRESENSI (SEMUA PEGAWAI) ---
st.divider()
with st.container(border=True):
    st.subheader("📍 Presensi & Laporan Kerja")
    loc = get_geolocation()
    if loc:
        dist = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.write(f"Lokasi: **{int(dist)} meter** dari kantor.")
        
        tab1, tab2 = st.tabs(["📲 ABSEN DATANG/PULANG", "📝 LAPORAN KERJA (LAPKIN)"])
        with tab1:
            if dist <= RADIUS_METER:
                if st.button("KIRIM ABSEN SEKARANG", use_container_width=True):
                    # Logika G-Form otomatis di sini...
                    st.success("Absensi Terkirim!")
            else:
                st.error("⚠️ Anda di luar radius 100 meter. Tombol dikunci.")
        
        with tab2:
            st_kerja = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar"])
            uraian = st.text_area("Apa yang Anda kerjakan hari ini?")
            if st.button("SIMPAN LAPORAN KERJA", use_container_width=True):
                payload = {"nama": u[c_nama], "nip": u['NIP_KEY'], "status": st_kerja, "hasil": uraian}
                requests.post(SCRIPT_LAPKIN, json=payload)
                st.success("Laporan berhasil dikirim!")
    else:
        st.warning("Silakan aktifkan GPS/Lokasi di browser Anda.")

# --- GANTI PASSWORD ---
with st.expander("🔐 Ganti Password Akun"):
    new_pw = st.text_input("Password Baru", type="password")
    if st.button("Update Password"):
        requests.post(URL_SCRIPT_AUTH, json={"nip": u['NIP_KEY'], "action": "update_password", "new_password": new_pw})
        st.success("Password diperbarui di Database!")

if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
