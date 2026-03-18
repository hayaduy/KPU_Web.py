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
st.set_page_config(page_title="KPU HSS Presence Hub v99.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- CONFIGURATION (LINK DATABASE ABANG) ---
URL_AUTH_SS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSl2RdRthniRbPIJXmMRPdDlLADmpNTZYO9fY9NixfjdrSWd4UKrzoFH_8ZcxYg1_y2thPdkqUi5CIQ/pub?output=csv"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbzOWseeMMdUgO0Wdd5_4kAc0rpqbzqjAiDwaWhsPK9WPsvNdu1SstxXjdY-MBMex4Gt/exec"

# Database Spreadsheet KPU
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100

# --- 2. DATA CORE (31 PEGAWAI) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 3. HELPERS ---
def clean_logic(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

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

def update_db_remote(nip, password=None, role=None):
    payload = {"nip": str(nip)}
    if password: 
        payload["action"] = "update_password"
        payload["new_password"] = str(password)
    elif role:
        payload["action"] = "update_role"
        payload["new_role"] = str(role)
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
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; color: white; }
    .card-user { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid #F59E0B; margin-bottom: 15px; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    div[data-testid="stDialog"] div[role="dialog"] { background-color: #121212 !important; color: white !important; border: 1px solid #F59E0B !important; }
    div[role="radiogroup"] label { background-color: #262626 !important; padding: 10px !important; border-radius: 8px !important; border: 1px solid #404040 !important; }
    div[role="radiogroup"] label p { color: #F59E0B !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTH PAGE ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; color:#F59E0B;'>🏛️ KPU HSS LOGIN</h1>", unsafe_allow_html=True)
        nip_in = st.text_input("NIP (Username)")
        pass_in = st.text_input("Password", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            df_u = load_user_db()
            if not df_u.empty:
                match = df_u[df_u['NIP'] == nip_in.strip()]
                if not match.empty and str(match.iloc[0]['Password']) == pass_in:
                    st.session_state.logged_in = True
                    st.session_state.user_data = match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("NIP atau Password Salah")
            else: st.error("Database tidak terbaca")
    st.stop()

# --- 6. DASHBOARD MAIN ---
u = st.session_state.user_data
role = u['Role']

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.write(f"Halo, **{u['Nama']}**")
    st.caption(f"Role: {role}")
    if st.button("🚪 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- DIALOGS (GPS & LAPORAN) ---
@st.dialog("Update Absen/Lapkin")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    loc = get_geolocation()
    jarak = 9999
    if loc:
        jarak = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.info(f"📍 Jarak Anda: {int(jarak)}m dari kantor.")
    else: st.warning("Mohon izinkan akses GPS.")

    tipe = st.radio("Pilih Kegiatan:", ["Absen", "Lapkin"])
    if tipe == "Absen":
        if loc and jarak <= RADIUS_METER:
            if st.button("🚀 KIRIM ABSEN SEKARANG"):
                info = DATABASE_INFO[nama]
                f_id = FORM_ID_PNS if info[4] == "PNS" else FORM_ID_PPPK
                requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data={E_NAMA: nama, E_NIP: info[0], E_JABATAN: info[1], "submit": "Submit"})
                st.success("Terkirim!"); time.sleep(1); st.rerun()
        else: st.error("Tombol Terkunci! Anda di luar radius kantor.")
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Uraian Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            info = DATABASE_INFO[nama]
            requests.post(SCRIPT_LAPKIN, json={"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja})
            st.success("Tersimpan!"); time.sleep(1); st.rerun()

@st.dialog("Download Laporan Bulanan")
def pop_cetak(nama_target):
    c_b = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    if st.button("📊 GENERATE LAPKIN"):
        df = get_clean_df(URL_LAPKIN)
        if df is not None:
            df_f = df[df.iloc[:, 1] == nama_target]
            info = DATABASE_INFO[nama_target]
            atasan_nama = info[5]
            if atasan_nama == "Suwanto, SH., MH.": j_atasan = "Sekretaris KPU Kab. Hulu Sungai Selatan"
            else:
                j_raw = DATABASE_INFO.get(atasan_nama, ["-", "Kasubbag"])[1]
                j_atasan = "Kepala Sub Bagian " + j_raw.replace("Kasubbag ", "")
                if "TP-Hupmas" in j_atasan: j_atasan = "Kepala Sub Bagian Teknis Penyelenggaraan Pemilu,\nPartisipasi dan Hubungan Masyarakat"

            hr_t = calendar.monthrange(datetime.now(wita_tz).year, LIST_BULAN.index(c_b)+1)[1]
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                header = [["LAPORAN BULANAN"], ["SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN"], [], ["Bulan", f": {c_b}"], ["Nama", f": {nama_target}"]]
                body = [[i+1, f"{pd.to_datetime(r.iloc[0], dayfirst=True).day} {LIST_BULAN[pd.to_datetime(r.iloc[0], dayfirst=True).month-1]} {pd.to_datetime(r.iloc[0], dayfirst=True).year}", "Melaksanakan Pekerjaan...", r.iloc[5], "-"] for i, (_, r) in enumerate(df_f.iterrows())]
                pd.DataFrame(header + body).to_excel(writer, index=False, header=False)
            st.download_button("📥 DOWNLOAD", out.getvalue(), f"LAPKIN_{nama_target}.xlsx")

# --- 7. DASHBOARD UI ---
st.title("🏛️ DASHBOARD HUB KPU HSS")

# DASHBOARD MINIMALIS USER
st.markdown('<div class="card-user">', unsafe_allow_html=True)
st.subheader(f"Profil: {u['Nama']}")
c_1, c_2, c_3 = st.columns(3)
with c_1:
    if st.button("✨ UPDATE HARIAN", use_container_width=True): pop_update(u['Nama'])
with c_2:
    if st.button("🖨️ CETAK LAPKIN", use_container_width=True): pop_cetak(u['Nama'])
with c_3:
    with st.expander("🔑 GANTI PASSWORD"):
        np = st.text_input("Baru", type="password")
        if st.button("UBAH"):
            update_db_remote(u['NIP'], password=np)
            st.success("Tersimpan di Database!")
st.markdown('</div>', unsafe_allow_html=True)

# PANEL ADMIN & BENDAHARA (MONITORING 31 ORANG)
if role in ["Admin", "Bendahara"]:
    st.write("---")
    st.subheader("🖥️ Monitoring Dashboard")
    
    if role == "Admin":
        with st.expander("🔑 Database User & Admin (Sync Spreadsheet)"):
            st.dataframe(load_user_db(), use_container_width=True)

    tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PNS", "👥 PPPK"])
    
    def render_ui(masters, tab_id):
        df_pns = get_clean_df(URL_PNS)
        df_pppk = get_clean_df(URL_PPPK)
        df = pd.concat([df_pns, df_pppk]) if df_pns is not None else df_pppk
        today = datetime.now(wita_tz).strftime('%d/%m/%Y')
        
        for i, p in enumerate(masters, 1):
            log = df[(df.iloc[:, 1] == p) & (df.iloc[:, 0].str.contains(today))]
            k = "HADIR" if not log.empty else "ALPA"
            st_cls = "status-hadir" if k == "HADIR" else "status-alpa"
            st.markdown(f'<div class="employee-card"><div class="emp-name">{i}. {p}</div><div class="{st_cls}">{k}</div></div>', unsafe_allow_html=True)

    with tab_all: render_ui(list(DATABASE_INFO.keys()), "all")
    with tab_pns: render_ui(MASTER_PNS, "pns")
    with tab_pppk: render_ui(MASTER_PPPK, "pppk")
