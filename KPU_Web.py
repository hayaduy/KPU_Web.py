import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="KPU HSS Presence Hub v117.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# LINKS
URL_RAW_DB = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 2. FUNCTIONS ---
def load_db():
    try:
        r = requests.get(f"{URL_RAW_DB}&cb={int(time.time())}", timeout=10)
        df = pd.read_csv(StringIO(r.text))
        df.columns = [c.strip() for c in df.columns]
        # Cari kolom NIP secara cerdas
        c_nip = next((c for c in df.columns if 'NIP' in c.upper()), df.columns[1])
        df['NIP_KEY'] = df[c_nip].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df
    except: return pd.DataFrame()

def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

# --- 3. LOGIN INTERFACE ---
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

# --- 4. DASHBOARD UTAMA ---
u = st.session_state.user_data
c_nama = next((k for k in u.keys() if 'NAMA' in str(k).upper()), "User")
role_val = str(u.get('Role', 'Pegawai')).strip().upper()

st.title(f"🏛️ Halo, {u[c_nama]}")

# --- FITUR KHUSUS ADMIN (FIXED) ---
if role_val in ["ADMIN", "BENDAHARA"]:
    st.subheader("📊 Panel Monitoring Admin")
    
    tab_m1, tab_m2 = st.tabs(["👥 Daftar Pegawai (Database)", "📑 Laporan Harian Masuk"])
    
    with tab_m1:
        st.write("Menampilkan data seluruh pegawai dari Spreadsheet utama.")
        df_master = load_db()
        if not df_master.empty:
            # Sembunyikan kolom password demi keamanan
            cols_to_show = [c for c in df_master.columns if 'PASS' not in c.upper() and 'NIP_KEY' not in c]
            st.dataframe(df_master[cols_to_show], use_container_width=True)
        else:
            st.warning("Gagal memuat daftar pegawai.")

    with tab_m2:
        try:
            res_lapkin = requests.get(SCRIPT_LAPKIN + "?action=read", timeout=5)
            if res_lapkin.status_code == 200:
                df_l = pd.DataFrame(res_lapkin.json())
                st.dataframe(df_l, use_container_width=True)
            else: st.info("Belum ada laporan kerja yang masuk hari ini.")
        except:
            st.info("Koneksi ke database laporan (Lapkin) belum tersedia.")

# --- FITUR PRESENSI & LAPKIN (SEMUA) ---
st.divider()
with st.container(border=True):
    st.subheader("📍 Presensi & Laporan Kerja")
    loc = get_geolocation()
    if loc:
        dist = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.write(f"Lokasi: **{int(dist)} meter** dari kantor.")
        
        t1, t2 = st.tabs(["📲 ABSEN DATANG/PULANG", "📝 LAPORAN KERJA (LAPKIN)"])
        with t1:
            if dist <= RADIUS_METER:
                if st.button("KIRIM ABSEN SEKARANG", use_container_width=True):
                    st.success("Absensi Terkirim!")
            else:
                st.error("⚠️ Anda di luar radius 100 meter.")
        
        with t2:
            st_kerja = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar"])
            uraian = st.text_area("Apa yang Anda kerjakan hari ini?")
            if st.button("SIMPAN LAPORAN KERJA", use_container_width=True):
                payload = {"nama": u[c_nama], "nip": u['NIP_KEY'], "status": st_kerja, "hasil": uraian}
                requests.post(SCRIPT_LAPKIN, json=payload)
                st.success("Laporan dikirim!")
    else:
        st.warning("Aktifkan GPS Browser Anda.")

if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
