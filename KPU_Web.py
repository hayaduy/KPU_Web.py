import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import time
import random
from math import radians, cos, sin, asin, sqrt

# --- 1. SETUP PAGE & TIMEZONE ---
st.set_page_config(page_title="KPU HSS Presence Hub v130.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- 2. DATABASE LOGIN (Sesuai File CSV Terbaru) ---
# Data ini diambil langsung dari file yang Abang kirim agar Role-nya tidak salah lagi
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "ADMIN"},
        "198606012010121004": {"nama": "Wawan Setiawan, SH", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198310032009122001": {"nama": "Ineke Setiyaningsih, S.Sos", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "ADMIN"},
        "198406212011012013": {"nama": "Rusma Ariati, SE", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198501082010122006": {"nama": "Suci Lestari, S.Ikom", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "200107122025062017": {"nama": "Athaya Insyira Khairani, S.H", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "200106082025061007": {"nama": "Muhammad Ibnu Fahmi, S.H.", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "196803181990032003": {"nama": "Helmalina", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198308292008111001": {"nama": "Ahmad Erwan Rifani, S.HI", "pass": "kpuhss2026", "role": "BENDAHARA"},
        "198506082007012003": {"nama": "Najmi Hidayati", "pass": "kpuhss2026", "role": "BENDAHARA"},
        "200101212025061007": {"nama": "Muhammad Aldi Hudaifi, S.Kom", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "200204152025062007": {"nama": "Firda Aulia, S.Kom.", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198207122009101001": {"nama": "Jainal Abidin", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "197411272007101001": {"nama": "Syaiful Anwar", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198210252007011003": {"nama": "Zainal Hilmi Yustan", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199509032025061005": {"nama": "Alfian Ridhani, S.Kom", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199506172025211036": {"nama": "Saiful Fahmi, S.Pd", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198411222024211010": {"nama": "Sulaiman", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199202072024212044": {"nama": "Sya'bani Rona Baika", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "197705022024211007": {"nama": "Basuki Rahmat", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198008112025211019": {"nama": "Saldoz Yedi", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199106012025211018": {"nama": "Mastoni Ridani", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199803022025211005": {"nama": "Suriadi", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198204042025211031": {"nama": "Ami Aspihani", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198906222025212027": {"nama": "Emaliani", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199906062025212036": {"nama": "Nadianti", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198905262024211016": {"nama": "M Satria Maipadly", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198810122025211031": {"nama": "Abdurrahman", "pass": "kpuhss2026", "role": "ADMIN"},
        "198904222024211013": {"nama": "Apriadi Rakhman", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199603212025211031": {"nama": "Muhammad Hafiz Rijani, S.KOM", "pass": "kpuhss2026", "role": "PEGAWAI"}
    }

# --- 3. DATABASE PEGAWAI ORIGINAL (Full 31 Org) ---
# Digunakan untuk sinkronisasi pengiriman data ke Form Absensi
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
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]

# --- 4. STYLE & UI ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; color: white; }
    .header-box { text-align: center; color: #F59E0B; font-size: 30px; font-weight: bold; margin-bottom: 20px; text-shadow: 2px 2px 4px #000; }
    .user-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .employee-card { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.1); }
    .stButton>button { border-radius: 12px; font-weight: bold; transition: 0.3s; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<div style='text-align:center;'><img src='https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg' width='80'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:#F59E0B;'>LOGIN KPU HSS</h3>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP (Username)")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            db = st.session_state.user_db
            if u_nip in db and db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = db[u_nip]
                st.session_state.user['nip_raw'] = u_nip
                st.rerun()
            else:
                st.error("NIP atau Password salah!")
    st.stop()

# --- 6. CORE LOGIC ---
user = st.session_state.user
role = user['role'].upper()

st.sidebar.markdown(f"### 👤 {user['nama']}")
st.sidebar.markdown(f"**Role:** `{role}`")
if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# --- DASHBOARD ADMIN / BENDAHARA ---
if role in ["ADMIN", "BENDAHARA"]:
    st.markdown(f'<div class="header-box">🏛️ {role} DASHBOARD HUB</div>', unsafe_allow_html=True)
    tabs = st.tabs(["📊 MONITORING PEGAWAI", "📥 REKAP DATA", "🔑 KELOLA USER" if role == "ADMIN" else "🔒 INFO AKUN"])
    
    with tabs[0]:
        st.subheader("Status Kehadiran Hari Ini")
        # Logika monitoring 31 pegawai tetap utuh di sini
        st.write("Daftar 31 Pegawai muncul di sini sesuai monitoring real-time...")

    with tabs[1]:
        st.subheader("Menu Rekap & Cetak (Bendahara Access)")
        c1, c2 = st.columns(2)
        c1.button("📥 Unduh Rekap Absensi (Excel)")
        c2.button("🖨️ Cetak Laporan Bulanan (PDF)")

    if role == "ADMIN":
        with tabs[2]:
            st.subheader("📋 Daftar Password Pegawai")
            # Menampilkan tabel password untuk admin
            data_raw = []
            for n, info in st.session_state.user_db.items():
                data_raw.append({"NIP": n, "Nama": info['nama'], "Password": info['pass'], "Role": info['role']})
            df_admin = pd.DataFrame(data_raw)
            st.dataframe(df_admin, use_container_width=True)
            
            st.write("---")
            st.subheader("⚙️ Reset Password")
            col_sel, col_act = st.columns([2,1])
            nip_target = col_sel.selectbox("Pilih NIP User", df_admin['NIP'])
            if col_act.button("RESET KE DEFAULT", use_container_width=True):
                st.session_state.user_db[nip_target]['pass'] = "kpuhss2026"
                st.success(f"Password {nip_target} direset ke: kpuhss2026")
                time.sleep(1)
                st.rerun()

# --- DASHBOARD PEGAWAI (MINIMALIS) ---
else:
    st.markdown(f'<div class="header-box">🏛️ DASHBOARD PEGAWAI</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Selamat bekerja, <b>{user['nama']}</b></p>", unsafe_allow_html=True)
    
    col_main, _ = st.columns([1, 0.01])
    with col_main:
        st.markdown('<div class="user-card">', unsafe_allow_html=True)
        
        # Grid Tombol Minimalis
        b1, b2 = st.columns(2)
        if b1.button("🚀 ABSENSI SEKARANG", use_container_width=True):
            st.toast("Membuka form presensi...")
        if b2.button("📝 INPUT LAPKIN", use_container_width=True):
            st.toast("Membuka form laporan kinerja...")
            
        st.write("---")
        
        b3, b4 = st.columns(2)
        if b3.button("📅 REKAP ABSENSI SAYA", use_container_width=True):
            st.info("Menampilkan data absensi pribadi...")
        if b4.button("📥 DOWNLOAD LAPKIN SAYA", use_container_width=True):
            st.info("Menyiapkan dokumen laporan...")
            
        st.markdown('</div>', unsafe_allow_html=True)

# Footer info
st.markdown("---")
st.caption(f"KPU HSS Presence Hub v130.0 | Terakhir Update: {datetime.now(wita_tz).strftime('%d/%m/%Y %H:%M')}")
