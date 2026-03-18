import streamlit as st
import pandas as pd
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. POP-UP MENU MANDIRI (Sama untuk SEMUA Role) ---
@st.dialog("📋 AKSES MANDIRI PEGAWAI")
def pop_menu_mandiri(user):
    st.write(f"Nama: **{user['nama']}**")
    st.caption(f"NIP: {DATABASE_INFO[user['nama']][0]}")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        # Tombol Absen Langsung ke Google Form
        st.link_button("🚀 ABSEN SEKARANG", "https://link-google-form-absen-anda.com", use_container_width=True)
        # Tombol Download Absen Pribadi
        if st.button("📊 REKAP ABSEN SAYA", use_container_width=True):
            st.info("Fitur unduh absen pribadi sedang disiapkan...")

    with col2:
        # Tombol Lapkin Langsung ke Google Form
        st.link_button("📝 BUAT LAPKIN", "https://link-google-form-lapkin-anda.com", use_container_width=True)
        # Tombol Download Lapkin Pribadi (Privasi Terjaga)
        if st.button("📄 LAPKIN SAYA", use_container_width=True):
            st.info("File Lapkin Anda sedang diproses...")

# --- 2. DASHBOARD PEGAWAI (Fungsi Terbatas Mandiri) ---
def show_pegawai(user):
    st.markdown(f"### 📱 Hub Pegawai")
    st.info(f"Halo **{user['nama']}**, silakan gunakan tombol di bawah untuk urusan kehadiran dan kinerja.")
    
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    
    st.divider()
    st.subheader("📢 Pengumuman Internal")
    st.write("Belum ada pengumuman hari ini.")

# --- 3. DASHBOARD BENDAHARA (Fungsi Mandiri + Rekap Kantor) ---
def show_bendahara(user):
    st.markdown(f"### 💰 Hub Bendahara")
    
    # Tetap punya menu mandiri untuk absen diri sendiri
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    
    st.divider()
    st.subheader("📑 Fitur Khusus Bendahara")
    st.caption("Akses download rekap keseluruhan untuk keperluan administrasi keuangan.")
    
    # Bendahara bisa download rekap absen 31 orang (tapi bukan lapkin)
    if st.button("📥 DOWNLOAD REKAP ABSEN KESELURUHAN (EXCEL)", use_container_width=True):
        with st.spinner("Menarik data dari Google Sheets..."):
            # Logika download excel kolektif di sini
            st.success("File Rekap Absen 31 Pegawai berhasil dibuat!")

# --- 4. DASHBOARD ADMIN (Fungsi Paling Lengkap) ---
def show_admin(user, database):
    st.markdown(f"### 🏛️ Hub Administrator")
    
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    
    st.divider()
    
    tab_mon, tab_down, tab_set = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD CENTER", "🔑 SETTINGS"])
    
    with tab_mon:
        # Monitoring real-time (hanya admin yang bisa lihat status ALPA/HADIR semua orang)
        c1, c2 = st.columns([1, 1])
        tgl = c1.date_input("Tanggal Pantau:", datetime.now())
        search = c2.text_input("🔍 Cari Nama:")
        
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        
        # Sub-Tabs Filter
        s1, s2, s3 = st.tabs(["SEMUA", "PNS", "PPPK"])
        from dashboards import render_monitoring_list # Menggunakan fungsi render list
        
        with s1: 
            names = [n for n in list(database.keys()) if search.lower() in n.lower()]
            render_monitoring_list(names, data_log)
        # ... s2 dan s3 mengikuti pola s1 ...

    with tab_down:
        st.subheader("Pusat Unduhan Admin")
        st.button("📥 Download Rekap Absen Bulanan (Semua)", use_container_width=True)

    with tab_set:
        st.subheader("Manajemen Sistem")
        target = st.selectbox("Pilih Pegawai:", list(database.keys()))
        if st.button(f"Reset Password {target}", use_container_width=True):
            st.success(f"Password {target} direset ke default.")

# --- 5. FUNGSI RENDER LIST (Visual Card) ---
def render_monitoring_list(list_nama, data_log):
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid {color};">
                <small>{p}</small><br><b>{d['m']} - {d['p']}</b> ({d['k']})
            </div>
        """, unsafe_allow_html=True)
