import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import pytz
import random
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE & SESSION ---
st.set_page_config(page_title="KPU HSS Presence Hub v105.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- CONFIGURATION (LINK DATABASE) ---
# Link Spreadsheet Login (CSV Format)
URL_LOGIN_DB = "https://docs.google.com/spreadsheets/d/1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4/export?format=csv"
# URL SCRIPT TERBARU YANG ABANG BERIKAN
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# Database Hasil & Form (Tetap)
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 2. DATA PEGAWAI (31 ORANG LENGKAP) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

# --- 3. HELPERS ---
def hitung_jarak(lat1, lon1, lat2, lon2):
    R = 6371000 
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * asin(sqrt(a))

def load_auth_db():
    try:
        r = requests.get(f"{URL_LOGIN_DB}&cb={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(r.text))
        df['NIP'] = df['NIP'].astype(str).str.replace(" ", "")
        return df
    except: return pd.DataFrame()

# --- 4. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e1e1e 0%, #000000 100%); color: white; }
    .card-user { background: rgba(245, 158, 11, 0.1); padding: 20px; border-radius: 12px; border: 1px solid #F59E0B; margin-bottom: 20px; }
    .employee-card { background: rgba(255, 255, 255, 0.05); padding: 10px 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 5px; display: flex; align-items: center; }
    .status-hadir { color: #4ADE80; font-weight: bold; flex: 1; text-align: right; }
    .status-alpa { color: #F87171; font-weight: bold; flex: 1; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DIALOGS ---
@st.dialog("Update Presensi & Lapkin", width="large")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    loc = get_geolocation()
    if loc:
        jarak = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR)
        st.info(f"📍 Posisi: {int(jarak)}m dari kantor")
        
        mode = st.radio("Kegiatan:", ["Absensi Kedatangan", "Laporan Kerja (Lapkin)"])
        if mode == "Absensi Kedatangan":
            if jarak <= RADIUS_METER:
                if st.button("KIRIM ABSEN"):
                    info = DATABASE_INFO[nama]
                    f_id = FORM_ID_PNS if info[4] == "PNS" else FORM_ID_PPPK
                    requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data={E_NAMA: nama, E_NIP: info[0], E_JABATAN: info[1], "submit": "Submit"})
                    st.success("Terkirim!"); time.sleep(1); st.rerun()
            else: st.error("Terkunci! Harus berada di radius 100m.")
        else:
            stat = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar"])
            uraian = st.text_area("Uraian Pekerjaan:")
            if st.button("SIMPAN LAPORAN"):
                info = DATABASE_INFO[nama]
                requests.post(SCRIPT_LAPKIN, json={"nama": nama, "nip": info[0], "jabatan": info[1], "status": stat, "hasil": uraian})
                st.success("Tersimpan!"); time.sleep(1); st.rerun()
    else: st.warning("Aktifkan GPS!")

# --- 6. AUTH LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u_in = st.text_input("Username (NIP tanpa spasi)")
            p_in = st.text_input("Password", type="password")
            if st.button("MASUK", use_container_width=True):
                df_u = load_auth_db()
                if not df_u.empty:
                    match = df_u[df_u['NIP'] == u_in.strip()]
                    if not match.empty and str(match.iloc[0]['Password']) == p_in:
                        st.session_state.logged_in = True
                        st.session_state.user_data = match.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Cek NIP/Password.")
                else: st.error("Database Login Tidak Terbaca.")
    st.stop()

# --- 7. MAIN UI ---
u = st.session_state.user_data
st.sidebar.write(f"Halo, **{u['Nama']}**")
if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🏛️ Presence Hub KPU HSS")
st.markdown('<div class="card-user">', unsafe_allow_html=True)
st.write(f"Role: {u['Role']}")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("✨ UPDATE HARIAN", use_container_width=True): pop_update(u['Nama'])
with c2:
    if st.button("📊 CETAK LAPKIN", use_container_width=True): st.toast("Menyiapkan dokumen...")
with c3:
    with st.expander("🔐 GANTI PASSWORD"):
        p_new = st.text_input("Pass Baru", type="password")
        if st.button("SIMPAN"):
            requests.post(URL_SCRIPT_AUTH, json={"nip": u['NIP'], "action": "update_password", "new_password": p_new})
            st.success("Tersimpan!")
st.markdown('</div>', unsafe_allow_html=True)

if u['Role'] in ["Admin", "Bendahara"]:
    st.subheader("🖥️ Monitoring Kehadiran (31 Pegawai)")
    for i, p in enumerate(DATABASE_INFO.keys(), 1):
        st.markdown(f'<div class="employee-card"><div>{i}. {p}</div><div class="status-alpa">ALPA</div></div>', unsafe_allow_html=True)
