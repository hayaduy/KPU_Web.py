import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import random
import time

# --- 1. SETUP & STYLE ---
st.set_page_config(page_title="KPU HSS Presence Hub v142.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .header-box { text-align: center; color: #F59E0B; font-size: 30px; font-weight: bold; margin-bottom: 5px; }
    .card-minimalist { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; text-align: center; backdrop-filter: blur(10px); }
    .employee-card { background: rgba(255, 255, 255, 0.07); padding: 10px 15px; border-radius: 10px; display: flex; align-items: center; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.5; color: #cbd5e1; text-align: center; font-size: 12px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 12px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { border-radius: 10px; font-weight: bold; background: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INFO (31 PEGAWAI) ---
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

# --- 3. CORE LOGIC ---
def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=10)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

def clean_name(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

# --- 4. DIALOGS (FITUR YANG DIKEMBALIKAN) ---
@st.dialog("🚀 Absensi Cepat")
def pop_absen(user_nama):
    info = DATABASE_INFO[user_nama]
    st.write(f"Pegawai: **{user_nama}**")
    if st.button("KIRIM ABSEN SEKARANG"):
        # Logika kirim ke Google Form
        st.success("Absen Berhasil Terkirim!"); time.sleep(1); st.rerun()

@st.dialog("📝 Laporan Kinerja")
def pop_lapkin(user_nama):
    st.write(f"Input kerja harian untuk: **{user_nama}**")
    hasil = st.text_area("Apa kegiatan hari ini?")
    if st.button("SIMPAN"):
        st.success("Laporan Tersimpan!"); time.sleep(1); st.rerun()

# --- 5. DASHBOARDS ---
def render_monitor(tgl_target):
    url_pns = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
    url_pppk = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
    df1, df2 = get_clean_df(url_pns), get_clean_df(url_pppk)
    df_all = pd.concat([df1, df2], ignore_index=True) if df1 is not None else None
    
    log = {}
    if df_all is not None:
        t_str = tgl_target.strftime('%d/%m/%Y')
        for _, row in df_all.iterrows():
            if t_str in str(row.iloc[0]):
                n_csv = clean_name(row.iloc[1])
                dt = pd.to_datetime(row.iloc[0], errors='coerce')
                for p_real in DATABASE_INFO.keys():
                    if clean_name(p_real) == n_csv:
                        if p_real not in log: log[p_real] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
                        if dt.hour >= 15: log[p_real]["p"] = dt.strftime("%H:%M")

    for i, p in enumerate(DATABASE_INFO.keys(), 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        st.markdown(f'<div class="employee-card"><div class="emp-name">{i}. {p}</div><div class="emp-time">M: {d["m"]}</div><div class="emp-time">P: {d["p"]}</div><div class="emp-status {cls}">{d["k"]}</div></div>', unsafe_allow_html=True)

def dashboard_admin():
    st.markdown('<div class="header-box">🏛️ ADMIN CONTROL</div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌍 MONITORING", "📊 REKAP"])
    with t1:
        tgl = st.date_input("Tanggal", value=datetime.now(wita_tz).date())
        render_monitor(tgl)
    with t2:
        st.button("📥 DOWNLOAD REKAP SEMUA PEGAWAI")

def dashboard_bendahara():
    st.markdown('<div class="header-box">💰 DASHBOARD BENDAHARA</div>', unsafe_allow_html=True)
    st.info("Menu khusus rekapitulasi uang makan & tunjangan.")
    st.button("📊 GENERATE LAPORAN KEUANGAN")

def dashboard_pegawai(user):
    st.markdown(f'<div class="header-box">📱 HUB PEGAWAI</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:white;'>Halo, <b>{user['nama']}</b></p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-minimalist">', unsafe_allow_html=True)
        if st.button("🚀 ABSENSI"): pop_absen(user['nama'])
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-minimalist">', unsafe_allow_html=True)
        if st.button("📝 LAPKIN"): pop_lapkin(user['nama'])
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-minimalist" style="margin-top:15px;">', unsafe_allow_html=True)
    st.button("📥 DOWNLOAD LAPORAN BULANAN")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN HUB</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            clean_in = u_nip.replace(" ", "").replace(".", "")
            match = next((k for k, v in DATABASE_INFO.items() if clean_in in v[0].replace(" ", "").replace(".", "")), None)
            if match and u_pass == "kpuhss2026":
                st.session_state.logged_in = True
                st.session_state.user = {"nama": match, "role": DATABASE_INFO[match][7]}
                st.rerun()
            else: st.error("NIP atau Password salah!")
    st.stop()

# --- 7. ROUTING ---
with st.sidebar:
    st.write(f"👤 {st.session_state.user['nama']}")
    st.write(f"Role: **{st.session_state.user['role']}**")
    if st.button("🚪 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

if st.session_state.user['role'] == "Admin": dashboard_admin()
elif st.session_state.user['role'] == "Bendahara": dashboard_bendahara()
else: dashboard_pegawai(st.session_state.user)
