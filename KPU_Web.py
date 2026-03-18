import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import random

# --- 1. SETUP & STYLE ---
st.set_page_config(page_title="KPU HSS Presence Hub v141.0", layout="wide")
wita_tz = pytz.timezone('Asia/Makassar')

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .employee-card { background: rgba(255, 255, 255, 0.07); padding: 12px 20px; border-radius: 10px; display: flex; align-items: center; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.5; color: #cbd5e1; text-align: center; font-size: 12px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 12px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .header-box { text-align: center; color: #F59E0B; font-size: 28px; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE (31 PEGAWAI) ---
# (Tetap menggunakan DATABASE_INFO yang sama seperti sebelumnya untuk menjaga struktur 31 orang)
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

# --- 3. CORE FUNCTIONS ---
def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=10)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

def clean_name(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

def render_monitor(tgl_target):
    # Ambil data dari Sheets
    url_pns = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
    url_pppk = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
    
    df1, df2 = get_clean_df(url_pns), get_clean_df(url_pppk)
    df_all = pd.concat([df1, df2], ignore_index=True) if df1 is not None else None
    
    log = {}
    if df_all is not None:
        t_str1 = tgl_target.strftime('%d/%m/%Y')
        t_str2 = tgl_target.strftime('%Y-%m-%d')
        
        for _, row in df_all.iterrows():
            ts = str(row.iloc[0])
            if t_str1 in ts or t_str2 in ts:
                n_csv = clean_name(row.iloc[1])
                dt = pd.to_datetime(ts, errors='coerce')
                if pd.isna(dt): continue
                
                for p_real in DATABASE_INFO.keys():
                    if clean_name(p_real) == n_csv:
                        if p_real not in log:
                            status = "HADIR" if dt.hour < 9 else "TERLAMBAT"
                            log[p_real] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": status}
                        if dt.hour >= 15:
                            log[p_real]["p"] = dt.strftime("%H:%M")

    # TAMPILKAN DAFTAR 31 PEGAWAI (PASTI MUNCUL)
    st.write(f"📊 **Data Kehadiran: {tgl_target.strftime('%d %B %Y')}**")
    for i, p in enumerate(DATABASE_INFO.keys(), 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        
        st.markdown(f"""
            <div class="employee-card">
                <div class="emp-name">{i}. {p}</div>
                <div class="emp-time">Masuk: <b>{d['m']}</b></div>
                <div class="emp-time">Pulang: <b>{d['p']}</b></div>
                <div class="emp-status {cls}">{d['k']}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 4. DASHBOARDS ---
def dashboard_admin():
    st.markdown('<div class="header-box">🏛️ DASHBOARD ADMIN</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 REFRESH DATA"): st.rerun()
    with col2:
        tgl = st.date_input("Pilih Tanggal", value=datetime.now(wita_tz).date())
    
    st.write("---")
    render_monitor(tgl)

def dashboard_pegawai(user):
    st.markdown('<div class="header-box">📱 HUB PEGAWAI</div>', unsafe_allow_html=True)
    st.write(f"Selamat bekerja, **{user['nama']}**")
    # Menu Absen & Lapkin (Simple)
    if st.button("🚀 KIRIM ABSENSI"): st.success("Fitur Absen Aktif!")
    if st.button("📝 ISI LAPORAN KERJA"): st.info("Form Lapkin Aktif!")

# --- 5. LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            clean_in = u_nip.replace(" ", "").replace(".", "")
            match = next((k for k, v in DATABASE_INFO.items() if clean_in in v[0].replace(" ", "").replace(".", "")), None)
            if match and u_pass == "kpuhss2026":
                st.session_state.logged_in = True
                st.session_state.user = {"nama": match, "role": DATABASE_INFO[match][7]}
                st.rerun()
            else: st.error("NIP atau Password salah!")
    st.stop()

# --- 6. ROUTING ---
if st.session_state.user['role'] == "Admin": dashboard_admin()
else: dashboard_pegawai(st.session_state.user)

if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
