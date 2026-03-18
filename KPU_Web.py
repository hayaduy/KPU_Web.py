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

# --- 1. SETUP PAGE & STYLE ---
st.set_page_config(page_title="KPU HSS Presence Hub v139.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. NYAWA APLIKASI: DATABASE 31 PEGAWAI ---
if 'user_db' not in st.session_state:
    # Role & Password Storage
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "Admin"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "Admin"},
        "198810122025211031": {"nama": "Abdurrahman", "pass": "kpuhss2026", "role": "Admin"},
        "198308292008111001": {"nama": "Ahmad Erwan Rifani, S.HI", "pass": "kpuhss2026", "role": "Bendahara"},
        "198506082007012003": {"nama": "Najmi Hidayati", "pass": "kpuhss2026", "role": "Bendahara"},
    }

DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. HSS", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. HSS", "Hukum", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. HSS", "Perencanaan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum", "Sekretariat KPU Kab. HSS", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan", "Sekretariat KPU Kab. HSS", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]

# --- 3. DASHBOARDS ---

def dashboard_admin():
    st.markdown('<div class="header-box">🏛️ ADMIN CONTROL PANEL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="clock-box">{datetime.now(wita_tz).strftime("%H:%M:%S WITA")}</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🌎 MONITORING", "👥 KELOLA USER", "📊 REKAP & CETAK"])
    
    with tabs[0]:
        st.write("---")
        col_ref, col_date = st.columns([1, 1])
        with col_ref: st.button("🔄 REFRESH DATA")
        with col_date: tgl = st.date_input("Pilih Tanggal", value=datetime.now(wita_tz).date())
        # Render UI Monitoring 31 Pegawai
        st.info("Menampilkan status kehadiran seluruh pegawai...")

    with tabs[1]:
        st.subheader("🔑 Kelola Password & Role")
        data_user = []
        for nip, val in st.session_state.user_db.items():
            data_user.append({"NIP": nip, "Nama": val['nama'], "Password": val['pass'], "Role": val['role']})
        
        df_users = pd.DataFrame(data_user)
        st.table(df_users)
        
        with st.expander("🛠️ Tambah/Ubah Admin Baru"):
            target_nip = st.text_input("Masukkan NIP Pegawai")
            new_role = st.selectbox("Tentukan Role", ["Admin", "Bendahara", "Pegawai"])
            new_pass = st.text_input("Reset Password (Opsional)")
            if st.button("UPDATE AKSES"):
                # Logika Update Role/Password di session
                st.success("Akses berhasil diperbarui!")

    with tabs[2]:
        st.subheader("📊 Laporan Seluruh Pegawai")
        col1, col2 = st.columns(2)
        with col1: st.button("📥 DOWNLOAD REKAP EXCEL")
        with col2: st.button("🖨️ CETAK SEMUA LAPKIN")

def dashboard_bendahara():
    st.markdown('<div class="header-box">💰 DASHBOARD BENDAHARA</div>', unsafe_allow_html=True)
    tabs = st.tabs(["📊 MONITORING ABSENSI", "📥 REKAP BULANAN"])
    with tabs[0]:
        st.info("Melihat kehadiran untuk keperluan uang makan/tunjangan.")
    with tabs[1]:
        st.button("📊 DOWNLOAD REKAP SELURUH PEGAWAI")

def dashboard_pegawai(user):
    st.markdown(f'<div class="header-box">📱 HUB PEGAWAI</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-info" style="text-align:center; color:white;">Selamat Bekerja, <b>{user["nama"]}</b></div>', unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        st.button("🚀 ABSENSI", on_click=lambda: st.toast("Membuka GPS..."))
        st.caption("Klik untuk absen masuk/pulang")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        st.button("📊 REKAP SAYA")
        st.caption("Lihat kehadiran pribadi")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        st.button("📝 LAPKIN")
        st.caption("Input hasil kerja harian")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        st.button("📥 DOWNLOAD")
        st.caption("Unduh laporan bulanan")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN HUB</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            # Cek di database login
            db = st.session_state.user_db
            if u_nip in db and db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = db[u_nip]
                st.rerun()
            # Jika NIP ada di 31 orang tapi belum punya role khusus (Default Pegawai)
            elif any(u_nip.replace(" ", "") in v[0].replace(" ", "") for v in DATABASE_INFO.values()):
                # Cari nama berdasarkan NIP
                nama_found = next(k for k, v in DATABASE_INFO.items() if u_nip.replace(" ", "") in v[0].replace(" ", ""))
                if u_pass == "kpuhss2026":
                    st.session_state.logged_in = True
                    st.session_state.user = {"nama": nama_found, "role": "Pegawai", "pass": "kpuhss2026"}
                    st.rerun()
            else:
                st.error("NIP atau Password salah!")
    st.stop()

# --- 5. APP ROUTING ---
user = st.session_state.user

with st.sidebar:
    st.markdown(f"### 👤 {user['nama']}")
    st.markdown(f"Role: **{user['role']}**")
    if st.button("🚪 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

if user['role'] == "Admin":
    dashboard_admin()
elif user['role'] == "Bendahara":
    dashboard_bendahara()
else:
    dashboard_pegawai(user)
