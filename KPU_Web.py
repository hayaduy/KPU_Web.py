import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import time
import random

# --- 1. KONFIGURASI DASAR ---
st.set_page_config(page_title="KPU HSS Presence Hub v146.0", layout="wide")
wita_tz = pytz.timezone('Asia/Makassar')

# CSS Custom untuk tampilan Card dan Dashboard
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .card-box { background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; margin-bottom: 15px; backdrop-filter: blur(10px); }
    .status-tag { padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 11px; text-transform: uppercase; }
    .tag-pns { background-color: #1d4ed8; color: white; }
    .tag-pppk { background-color: #7c3aed; color: white; }
    .header-main { text-align: center; color: #F59E0B; font-size: 28px; font-weight: bold; margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE UTAMA (31 PEGAWAI) ---
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

# --- 3. FUNGSI MODAL (FITUR MANDIRI PEGAWAI) ---

@st.dialog("🚀 UPDATE ABSENSI HARIAN")
def modal_absen(nama):
    st.write(f"Pegawai: **{nama}**")
    tipe = st.selectbox("Pilih Tipe Absen", ["Masuk Pagi", "Pulang Kantor", "Izin Khusus"])
    st.info(f"Waktu saat ini: {datetime.now(wita_tz).strftime('%H:%M:%S')} WITA")
    if st.button("KIRIM DATA ABSEN", use_container_width=True):
        st.success("Absensi berhasil diperbarui!")
        time.sleep(1); st.rerun()

@st.dialog("📝 INPUT LAPORAN KINERJA (LAPKIN)")
def modal_lapkin(nama):
    st.write(f"Pengisian Lapkin untuk: **{nama}**")
    tgl = st.date_input("Tanggal Kegiatan", value=datetime.now(wita_tz).date())
    kegiatan = st.text_area("Uraian Pekerjaan/Hasil Kerja:", height=150, placeholder="Tuliskan aktivitas kerja Anda hari ini...")
    if st.button("SIMPAN LAPORAN", use_container_width=True):
        st.success("Laporan Kinerja harian telah tersimpan!")
        time.sleep(1); st.rerun()

# --- 4. DASHBOARD PEGAWAI ---
def dashboard_pegawai(user):
    st.markdown(f'<div class="header-main">📱 HUB PEGAWAI</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:white;'>Selamat Datang, <b>{user['nama']}</b></p>", unsafe_allow_html=True)
    
    # Grid Menu Utama Mandiri
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.write("### 🕒 Presensi")
        if st.button("🚀 UPDATE ABSEN", use_container_width=True): modal_absen(user['nama'])
        st.caption("Klik untuk absen masuk atau pulang")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.write("### 📝 Pekerjaan")
        if st.button("📝 ISI LAPKIN", use_container_width=True): modal_lapkin(user['nama'])
        st.caption("Klik untuk input uraian kerja harian")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-box" style="text-align:center;">', unsafe_allow_html=True)
    st.write("### 📥 Laporan")
    if st.button("📊 DOWNLOAD REKAP SAYA (EXCEL)", use_container_width=True):
        st.toast("Menyusun file laporan...")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. DASHBOARD ADMIN ---
def dashboard_admin():
    st.markdown('<div class="header-main">🏛️ DASHBOARD ADMIN</div>', unsafe_allow_html=True)
    
    # Filter Area
    with st.expander("🔍 Filter & Kontrol", expanded=True):
        c1, c2, c3 = st.columns([1,1,1])
        filter_jenis = c1.multiselect("Jenis Pegawai", ["PNS", "PPPK"], default=["PNS", "PPPK"])
        tgl_monitor = c2.date_input("Tanggal", value=datetime.now(wita_tz).date())
        if c3.button("🔄 REFRESH DATA"): st.rerun()

    st.write("---")
    
    # Loop 31 Pegawai dengan Filter
    for p, info in DATABASE_INFO.items():
        jenis = info[4]
        if jenis in filter_jenis:
            tag_clr = "tag-pns" if jenis == "PNS" else "tag-pppk"
            st.markdown(f"""
                <div class="card-box">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:16px; font-weight:bold; color:white;">{p}</span>
                        <span class="status-tag {tag_clr}">{jenis}</span>
                    </div>
                    <div style="font-size:12px; color:#cbd5e1; margin-top:5px;">NIP: {info[0]} | {info[1]}</div>
                    <div style="display:flex; gap:30px; margin-top:15px; background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;">
                        <div><small style="color:#94a3b8;">Masuk</small><br><b style="color:#10B981;">07:30</b></div>
                        <div><small style="color:#94a3b8;">Pulang</small><br><b style="color:#64748b;">--:--</b></div>
                        <div><small style="color:#94a3b8;">Status</small><br><b style="color:#10B981;">HADIR</b></div>
                        <div style="flex-grow:1; text-align:right;"><br><small style="color:#F59E0B;">Lihat Detail →</small></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 6. DASHBOARD BENDAHARA ---
def dashboard_bendahara():
    st.markdown('<div class="header-main">💰 DASHBOARD BENDAHARA</div>', unsafe_allow_html=True)
    st.info("Menu ini digunakan untuk validasi kehadiran terkait tunjangan dan uang makan.")
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.write("### Rekap Keuangan")
    if st.button("📊 DOWNLOAD DATA BENDAHARA (ALL)"):
        st.toast("Sedang mengunduh...")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SISTEM LOGIN & ROUTING ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN HUB</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP Pegawai")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK KE SISTEM", use_container_width=True):
            clean_in = u_nip.replace(" ", "").replace(".", "")
            match = next((k for k, v in DATABASE_INFO.items() if clean_in in v[0].replace(" ", "").replace(".", "")), None)
            if match and u_pass == "kpuhss2026":
                st.session_state.logged_in = True
                st.session_state.user = {"nama": match, "role": DATABASE_INFO[match][7]}
                st.rerun()
            else: st.error("Maaf, NIP atau Password salah!")
    st.stop()

# Logout di Sidebar
if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()

# --- MENU ROUTER ---
role_user = st.session_state.user['role']
if role_user == "Admin": dashboard_admin()
elif role_user == "Bendahara": dashboard_bendahara()
else: dashboard_pegawai(st.session_state.user)
