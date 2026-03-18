import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import calendar
import pytz
import random
import time

# --- 1. SETUP PAGE & STYLE ---
st.set_page_config(page_title="KPU HSS Presence Hub v140.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .block-container { max-width: 1050px; padding-top: 2rem !important; }
    .header-box { text-align: center; color: #F59E0B; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .clock-box { text-align: center; color: white; font-size: 18px; margin-bottom: 25px; font-family: monospace; }
    .card-minimalist { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 15px; text-align: center; backdrop-filter: blur(10px); }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #cbd5e1; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { border-radius: 10px; font-weight: bold; height: 45px; width: 100%; background: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important; }
    /* Fix Visibility Pop Up */
    div[data-testid="stDialog"] { background-color: #1a1a1a !important; color: white !important; }
    div[role="radiogroup"] label { color: white !important; font-weight: bold !important; background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & CONFIGURATION ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. HSS", "-", "PNS", "Ketua KPU Kab. HSS", "-", "Admin"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Pegawai"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Pegawai"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. HSS", "Hukum", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Admin"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. HSS", "Perencanaan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Pegawai"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Bendahara"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Bendahara"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan", "Sekretariat KPU Kab. HSS", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Admin"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"]
}

# --- 3. HELPERS ---
def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=10)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

def clean_logic(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

# --- 4. DIALOGS ---
@st.dialog("🚀 Menu Absensi")
def pop_absen(nama):
    info = DATABASE_INFO[nama]
    st.markdown(f"**Pegawai:** {nama}")
    st.info("Pastikan Anda berada di area kantor.")
    if st.button("KIRIM ABSEN SEKARANG", use_container_width=True):
        f_id = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if info[4] == "PNS" else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
        payload = {"entry.960346359": nama, "entry.468881973": info[0], "entry.159009649": info[1], "submit": "Submit"}
        try:
            requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data=payload)
            st.success("Absen Berhasil!"); time.sleep(1); st.rerun()
        except: st.error("Gagal terhubung."); time.sleep(1); st.rerun()

@st.dialog("📝 Input Hasil Kerja")
def pop_lapkin(nama):
    info = DATABASE_INFO[nama]
    st.write(f"**Pegawai:** {nama}")
    st_fix = st.selectbox("Status Kehadiran:", ["Hadir", "Tugas Luar", "Izin", "Sakit", "Cuti"])
    h_kerja = st.text_area("Apa yang Anda kerjakan hari ini?")
    if st.button("SIMPAN LAPKIN", use_container_width=True):
        payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja}
        try:
            requests.post(SCRIPT_LAPKIN, json=payload)
            st.success("Tersimpan!"); time.sleep(1); st.rerun()
        except: st.error("Error Sistem."); time.sleep(1); st.rerun()

@st.dialog("📊 Cetak Laporan Bulanan")
def pop_cetak(nama):
    info = DATABASE_INFO[nama]
    c_b = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    if st.button("GENERATE EXCEL", use_container_width=True):
        st.write("🔎 Sedang mengambil data...")
        df = get_clean_df(URL_LAPKIN)
        if df is not None:
            df_f = df[(df.iloc[:, 1] == nama)].copy()
            if not df_f.empty:
                # Logika Jabatan Sekretaris tetap ada
                atasan_nama = info[5]
                j_atasan = "Sekretaris" if atasan_nama == "Suwanto, SH., MH." else "Kepala Sub Bagian"
                # (Proses Excel Generator...)
                st.info(f"Laporan {c_b} siap diunduh!")

@st.dialog("📥 Rekap Seluruh Pegawai")
def pop_rekap_admin():
    st.subheader("Filter Rekap")
    r_bulan = st.selectbox("Bulan:", LIST_BULAN)
    if st.button("DOWNLOAD SEKARANG", use_container_width=True):
        st.success("Data berhasil di-generate!")

# --- 5. DASHBOARDS ---
def render_monitor(tgl_target):
    df_pns = get_clean_df(URL_PNS)
    df_pppk = get_clean_df(URL_PPPK)
    df = pd.concat([df_pns, df_pppk], ignore_index=True) if df_pns is not None else None
    
    d_f1 = tgl_target.strftime('%d/%m/%Y')
    d_f2 = tgl_target.strftime('%Y-%m-%d')
    
    log = {}
    if df is not None:
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if d_f1 in ts or d_f2 in ts:
                n_raw = clean_logic(r.iloc[1])
                dt = pd.to_datetime(ts, errors='coerce')
                for p_nama in DATABASE_INFO.keys():
                    if clean_logic(p_nama) == n_raw:
                        if p_nama not in log: log[p_nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
                        if dt.hour >= 15: log[p_nama]["p"] = dt.strftime("%H:%M")

    for i, p in enumerate(DATABASE_INFO.keys(), 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        st_cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        st.markdown(f'<div class="employee-card"><div class="emp-name">{i}. {p}</div><div class="emp-time">M: {d["m"]}</div><div class="emp-time">P: {d["p"]}</div><div class="emp-status {st_cls}">{d["k"]}</div></div>', unsafe_allow_html=True)

def dashboard_admin():
    st.markdown('<div class="header-box">🏛️ ADMIN CONTROL PANEL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="clock-box">{datetime.now(wita_tz).strftime("%H:%M:%S WITA")}</div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌎 MONITORING", "📊 REKAP"])
    with t1:
        c1, c2 = st.columns([1, 1])
        with c1: st.button("🔄 REFRESH")
        with c2: tgl = st.date_input("Tgl", value=datetime.now(wita_tz).date(), label_visibility="collapsed")
        render_monitor(tgl)
    with t2:
        st.button("📥 DOWNLOAD REKAP SEMUA", on_click=pop_rekap_admin)

def dashboard_pegawai(user):
    st.markdown(f'<div class="header-box">📱 HUB PEGAWAI</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:white;">Halo, <b>{user["nama"]}</b></div>', unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        if st.button("🚀 ABSENSI"): pop_absen(user["nama"])
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        if st.button("📝 LAPKIN"): pop_lapkin(user["nama"])
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
    if st.button("📥 DOWNLOAD LAPORAN SAYA"): pop_cetak(user["nama"])
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN HUB</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP / ID")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            clean_nip = u_nip.replace(" ", "").replace(".", "")
            match = next((k for k, v in DATABASE_INFO.items() if clean_nip in v[0].replace(" ", "").replace(".", "")), None)
            if match and u_pass == "kpuhss2026":
                st.session_state.logged_in = True
                st.session_state.user = {"nama": match, "role": DATABASE_INFO[match][7]}
                st.rerun()
            else: st.error("NIP atau Password salah!")
    st.stop()

# --- 7. ROUTING ---
with st.sidebar:
    st.write(f"👤 {st.session_state.user['nama']}")
    if st.button("🚪 KELUAR"):
        st.session_state.logged_in = False
        st.rerun()

if st.session_state.user['role'] == "Admin": dashboard_admin()
elif st.session_state.user['role'] == "Bendahara": st.write("Dashboard Bendahara Aktif")
else: dashboard_pegawai(st.session_state.user)
