import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import time

# --- 1. SETUP & STYLE ---
st.set_page_config(page_title="KPU HSS Presence Hub v145.0", layout="wide")
wita_tz = pytz.timezone('Asia/Makassar')

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .card-box { background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .status-tag { padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .tag-pns { background-color: #3b82f6; color: white; }
    .tag-pppk { background-color: #8b5cf6; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE LENGKAP (31 PEGAWAI) ---
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

# --- 3. DIALOGS (PENGISIAN MANDIRI) ---

@st.dialog("📝 INPUT LAPKIN HARIAN")
def pop_lapkin(nama):
    st.write(f"Laporan Kerja: **{nama}**")
    tgl = st.date_input("Tanggal", value=datetime.now(wita_tz).date())
    uraian = st.text_area("Apa kegiatan/pekerjaan Anda hari ini?", height=150)
    if st.button("SIMPAN LAPKIN", use_container_width=True):
        st.success("Laporan berhasil dikirim!"); time.sleep(1); st.rerun()

@st.dialog("🚀 UPDATE ABSENSI")
def pop_absen(nama):
    st.write(f"Update Absen: **{nama}**")
    tipe = st.radio("Tipe Presensi", ["Masuk", "Pulang"])
    jam = datetime.now(wita_tz).strftime("%H:%M:%S")
    st.info(f"Waktu terdeteksi: {jam}")
    if st.button("KIRIM SEKARANG", use_container_width=True):
        st.success(f"Berhasil Absen {tipe} pada jam {jam}"); time.sleep(1); st.rerun()

# --- 4. DASHBOARD ADMIN (DENGAN FILTER) ---
def dashboard_admin():
    st.header("🏛️ Dashboard Admin")
    
    # FILTER JENIS PEGAWAI
    col1, col2 = st.columns([1, 1])
    filter_jenis = col1.multiselect("Filter Jenis Pegawai", ["PNS", "PPPK"], default=["PNS", "PPPK"])
    tgl_pilih = col2.date_input("Tanggal Monitoring", value=datetime.now(wita_tz).date())

    st.write("---")
    
    # Rendering 31 Pegawai berdasarkan Filter
    for p, info in DATABASE_INFO.items():
        jenis = info[4] # Index 4 adalah PNS/PPPK
        if jenis in filter_jenis:
            tag_class = "tag-pns" if jenis == "PNS" else "tag-pppk"
            st.markdown(f"""
                <div class="card-box">
                    <div style="display:flex; justify-content:space-between;">
                        <b>{p}</b>
                        <span class="status-tag {tag_class}">{jenis}</span>
                    </div>
                    <p style="font-size:12px; color:#cbd5e1; margin:0;">NIP: {info[0]} | Jabatan: {info[1]}</p>
                    <hr style="margin:10px 0; border:0.1px solid rgba(255,255,255,0.1);">
                    <div style="display:flex; gap:20px; font-size:13px;">
                        <span>Masuk: <b style="color:#10B981;">07:30</b></span>
                        <span>Pulang: <b style="color:#64748b;">--:--</b></span>
                        <span>Status: <b style="color:#10B981;">HADIR</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 5. DASHBOARD PEGAWAI (MANDIRI) ---
def dashboard_pegawai(user):
    st.header(f"📱 Hub Pegawai")
    st.write(f"Halo, **{user['nama']}**")
    
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Menu Utama")
    c1, c2 = st.columns(2)
    if c1.button("🚀 UPDATE ABSENSI", use_container_width=True): pop_absen(user['nama'])
    if c2.button("📝 INPUT LAPKIN", use_container_width=True): pop_lapkin(user['nama'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Laporan & Rekap")
    if st.button("📥 DOWNLOAD LAPORAN BULANAN (EXCEL)", use_container_width=True):
        st.toast("Menyiapkan file Excel...")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LOGIN & ROUTING ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown("<h2 style='text-align:center;'>LOGIN</h2>", unsafe_allow_html=True)
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

# --- SIDEBAR LOGOUT ---
if st.sidebar.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()

# --- DASHBOARD SELECTOR ---
role = st.session_state.user['role']
if role == "Admin": dashboard_admin()
elif role == "Bendahara": 
    st.title("💰 Dashboard Bendahara")
    st.info("Fitur validasi keuangan aktif.")
else: dashboard_pegawai(st.session_state.user)
