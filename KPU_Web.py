import streamlit as st
import pandas as pd
import requests
from io import StringIO
import pytz
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v113.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION (LINK FIX) ---
# Link pubhtml Abang dikonversi otomatis ke format CSV agar bisa dibaca sistem
LINK_PUBHTML = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# Database Hasil & Form (TETAP)
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"
FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 3. DATA PEGAWAI (31 ORANG LENGKAP - TIDAK DIHAPUS) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "PNS"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "PNS"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "PNS"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "PNS"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum...", "PNS"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum...", "PNS"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "PNS"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "PNS"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem...", "PNS"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem...", "PNS"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem...", "PNS"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan...", "PNS"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem...", "PNS"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem...", "PNS"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem...", "PNS"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU...", "PPPK"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU...", "PPPK"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER...", "PPPK"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU...", "PPPK"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN...", "PPPK"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN...", "PPPK"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM...", "PPPK"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN...", "PPPK"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI...", "PPPK"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI...", "PPPK"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU...", "PPPK"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN...", "PPPK"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER...", "PPPK"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU...", "PPPK"]
}

# --- 4. HELPERS ---
def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def load_auth_db():
    try:
        r = requests.get(LINK_PUBHTML, timeout=10)
        df = pd.read_csv(StringIO(r.text))
        df.columns = [c.strip() for c in df.columns]
        # Cari kolom NIP secara cerdas
        col_nip = next((c for c in df.columns if 'NIP' in c.upper()), df.columns[1])
        df['NIP_CLEAN'] = df[col_nip].astype(str).str.strip().str.replace(".0", "", regex=False)
        return df
    except: return pd.DataFrame()

# --- 5. STYLING ---
st.markdown("""
    <style>
    .stApp { background: #0e1117; color: white; }
    .card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid #F59E0B; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. LOGIN ---
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
                    match = df_u[df_u['NIP_CLEAN'] == u_in.strip()]
                    if not match.empty:
                        # Cari kolom Password secara cerdas
                        col_pw = next((c for c in df_u.columns if 'PASS' in c.upper()), df_u.columns[2])
                        if str(p_in) == str(match.iloc[0][col_pw]).strip():
                            st.session_state.logged_in = True
                            st.session_state.user_data = match.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("Password Salah.")
                    else: st.error("NIP tidak ditemukan.")
                else: st.error("Gagal memuat database.")
    st.stop()

# --- 7. MAIN DASHBOARD ---
u = st.session_state.user_data
st.title("🏛️ Hub Presensi KPU HSS")
st.sidebar.write(f"Login: **{u.get('Nama Pegawai', 'User')}**")

# --- MENU UPDATE (ABSEN & LAPKIN) ---
with st.container(border=True):
    st.subheader("🚀 Update Harian")
    loc = get_geolocation()
    if loc:
        lat_u, lon_u = loc['coords']['latitude'], loc['coords']['longitude']
        jarak = hitung_jarak(lat_u, lon_u, LAT_KANTOR, LON_KANTOR)
        st.info(f"📍 Jarak Anda: {int(jarak)}m dari kantor.")
        
        t1, t2 = st.tabs(["ABSENSI", "LAPORAN KERJA (LAPKIN)"])
        with t1:
            if jarak <= RADIUS_METER:
                if st.button("KIRIM ABSEN SEKARANG", use_container_width=True):
                    info = DATABASE_INFO.get(u.get('Nama Pegawai'), ["", "", "PNS"])
                    f_id = FORM_ID_PNS if info[2] == "PNS" else FORM_ID_PPPK
                    requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", 
                                  data={E_NAMA: u.get('Nama Pegawai'), E_NIP: info[0], E_JABATAN: info[1], "submit": "Submit"})
                    st.success("Berhasil Absen!"); time.sleep(1); st.rerun()
            else: st.error("MAAF! Anda di luar radius 100m. Tombol terkunci.")
        
        with t2:
            st_kerja = st.selectbox("Status Kehadiran:", ["Hadir", "Izin", "Sakit", "Tugas Luar"])
            uraian = st.text_area("Uraian Pekerjaan:")
            if st.button("SIMPAN LAPORAN", use_container_width=True):
                info = DATABASE_INFO.get(u.get('Nama Pegawai'), ["", "", "PNS"])
                requests.post(SCRIPT_LAPKIN, json={"nama": u.get('Nama Pegawai'), "nip": info[0], "status": st_kerja, "hasil": uraian})
                st.success("Laporan Tersimpan!"); time.sleep(1); st.rerun()
    else: st.warning("Aktifkan GPS Browser Anda untuk Absen.")

# --- FITUR ADMIN & GANTI PASSWORD ---
with st.expander("🔐 GANTI PASSWORD / ADMIN PANEL"):
    new_p = st.text_input("Password Baru", type="password")
    if st.button("Simpan Password Baru"):
        # Ambil NIP Clean dari session
        nip_val = u.get('NIP_CLEAN')
        requests.post(URL_SCRIPT_AUTH, json={"nip": nip_val, "action": "update_password", "new_password": new_p})
        st.success("Password diperbarui di Spreadsheet!")

if st.sidebar.button("Keluar"):
    st.session_state.logged_in = False
    st.rerun()
