import streamlit as st
import pandas as pd
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK

# --- FUNGSI MANDIRI (ABSEN & LAPKIN) ---
@st.dialog("🚀 KONFIRMASI TINDAKAN")
def pop_update(nama, jenis):
    st.write(f"Pegawai: **{nama}**")
    info = DATABASE_INFO[nama]
    
    if jenis == "Absen":
        st.warning("Pastikan Anda berada di lokasi kantor/tugas.")
        if st.button("KIRIM PRESENSI SEKARANG", use_container_width=True):
            # Di sini nanti masukkan link Google Form Abang
            st.success("Presensi Berhasil Dikirim!")
            st.rerun()
    else:
        st.subheader("Form Laporan Kinerja")
        status = st.selectbox("Status Kehadiran:", ["Hadir", "Tugas Luar", "Izin", "Sakit"])
        uraian = st.text_area("Apa yang Anda kerjakan hari ini?")
        if st.button("SIMPAN LAPORAN", use_container_width=True):
            # Di sini nanti masukkan link Apps Script Abang
            st.success("Laporan Berhasil Disimpan!")
            st.rerun()

def menu_mandiri(nama):
    st.markdown("### 👤 Menu Mandiri")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 ABSEN SEKARANG", use_container_width=True):
            pop_update(nama, "Absen")
    with c2:
        if st.button("📝 BUAT LAPKIN", use_container_width=True):
            pop_update(nama, "Lapkin")

# --- 1. DASHBOARD PEGAWAI ---
def show_pegawai(user):
    st.write(f"Login sebagai: **Pegawai**")
    menu_mandiri(user['nama'])
    st.divider()
    st.subheader("📥 Laporan Saya")
    st.button("📊 Download Rekap Absen Bulanan SAYA")
    st.button("📄 Download Histori Lapkin SAYA")

# --- 2. DASHBOARD BENDAHARA ---
def show_bendahara(user):
    st.write(f"Login sebagai: **Bendahara**")
    menu_mandiri(user['nama'])
    st.divider()
    st.subheader("💰 Fitur Keuangan")
    if st.button("📥 DOWNLOAD REKAP KESELURUHAN (EXCEL)", use_container_width=True):
        st.write("Sedang menarik data dari Google Sheets...")
    st.button("📄 Download Lapkin SAYA")

# --- 3. DASHBOARD ADMIN ---
def show_admin(user, database):
    st.write(f"Login sebagai: **Administrator**")
    menu_mandiri(user['nama'])
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD CENTER", "🔑 SETTINGS"])
    
    with tab1:
        st.subheader("Status Kehadiran Real-time")
        tgl = st.date_input("Pantau Tanggal:", datetime.now())
        # Memanggil mesin core_logic untuk ambil data asli
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        
        for p in list(database.keys()):
            d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
            color = "#10B981" if d['k'] == "HADIR" else "#F59E0B" if d['k'] == "TERLAMBAT" else "#EF4444"
            
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; background:rgba(255,255,255,0.05); padding:10px; border-radius:5px; margin-bottom:5px; border-left: 5px solid {color}">
                    <span>{p}</span>
                    <span>Masuk: <b>{d['m']}</b> | Pulang: <b>{d['p']}</b> | <b style="color:{color}">{d['k']}</b></span>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Unduh Laporan Kolektif")
        st.button("📥 Download SEMUA Lapkin Pegawai (Bulan Ini)")
        st.button("📥 Download Rekap Absen SEMUA Pegawai")

    with tab3:
        st.subheader("Manajemen Akun")
        target = st.selectbox("Pilih Pegawai untuk Reset:", list(database.keys()))
        if st.button(f"Reset Password {target} ke Default"):
            st.success(f"Password {target} dikembalikan ke: kpuhss2026")
