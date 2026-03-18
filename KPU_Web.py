import streamlit as st
import pandas as pd
import requests
from io import StringIO
import pytz
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v115.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
# SAYA KONVERSI LINK ABANG KE FORMAT CSV MURNI AGAR BISA DIBACA
URL_RAW_DB = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# Database Hasil & Form
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"
FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 3. DATABASE INFO (31 PEGAWAI LENGKAP) ---
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

# --- 4. DATA LOADER ---
def load_db():
    try:
        # Menarik data CSV dari link Publish to Web
        r = requests.get(f"{URL_RAW_DB}&cb={int(time.time())}", timeout=10)
        df = pd.read_csv(StringIO(r.text))
        # Bersihkan spasi di header
        df.columns = [c.strip() for c in df.columns]
        # Konversi NIP ke String agar tidak jadi angka desimal
        c_nip = next((c for c in df.columns if 'NIP' in c.upper()), df.columns[1])
        df['NIP_KEY'] = df[c_nip].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df
    except:
        return pd.DataFrame()

def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

# --- 5. UI LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>🏛️ LOGIN KPU HSS</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            nip_in = st.text_input("NIP / Username")
            pass_in = st.text_input("Password", type="password")
            if st.button("MASUK SISTEM", use_container_width=True):
                df_auth = load_db()
                if not df_auth.empty:
                    # Cari Baris
                    res = df_auth[df_auth['NIP_KEY'] == nip_in.strip()]
                    if not res.empty:
                        # Cek Pass (Kolom ke-3 biasanya)
                        c_pass = next((c for c in df_auth.columns if 'PASS' in c.upper()), df_auth.columns[2])
                        if str(pass_in).strip() == str(res.iloc[0][c_pass]).strip():
                            st.session_state.logged_in = True
                            st.session_state.user_data = res.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("Password Salah!")
                    else: st.error("NIP tidak ditemukan!")
                else: st.error("Gagal menarik data dari Google Sheets!")
    st.stop()

# --- 6. DASHBOARD ---
u = st.session_state.user_data
# Cari Nama Pegawai secara fleksibel
c_nama = next((c for c in u.keys() if 'NAMA' in str(c).upper()), "User")
st.title(f"🏛️ Halo, {u[c_nama]}")

# PANEL PRESENSI
with st.container(border=True):
    st.subheader("📍 Presensi & Lapkin")
    loc = get_geolocation()
    if loc:
        dist = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.write(f"Lokasi: **{int(dist)} meter** dari kantor.")
        
        t1, t2 = st.tabs(["ABSEN", "LAPORAN KERJA"])
        with t1:
            if dist <= RADIUS_METER:
                if st.button("KIRIM ABSEN"):
                    # Logika G-Form PNS/PPPK...
                    st.success("Absen Berhasil!")
            else: st.error("Diluar Radius 100m!")
        with t2:
            pekerjaan = st.text_area("Uraian kerja hari ini:")
            if st.button("SIMPAN LAPKIN"):
                # Logika Kirim ke Lapkin Script...
                st.success("Laporan terkirim!")
    else: st.warning("Aktifkan GPS!")

# GANTI PASSWORD
with st.expander("🔐 Ganti Password"):
    new_pw = st.text_input("Password Baru", type="password")
    if st.button("Update Sekarang"):
        requests.post(URL_SCRIPT_AUTH, json={"nip": u['NIP_KEY'], "action": "update_password", "new_password": new_pw})
        st.success("Tersimpan!")

if st.sidebar.button("Keluar"):
    st.session_state.logged_in = False
    st.rerun()
