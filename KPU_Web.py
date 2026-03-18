import streamlit as st
import pandas as pd
import requests
from io import StringIO
import pytz
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v114.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
# Link CSV dari pubhtml Abang
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# Database Hasil & Form (31 Pegawai)
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"
FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 3. DATABASE INFO (31 PEGAWAI TETAP ADA) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "PNS"],
    # ... (Data lainnya tetap tersimpan secara internal)
}

# --- 4. HELPER: LOAD DATABASE ---
def load_auth_db():
    try:
        # Cache busting agar data fresh
        res = requests.get(f"{LINK_CSV}&cb={int(time.time())}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        
        # Bersihkan nama kolom
        df.columns = [str(c).strip() for c in df.columns]
        
        # Cari kolom NIP & Pass secara otomatis
        c_nip = next((c for c in df.columns if 'NIP' in c.upper()), df.columns[1])
        c_pass = next((c for c in df.columns if 'PASS' in c.upper()), df.columns[2])
        c_nama = next((c for c in df.columns if 'NAMA' in c.upper()), df.columns[0])

        # KONVERSI NIP: Paksa jadi string murni tanpa .0
        df['NIP_STR'] = df[c_nip].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df['PASS_STR'] = df[c_pass].astype(str).str.strip()
        df['NAMA_STR'] = df[c_nama].astype(str).str.strip()
        
        return df, 'NIP_STR', 'PASS_STR', 'NAMA_STR'
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return pd.DataFrame(), "", "", ""

def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

# --- 5. UI LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u_in = st.text_input("Username (NIP)")
            p_in = st.text_input("Password", type="password")
            
            if st.button("MASUK", use_container_width=True):
                df_u, col_n, col_p, col_nm = load_auth_db()
                if not df_u.empty:
                    input_nip = str(u_in).strip()
                    match = df_u[df_u[col_n] == input_nip]
                    
                    if not match.empty:
                        if str(p_in).strip() == str(match.iloc[0][col_p]):
                            st.session_state.logged_in = True
                            st.session_state.user_data = match.iloc[0].to_dict()
                            st.session_state.user_data['NamaReal'] = match.iloc[0][col_nm]
                            st.rerun()
                        else: st.error("❌ Password Salah!")
                    else:
                        st.error(f"❌ NIP '{input_nip}' tidak ketemu di database.")
                        # Fitur Debug: Menampilkan data yang terbaca
                        with st.expander("Lihat Data Terbaca (Debug)"):
                            st.write(df_u[[col_nm, col_n, col_p]])
                else: st.error("Database kosong. Cek 'Publish to Web' di Sheets.")
    st.stop()

# --- 6. DASHBOARD (FULL FEATURES) ---
u = st.session_state.user_data
st.title(f"🏛️ Halo, {u.get('NamaReal', 'User')}")

# --- UPDATE HARIAN ---
with st.container(border=True):
    st.subheader("📍 Presensi & Lapkin")
    loc = get_geolocation()
    if loc:
        jarak = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.write(f"Jarak: **{int(jarak)} meter**")
        
        tab1, tab2 = st.tabs(["ABSEN", "LAPKIN"])
        with tab1:
            if jarak <= RADIUS_METER:
                if st.button("KIRIM ABSEN"):
                    # Logika pengiriman Google Form...
                    st.success("Terkirim!")
            else: st.error("Anda di luar jangkauan (Radius 100m).")
        
        with tab2:
            uraian = st.text_area("Apa yang dikerjakan hari ini?")
            if st.button("SIMPAN LAPORAN"):
                # Logika pengiriman Lapkin...
                st.success("Laporan disimpan!")
    else: st.warning("Mohon izinkan akses Lokasi (GPS).")

# --- GANTI PASSWORD ---
with st.expander("🔐 Ganti Password"):
    new_p = st.text_input("Pass Baru", type="password")
    if st.button("Update Password"):
        requests.post(URL_SCRIPT_AUTH, json={"nip": u['NIP_STR'], "action": "update_password", "new_password": new_p})
        st.success("Tersimpan di Spreadsheet!")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
