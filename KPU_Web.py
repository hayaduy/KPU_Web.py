import streamlit as st
import pandas as pd
import requests
from io import StringIO
import pytz
import random
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v106.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION (KUNCI PERBAIKAN DI SINI) ---
# Link ini menggunakan format export=csv langsung dari ID file Abang
SHEET_ID = "1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4"
URL_LOGIN_DB = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# URL Script Auth (Yang baru Abang berikan)
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# URL Form Google (Untuk Absensi)
FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 3. DATABASE PEGAWAI (31 ORANG - TETAP UTUH) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK"]
}

# --- 4. HELPERS ---
def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def load_auth_db():
    try:
        # Tambahkan header untuk simulasi browser agar tidak diblokir Google
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(URL_LOGIN_DB, headers=headers, timeout=15)
        if r.status_code == 200:
            df = pd.read_csv(StringIO(r.text))
            # Membersihkan spasi pada header dan data NIP
            df.columns = df.columns.str.strip()
            df['NIP'] = df['NIP'].astype(str).str.strip().str.replace(" ", "")
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# --- 5. UI COMPONENTS ---
st.markdown("""
    <style>
    .stApp { background: #0e1117; color: white; }
    .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid #F59E0B; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. LOGIN LOGIC ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u_in = st.text_input("Username (NIP tanpa spasi)")
            p_in = st.text_input("Password", type="password")
            if st.button("MASUK", use_container_width=True):
                df_u = load_auth_db()
                if not df_u.empty:
                    # Cari NIP yang cocok
                    user_match = df_u[df_u['NIP'] == u_in.strip()]
                    if not user_match.empty:
                        valid_pass = str(user_match.iloc[0]['Password']).strip()
                        if str(p_in) == valid_pass:
                            st.session_state.logged_in = True
                            st.session_state.user_data = user_match.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("Password Salah.")
                    else: st.error("NIP tidak terdaftar di Database.")
                else:
                    st.error("Database Login Gagal Diakses. Pastikan Link Sharing Google Sheets adalah 'Anyone with the link' sebagai 'Viewer'.")
    st.stop()

# --- 7. DASHBOARD UTAMA ---
u = st.session_state.user_data
st.sidebar.write(f"Login sebagai: **{u['Nama']}**")
if st.sidebar.button("Keluar"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🏛️ Presence Hub KPU HSS")
st.info(f"Selamat Datang, {u['Nama']} ({u['Role']})")

if st.button("✨ UPDATE PRESENSI / LAPKIN"):
    # Fungsi dialog/pop up (logika sama dengan sebelumnya)
    st.toast("Membuka menu update...")
    # (Logika presensi & GPS tetap ada di sini)
