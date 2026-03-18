import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import time
from math import radians, cos, sin, asin, sqrt

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v136.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- 2. DATABASE LOGIN (FIXED: ABDURRAHMAN = ADMIN) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "Admin"},
        "198606012010121004": {"nama": "Wawan Setiawan, SH", "pass": "kpuhss2026", "role": "Pegawai"},
        "198310032009122001": {"nama": "Ineke Setiyaningsih, S.Sos", "pass": "kpuhss2026", "role": "Pegawai"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "Admin"},
        "198406212011012013": {"nama": "Rusma Ariati, SE", "pass": "kpuhss2026", "role": "Pegawai"},
        "198501082010122006": {"nama": "Suci Lestari, S.Ikom", "pass": "kpuhss2026", "role": "Pegawai"},
        "200107122025062017": {"nama": "Athaya Insyira Khairani, S.H", "pass": "kpuhss2026", "role": "Pegawai"},
        "200106082025061007": {"nama": "Muhammad Ibnu Fahmi, S.H.", "pass": "kpuhss2026", "role": "Pegawai"},
        "196803181990032003": {"nama": "Helmalina", "pass": "kpuhss2026", "role": "Pegawai"},
        "198308292008111001": {"nama": "Ahmad Erwan Rifani, S.HI", "pass": "kpuhss2026", "role": "Bendahara"},
        "198506082007012003": {"nama": "Najmi Hidayati", "pass": "kpuhss2026", "role": "Bendahara"},
        "200101212025061007": {"nama": "Muhammad Aldi Hudaifi, S.Kom", "pass": "kpuhss2026", "role": "Pegawai"},
        "200204152025062007": {"nama": "Firda Aulia, S.Kom.", "pass": "kpuhss2026", "role": "Pegawai"},
        "198207122009101001": {"nama": "Jainal Abidin", "pass": "kpuhss2026", "role": "Pegawai"},
        "197411272007101001": {"nama": "Syaiful Anwar", "pass": "kpuhss2026", "role": "Pegawai"},
        "198210252007011003": {"nama": "Zainal Hilmi Yustan", "pass": "kpuhss2026", "role": "Pegawai"},
        "199509032025061005": {"nama": "Alfian Ridhani, S.Kom", "pass": "kpuhss2026", "role": "Pegawai"},
        "199506172025211036": {"nama": "Saiful Fahmi, S.Pd", "pass": "kpuhss2026", "role": "Pegawai"},
        "198411222024211010": {"nama": "Sulaiman", "pass": "kpuhss2026", "role": "Pegawai"},
        "199202072024212044": {"nama": "Sya'bani Rona Baika", "pass": "kpuhss2026", "role": "Pegawai"},
        "197705022024211007": {"nama": "Basuki Rahmat", "pass": "kpuhss2026", "role": "Pegawai"},
        "198008112025211019": {"nama": "Saldoz Yedi", "pass": "kpuhss2026", "role": "Pegawai"},
        "199106012025211018": {"nama": "Mastoni Ridani", "pass": "kpuhss2026", "role": "Pegawai"},
        "199803022025211005": {"nama": "Suriadi", "pass": "kpuhss2026", "role": "Pegawai"},
        "198204042025211031": {"nama": "Ami Aspihani", "pass": "kpuhss2026", "role": "Pegawai"},
        "198906222025212027": {"nama": "Emaliani", "pass": "kpuhss2026", "role": "Pegawai"},
        "199906062025212036": {"nama": "Nadianti", "pass": "kpuhss2026", "role": "Pegawai"},
        "198905262024211016": {"nama": "M Satria Maipadly", "pass": "kpuhss2026", "role": "Pegawai"},
        "198810122025211031": {"nama": "Abdurrahman", "pass": "kpuhss2026", "role": "Admin"}, # <-- SUDAH ADMIN
        "198904222024211013": {"nama": "Apriadi Rakhman", "pass": "kpuhss2026", "role": "Pegawai"},
        "199603212025211031": {"nama": "Muhammad Hafiz Rijani, S.KOM", "pass": "kpuhss2026", "role": "Pegawai"}
    }

