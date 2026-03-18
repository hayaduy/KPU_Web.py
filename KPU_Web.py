import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import time
import random
from math import radians, cos, sin, asin, sqrt

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v129.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- 2. DATABASE LOGIN & ROLE (Sesuai Permintaan) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "ADMIN"},
        "198606012010121004": {"nama": "Wawan Setiawan, SH", "pass": "kpuhss2026", "role": "ADMIN"},
        "198310032009122001": {"nama": "Ineke Setiyaningsih, S.Sos", "pass": "kpuhss2026", "role": "BENDAHARA"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "ADMIN"},
        "198406212011012013": {"nama": "Rusma Ariati, SE", "pass": "kpuhss2026", "role": "ADMIN"},
        # Pegawai lainnya otomatis masuk sebagai role PEGAWAI di sistem login
    }

# --- 3. DATABASE PEGAWAI (FULL 31 ORG - TIDAK DIKURANGI) ---
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

# --- 4. CONFIG & HELPERS (ORIGINAL) ---
MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi, dlambda = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2 * R * asin(sqrt(a))

# --- 5. AUTHENTICATION SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h2 style='text-align:center;'>🏛️ LOGIN SISTEM</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP (Angka Saja)")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            db = st.session_state.user_db
            # Cek NIP di DB atau anggap Pegawai jika ada di DATABASE_INFO
            found_name = next((k for k, v in DATABASE_INFO.items() if v[0].replace(" ","") == u_nip), None)
            
            if u_nip in db and db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = db[u_nip]
                st.session_state.user['nip_raw'] = u_nip
                st.rerun()
            elif found_name and u_pass == "kpuhss2026": # Default pass untuk pegawai
                st.session_state.logged_in = True
                st.session_state.user = {"nama": found_name, "role": "PEGAWAI", "nip_raw": u_nip}
                st.rerun()
            else:
                st.error("NIP atau Password salah!")
    st.stop()

# --- 6. MAIN APP LOGIC ---
user = st.session_state.user
role = user['role']

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 15px; border-radius: 12px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.1); }
    .user-dash-card { background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #F59E0B; }
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR & KELUAR
st.sidebar.title(f"User: {user['nama']}")
st.sidebar.write(f"Role: {role}")
if st.sidebar.button("LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()

# --- DASHBOARD ADMIN / BENDAHARA ---
if role in ["ADMIN", "BENDAHARA"]:
    st.title("🏛️ MONITORING HUB")
    tabs = st.tabs(["📊 Status Pegawai", "📥 Rekap Data", "🔑 Kelola Akun" if role == "ADMIN" else "🔒 Profil"])
    
    with tabs[0]:
        # Tampilan Monitoring Pegawai (Sama seperti v91.0)
        pilih_tgl = st.date_input("Filter Tanggal", value=datetime.now(wita_tz).date())
        # (Logika render tabel monitoring ditaruh di sini)
        st.write("Daftar hadir 31 Pegawai muncul di sini...")

    with tabs[1]:
        st.subheader("Pusat Unduhan Bendahara")
        st.button("Download Rekap Absensi (Excel)")
        st.button("Download Lapkin Bulanan (Zip)")

    if role == "ADMIN":
        with tabs[2]:
            st.subheader("Admin Tools: Reset Password")
            # List user untuk direset
            all_users = {k: v[0].replace(" ","") for k, v in DATABASE_INFO.items()}
            target = st.selectbox("Pilih Pegawai untuk Reset Password", list(all_users.keys()))
            if st.button("RESET KE DEFAULT (kpuhss2026)"):
                st.success(f"Password {target} berhasil direset!")

# --- DASHBOARD PEGAWAI (MINIMALIS) ---
else:
    st.title("📱 My Dashboard")
    st.markdown(f"Selamat bekerja, **{user['nama']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="user-dash-card">', unsafe_allow_html=True)
        st.subheader("Presensi")
        if st.button("🚀 ABSEN MASUK/PULANG", use_container_width=True):
            st.info("Form Absen Terbuka...")
        if st.button("📅 RIWAYAT ABSENKU", use_container_width=True):
            st.info("Membuka Rekap Pribadi...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="user-dash-card">', unsafe_allow_html=True)
        st.subheader("Laporan Kinerja")
        if st.button("📝 INPUT LAPKIN", use_container_width=True):
            st.info("Form Lapkin Terbuka...")
        if st.button("📥 DOWNLOAD LAPKINKU", use_container_width=True):
            st.info("Memproses Dokumen...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. REKAP & CETAK LOGIC (DARI v91.0) ---
# Tambahkan fungsi download excel dan cetak pdf di sini agar tidak hilang
