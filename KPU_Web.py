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

# --- 1. SETUP & SESSION ---
st.set_page_config(page_title="KPU HSS Presence Hub v95.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# KOORDINAT KANTOR
LAT_KANTOR = -2.775087
LON_KANTOR = 115.228639
RADIUS_METER = 100 

LIBUR_DAN_CUTI_2026 = {
    "2026-01-01": "Tahun Baru 2026", "2026-01-19": "Isra Mi'raj", "2026-02-17": "Imlek",
    "2026-03-18": "Cuti Nyepi", "2026-03-19": "Cuti Nyepi", "2026-03-20": "Hari Nyepi",
    "2026-03-21": "Idul Fitri", "2026-03-22": "Idul Fitri", "2026-03-23": "Cuti Idul Fitri",
    "2026-03-24": "Cuti Idul Fitri", "2026-03-25": "Cuti Idul Fitri", "2026-04-03": "Wafat Yesus",
    "2026-05-01": "Hari Buruh", "2026-05-14": "Kenaikan Yesus", "2026-05-22": "Waisak",
    "2026-06-01": "Hari Lahir Pancasila", "2026-08-17": "HUT RI", "2026-12-25": "Natal"
}

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 2. DATABASE CORE (31 PEGAWAI - DATA UTUH) ---
# Format: [NIP_ASLI, JABATAN, UNIT, SUBBAG, KATEGORI, ATASAN, NIP_ATASAN, ROLE_SISTEM]
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-", "Admin"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Admin"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Bendahara"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Admin"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Admin"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    
    # PPPK
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"]
}

# --- 3. HELPERS ---
def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def clean_logic(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=15)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

# --- 4. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .login-card { background: rgba(0,0,0,0.6); padding: 30px; border-radius: 15px; border: 1px solid #F59E0B; }
    .user-card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid #F59E0B; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .status-hadir { color: #10B981; } .status-alpa { color: #EF4444; }
    div[data-testid="stDialog"] div[role="dialog"] { background-color: #121212 !important; border: 1px solid #F59E0B !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTH LOGIC ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        with st.container():
            username = st.text_input("NIP (Tanpa Spasi)")
            password = st.text_input("Password", type="password")
            if st.button("MASUK SISTEM", use_container_width=True):
                found = False
                for nama, info in DATABASE_INFO.items():
                    if username == info[0].replace(" ", ""):
                        if password == "kpuhss2026": # Default Pass
                            st.session_state.logged_in = True
                            st.session_state.user_data = {"nama": nama, "role": info[7], "info": info}
                            found = True
                            st.rerun()
                if not found: st.error("NIP atau Password salah!")
    st.stop()

# --- 6. DASHBOARD MAIN ---
u_data = st.session_state.user_data
nama_user = u_data['nama']
role_user = u_data['role']

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.write(f"User: **{nama_user}**")
    st.write(f"Role: `{role_user}`")
    if st.button("🚪 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- 7. DIALOGS (Sama seperti versi 93 namun Role-Aware) ---
@st.dialog("Update Data (Radius)")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    loc = get_geolocation()
    jarak = 999999
    is_in_range = False
    if loc:
        u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
        jarak = hitung_jarak(u_lat, u_lon, LAT_KANTOR, LON_KANTOR)
        is_in_range = jarak <= RADIUS_METER
        st.info(f"📍 Jarak: {int(jarak)}m dari kantor.")
    else: st.warning("Izinkan GPS untuk Absen.")

    tipe = st.radio("Pilih:", ["Absen", "Lapkin"])
    if tipe == "Absen":
        if is_in_range:
            if st.button("🚀 KIRIM ABSEN"):
                f_id = FORM_ID_PNS if u_data['info'][4] == "PNS" else FORM_ID_PPPK
                requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data={E_NAMA: nama, E_NIP: u_data['info'][0], E_JABATAN: u_data['info'][1], "submit": "Submit"})
                st.success("Sukses!"); time.sleep(1); st.rerun()
        else: st.error("Diluar jangkauan kantor!")
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            requests.post(SCRIPT_LAPKIN, json={"nama": nama, "nip": u_data['info'][0], "jabatan": u_data['info'][1], "status": st_fix, "hasil": h_kerja})
            st.success("Tersimpan!"); time.sleep(1); st.rerun()

# --- 8. UI USER DASHBOARD (Minimalis) ---
st.markdown(f"## 🏛️ HUB KPU HSS - {role_user}")
st.write(f"Hari ini: {datetime.now(wita_tz).strftime('%A, %d %B %Y')}")

if role_user == "Pegawai" or role_user == "Bendahara":
    c1, c2 = st.columns([1.5, 2.5])
    with c1:
        st.markdown(f"""<div class="user-card">
            <h4>{nama_user}</h4>
            <p>NIP: {u_data['info'][0]}<br>Jabatan: {u_data['info'][1]}</p>
        </div>""", unsafe_allow_html=True)
        if st.button("✨ UPDATE ABSEN / LAPKIN"): pop_update(nama_user)
        # Tombol Download Lapkin Khusus User
        if st.button("📥 DOWNLOAD LAPKIN PRIBADI"): st.info("Membuka menu cetak...") # Hubungkan ke pop_cetak()
    
    with c2:
        st.markdown("#### 📊 Kehadiran Anda")
        # Logic filter data absensi dari spreadsheet yang namanya == nama_user
        st.caption("Data kehadiran pribadi...")

# --- 9. UI ADMIN / BENDAHARA (Full Access) ---
if role_user in ["Admin", "Bendahara"]:
    st.write("---")
    st.markdown("### 🖥️ Monitoring Panel")
    tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
    # Panggil fungsi render_ui() yang lama di sini untuk memunculkan list 31 orang
