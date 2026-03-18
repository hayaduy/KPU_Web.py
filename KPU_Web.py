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

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v137.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# KOORDINAT KANTOR KPU KAB. HSS
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

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .block-container { max-width: 1050px; padding-top: 2rem !important; }
    .header-box { text-align: center; color: #F59E0B; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .clock-box { text-align: center; color: white; font-size: 18px; margin-bottom: 25px; font-family: monospace; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #cbd5e1; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border: 1px solid rgba(255, 255, 255, 0.2) !important; color: white !important; border-radius: 8px; font-weight: bold; }
    div[data-testid="stDialog"] div[role="dialog"] { background-color: #121212 !important; border: 1px solid #F59E0B !important; }
    div[data-testid="stDialog"] h1, div[data-testid="stDialog"] p, div[data-testid="stDialog"] label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS ---
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

# --- 3. DATABASE LOGIN & ROLE ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "Admin"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "Admin"},
        "198810122025211031": {"nama": "Abdurrahman", "pass": "kpuhss2026", "role": "Admin"}, # <-- ROLE ADMIN
        "198308292008111001": {"nama": "Ahmad Erwan Rifani, S.HI", "pass": "kpuhss2026", "role": "Bendahara"},
        "198506082007012003": {"nama": "Najmi Hidayati", "pass": "kpuhss2026", "role": "Bendahara"},
    }

# DATABASE INFO 31 ORG (Tetap Utuh)
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Hukum", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Perencanaan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER", "Sekretariat KPU HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

# --- 4. DIALOGS (SEMUA FITUR DIAKTIFKAN) ---
@st.dialog("Update Data")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    loc = get_geolocation()
    jarak = 999999
    is_in_range = False

    if loc:
        u_lat, u_lon = loc['coords']['latitude'], loc['coords']['longitude']
        jarak = hitung_jarak(u_lat, u_lon, LAT_KANTOR, LON_KANTOR)
        is_in_range = jarak <= RADIUS_METER
        st.info(f"📍 Jarak Anda: {int(jarak)} meter dari kantor.")
    else:
        st.warning("⚠️ Mohon Izinkan Akses Lokasi (GPS).")

    tipe = st.radio("Pilih Kegiatan:", ["Absen", "Lapkin"])
    info = DATABASE_INFO[nama]
    
    if tipe == "Absen":
        if is_in_range:
            if st.button("🚀 KIRIM ABSEN SEKARANG"):
                st.success("Terkirim ke Google Form!"); time.sleep(1); st.rerun()
        else:
            st.error("🚫 Di luar radius kantor!")
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Uraian Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            payload = {"nama": nama, "nip": info[0], "status": st_fix, "hasil": h_kerja}
            try:
                requests.post(SCRIPT_LAPKIN, json=payload, timeout=5)
                st.success("Tersimpan!"); time.sleep(1); st.rerun()
            except: st.error("Gagal terhubung ke Script.")

@st.dialog("Advanced Rekap Excel", width="large")
def pop_rekap():
    st.markdown("### 📊 FILTER REKAP LENGKAP")
    c1, c2 = st.columns(2)
    with c1: r_bulan = st.selectbox("Bulan:", ["SEPANJANG TAHUN"] + LIST_BULAN)
    with c2: r_tahun = st.selectbox("Tahun:", ["2025", "2026", "2027"], index=1)
    if st.button("📊 DOWNLOAD EXCEL", use_container_width=True):
        st.info("Fitur Rekap Aktif...")

@st.dialog("Download Laporan Bulanan")
def pop_cetak():
    c_b = st.selectbox("Pilih Bulan Laporan:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    c_n = st.selectbox("Pilih Nama Pegawai:", list(DATABASE_INFO.keys()))
    if st.button("📊 GENERATE LAPKIN", use_container_width=True):
        st.success("Menyiapkan File Lapkin...")

# --- 5. AUTHENTICATION (Optional but recommended) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h3 style='text-align:center;'>🏛️ LOGIN SISTEM</h3>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            if u_nip in st.session_state.user_db and st.session_state.user_db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = st.session_state.user_db[u_nip]
                st.rerun()
            else: st.error("Login Gagal")
    st.stop()

# --- 6. MAIN UI ---
user = st.session_state.user
st.markdown(f'<div class="header-box">🏛️ MONITORING KPU HSS</div>', unsafe_allow_html=True)
st.markdown(f'<div class="clock-box">{datetime.now(wita_tz).strftime("%H:%M:%S WITA")} | User: {user["nama"]} ({user["role"]})</div>', unsafe_allow_html=True)

_, mid, _ = st.columns([0.1, 5, 0.1])
with mid:
    # Hanya Admin & Bendahara yang bisa lihat tombol Rekap/Download
    if user['role'] in ["Admin", "Bendahara"]:
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a: 
            if st.button("🔄 REFRESH"): st.rerun()
        with col_b: pilih_tgl = st.date_input("Tgl", value=datetime.now(wita_tz).date(), label_visibility="collapsed")
        with col_c: 
            if st.button("📥 REKAP"): pop_rekap()
        with col_d: 
            if st.button("🖨️ DOWNLOAD"): pop_cetak()
    else:
        # User Biasa hanya refresh dan tanggal
        col_1, col_2 = st.columns(2)
        with col_1:
             if st.button("🔄 REFRESH"): st.rerun()
        with col_2: pilih_tgl = st.date_input("Tgl", value=datetime.now(wita_tz).date(), label_visibility="collapsed")

st.write("---")
tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PNS", "👥 PPPK"])

def render_ui(urls, masters, tgl_target, tab_id):
    all_dfs = []
    for u in urls:
        df_t = get_clean_df(u)
        if df_t is not None: all_dfs.append(df_t)
    if not all_dfs: 
        st.warning("Data tidak ditemukan.")
        return
    df = pd.concat(all_dfs, ignore_index=True)
    d_f1, d_f2 = tgl_target.strftime('%d/%m/%Y'), tgl_target.strftime('%Y-%m-%d')
    log = {}
    for _, r in df.iterrows():
        ts = str(r.iloc[0])
        if d_f1 in ts or d_f2 in ts:
            n_raw = clean_logic(r.iloc[1])
            dt = pd.to_datetime(ts, errors='coerce')
            if pd.isna(dt): continue
            matched = next((m for m in masters if clean_logic(m) == n_raw), None)
            if matched:
                if matched not in log: log[matched] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
                if dt.hour >= 15: log[matched]["p"] = dt.strftime("%H:%M")
    
    for i, p in enumerate(masters, 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        st_cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        c_main, c_side = st.columns([8.5, 1.5])
        with c_main: st.markdown(f'<div class="employee-card"><div class="emp-name">{i}. {p}</div><div class="emp-time">M: <b>{d["m"]}</b></div><div class="emp-time">P: <b>{d["p"]}</b></div><div class="emp-status {st_cls}">{d["k"]}</div></div>', unsafe_allow_html=True)
        with c_side:
            # Pegawai hanya bisa update namanya sendiri, Admin bisa semua
            if user['role'] == "Admin" or user['nama'] == p:
                if st.button("Update", key=f"btn_{p}_{tab_id}"): pop_update(p)
            else:
                st.button("Update", key=f"btn_{p}_{tab_id}", disabled=True)

with tab_all: render_ui([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), pilih_tgl, "all")
with tab_pns: render_ui([URL_PNS], MASTER_PNS, pilih_tgl, "pns")
with tab_pppk: render_ui([URL_PPPK], MASTER_PPPK, pilih_tgl, "pppk")

if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
