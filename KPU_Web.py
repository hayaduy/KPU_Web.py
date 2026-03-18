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
st.set_page_config(page_title="KPU HSS Presence Hub v138.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .block-container { max-width: 1000px; padding-top: 2rem !important; }
    .header-box { text-align: center; color: #F59E0B; font-size: 28px; font-weight: bold; margin-bottom: 5px; }
    .user-info { text-align: center; color: #cbd5e1; font-size: 14px; margin-bottom: 20px; }
    .card-minimalist { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 15px; text-align: center; }
    .stButton>button { border-radius: 10px; font-weight: bold; height: 45px; width: 100%; }
    .admin-label { background: #7f1d1d; color: #fecaca; padding: 2px 8px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & SESSION ---
if 'user_db' not in st.session_state:
    # Database awal dengan Role yang sudah disesuaikan
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "Admin"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "Admin"},
        "198810122025211031": {"nama": "Abdurrahman", "pass": "kpuhss2026", "role": "Admin"},
        "198308292008111001": {"nama": "Ahmad Erwan Rifani, S.HI", "pass": "kpuhss2026", "role": "Bendahara"},
        "198506082007012003": {"nama": "Najmi Hidayati", "pass": "kpuhss2026", "role": "Bendahara"},
    }

# Data Master Pegawai (31 Orang)
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan", "PNS"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "PPPK"],
    # ... (Tambahkan 31 nama lainnya di sini sesuai list sebelumnya)
}

# --- 3. FUNGSI DASHBOARD ---

def menu_pegawai_minimalis(user):
    """Tampilan Dashboard untuk Pegawai Biasa"""
    st.markdown(f"<div class='header-box'>📱 HUB PEGAWAI</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='user-info'>Selamat bekerja, <b>{user['nama']}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        if st.button("🚀 ABSEN SEKARANG"): pop_update(user['nama'], "Absen")
        st.caption("Gunakan GPS di area kantor")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        if st.button("📅 REKAP SAYA"): st.info(f"Menampilkan rekap untuk: {user['nama']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        if st.button("📝 LAPKIN KHUSUS"): pop_update(user['nama'], "Lapkin")
        st.caption("Input laporan kinerja harian")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card-minimalist'>", unsafe_allow_html=True)
        if st.button("📥 DOWNLOAD LAPKIN"): st.info(f"Download file {user['nama']}.xlsx")
        st.markdown("</div>", unsafe_allow_html=True)

def dashboard_admin():
    """Tampilan Full Akses untuk Admin"""
    st.title("🏛️ ADMIN CONTROL CENTER")
    tabs = st.tabs(["📊 MONITORING", "🔑 KELOLA USER", "📥 REKAP & DOWNLOAD"])
    
    with tabs[0]:
        st.subheader("Status Presensi Real-time (31 Pegawai)")
        # Tambahkan fungsi render_ui monitoring di sini
        
    with tabs[1]:
        st.subheader("Manajemen Pengguna & Password")
        # FITUR: LIHAT PASSWORD & RESET
        data_user = []
        for nip, val in st.session_state.user_db.items():
            data_user.append({"NIP": nip, "Nama": val['nama'], "Password": val['pass'], "Role": val['role']})
        df_u = pd.DataFrame(data_user)
        st.dataframe(df_u, use_container_width=True)
        
        with st.expander("➕ Tambah/Update Role Admin Baru"):
            new_nip = st.text_input("Masukkan NIP")
            new_role = st.selectbox("Pilih Role", ["Admin", "Bendahara", "Pegawai"])
            if st.button("SIMPAN PERUBAHAN"):
                if new_nip in st.session_state.user_db:
                    st.session_state.user_db[new_nip]['role'] = new_role
                    st.success(f"NIP {new_nip} sekarang adalah {new_role}")
                else: st.error("NIP tidak terdaftar di database utama.")

    with tabs[2]:
        col1, col2 = st.columns(2)
        with col1: st.button("📊 REKAP SEMUA PEGAWAI")
        with col2: st.button("🖨️ CETAK SEMUA LAPORAN")

def dashboard_bendahara():
    """Tampilan Sub-Admin untuk Bendahara"""
    st.title("💰 DASHBOARD BENDAHARA")
    st.info("Akses terbatas: Monitoring & Rekap Absensi")
    tabs = st.tabs(["📊 MONITORING PRESENSI", "📥 REKAP ABSENSI"])
    
    with tabs[0]:
        st.write("Daftar kehadiran pegawai hari ini...")
    with tabs[1]:
        st.write("Download rekap absensi bulanan untuk penggajian...")

# --- 4. LOGIKA LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP (Username)")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            db = st.session_state.user_db
            if u_nip in db and db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = db[u_nip]
                st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# --- 5. ROUTING DASHBOARD ---
user = st.session_state.user

# Sidebar untuk Logout & Info Singkat
with st.sidebar:
    st.markdown(f"### 👤 {user['nama']}")
    st.markdown(f"Role: `{user['role']}`")
    if st.button("🚪 KELUAR"):
        st.session_state.logged_in = False
        st.rerun()

# Cek Role dan Tampilkan Dashboard yang sesuai
if user['role'] == "Admin":
    dashboard_admin()
elif user['role'] == "Bendahara":
    dashboard_bendahara()
else:
    menu_pegawai_minimalis(user)

# --- 6. DIALOGS (ABSEN/LAPKIN) ---
@st.dialog("Sistem Input")
def pop_update(nama, tipe):
    st.subheader(f"{tipe} - {nama}")
    if tipe == "Absen":
        loc = get_geolocation()
        if loc:
            st.success("Lokasi Terdeteksi. Anda bisa absen.")
            if st.button("KIRIM SEKARANG"): st.rerun()
        else: st.warning("Menunggu GPS...")
    else:
        st.text_area("Uraian Hasil Kerja")
        st.button("SIMPAN LAPORAN")