# --- 3. DATABASE PEGAWAI UTUH (31 DATA LENGKAP) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-", "https://docs.google.com/forms/d/e/1FAIpQLScP_7FpL-kI8hPj7-T9PzFjD-S_g7zO6_R1_R2_R3_R4_R5/viewform"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "https://docs.google.com/forms/d/e/1FAIpSclK7T0-R8S_v_Fm-V27Z2qG5WzX9J9"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "link_form_ineke"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Hukum", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "link_form_farah"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Perencanaan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "link_form_rusma"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "link_form_suci"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "link_form_athaya"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "link_form_ibnu"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_helmalina"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_erwan"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_najmi"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_aldi"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_firda"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "link_form_jainal"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "link_form_syaiful"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "link_form_hilmi"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "link_form_alfian"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "link_form_fami"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "link_form_sulaiman"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_sabani"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_basuki"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_saldoz"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_mastoni"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_suriadi"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_ami"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_emaliani"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI", "Sekretariat KPU HSS", "Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "link_form_nadianti"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "link_form_satria"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "Sekretariat KPU HSS", "Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "link_form_abdur"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER", "Sekretariat KPU HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "link_form_apri"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU", "Sekretariat KPU HSS", "Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "link_form_hafiz"]
}

# --- 4. CONFIG & HELPERS ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi, dlambda = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2 * R * asin(sqrt(a))

# --- 5. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h3 style='text-align:center; color:#F59E0B;'>🏛️ KPU HSS LOGIN</h3>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP (Username)")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            db = st.session_state.user_db
            if u_nip in db and db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = db[u_nip]
                st.rerun()
            else: st.error("NIP atau Password salah!")
    st.stop()

# --- 6. CORE APP ---
user = st.session_state.user
role = user['role']

st.sidebar.markdown(f"### 👤 {user['nama']}\nRole: **{role}**")
if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# FUNGSI MENU PEGAWAI (ABSEN/LAPKIN)
def render_menu_pegawai(prefix):
    st.markdown("#### 🛠️ Menu Mandiri Pegawai")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 ABSENSI", key=f"abs_{prefix}", use_container_width=True):
            st.toast("Menjalankan Fitur Geofencing Absensi...")
    with c2:
        if st.button("📝 LAPKIN", key=f"lap_{prefix}", use_container_width=True):
            st.markdown(f'<a href="{SCRIPT_LAPKIN}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:40px; background-color:#F59E0B; border:none; border-radius:10px; color:white; font-weight:bold;">BUKA FORM LAPKIN</button></a>', unsafe_allow_html=True)
    
    st.write("---")
    c3, c4 = st.columns(2)
    with c3:
        if st.button("📅 REKAP SAYA", key=f"rek_{prefix}", use_container_width=True):
            st.info("Menarik data riwayat pribadi...")
    with c4:
        if st.button("📥 DOWNLOAD", key=f"dow_{prefix}", use_container_width=True):
            st.info("Menyiapkan dokumen download...")

# --- 7. TAMPILAN DASHBOARD ---
if role == "Admin":
    st.title("🏛️ DASHBOARD ADMIN")
    # Menu Mandiri Admin (Bisa Absen/Lapkin Sendiri)
    with st.expander("🔑 AKSES PRIBADI SAYA", expanded=False):
        render_menu_pegawai("admin_self")
        
    tabs = st.tabs(["📊 MONITORING 31 PEGAWAI", "📥 REKAP DATA", "⚙️ KELOLA USER"])
    with tabs[0]:
        st.subheader("Status Real-time Seluruh Pegawai")
        st.info("Sistem Monitoring Aktif...")
    with tabs[1]:
        st.button("Export Semua Rekap ke Excel")
    with tabs[2]:
        st.subheader("Manajemen Password")
        df_users = pd.DataFrame([{"NIP":k, "Nama":v['nama'], "Pass":v['pass'], "Role":v['role']} for k,v in st.session_state.user_db.items()])
        st.dataframe(df_users, use_container_width=True)

elif role == "Bendahara":
    st.title("💰 DASHBOARD BENDAHARA")
    with st.expander("🔑 AKSES PRIBADI SAYA", expanded=False):
        render_menu_pegawai("bend_self")
    tabs = st.tabs(["📊 MONITORING", "📥 DOWNLOAD DATA"])

else: # PEGAWAI
    st.title("📱 HUB PEGAWAI")
    st.markdown(f"Selamat bekerja, **{user['nama']}**")
    st.markdown('<div style="border: 2px solid #F59E0B; padding:30px; border-radius:20px; background-color:rgba(255,255,255,0.05);">', unsafe_allow_html=True)
    render_menu_pegawai("user_only")
    st.markdown('</div>', unsafe_allow_html=True)
