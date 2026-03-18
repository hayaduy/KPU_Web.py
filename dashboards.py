import streamlit as st
import pandas as pd
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK

# --- 1. MENU MANDIRI (SEKARANG DISREMBUNYIKAN) ---
@st.dialog("📋 MENU MANDIRI & LAPORAN")
def pop_menu_mandiri(user):
    st.write(f"Pegawai: **{user['nama']}**")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 ABSEN SEKARANG", use_container_width=True):
            st.success("Form Absen Dibuka...")
        if st.button("📊 DOWNLOAD ABSEN SAYA", use_container_width=True):
            st.info("Mengunduh Rekap Absen...")
            
    with col2:
        if st.button("📝 BUAT LAPKIN", use_container_width=True):
            st.success("Form Lapkin Dibuka...")
        if st.button("📄 DOWNLOAD LAPKIN SAYA", use_container_width=True):
            st.info("Mengunduh File Lapkin...")

def render_menu_mandiri_button(user):
    st.markdown("### 👤 Akses Pribadi")
    if st.button("📂 BUKA MENU MANDIRI (Absen, Lapkin & Unduhan)", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)

# --- 2. FUNGSI RENDER LIST MONITORING (LEBIH RAPI) ---
def render_monitoring_list(list_nama, data_log):
    if not list_nama:
        st.caption("Tidak ada data pegawai di kategori ini.")
        return

    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        
        # Logika Warna & Label
        if d['k'] == "HADIR":
            bg_color, txt_color, border = "rgba(16, 185, 129, 0.1)", "#10B981", "#10B981"
        elif d['k'] == "TERLAMBAT":
            bg_color, txt_color, border = "rgba(245, 158, 11, 0.1)", "#F59E0B", "#F59E0B"
        else:
            bg_color, txt_color, border = "rgba(239, 68, 68, 0.1)", "#EF4444", "#EF4444"

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        background: {bg_color}; padding: 12px 20px; border-radius: 10px; 
                        margin-bottom: 8px; border: 1px solid {border}33; border-left: 5px solid {border};">
                <div style="flex: 1;">
                    <span style="font-weight: 600; font-size: 15px; color: #E0E0E0;">{p}</span>
                </div>
                <div style="display: flex; gap: 20px; font-family: 'Courier New', monospace;">
                    <div style="text-align: center;">
                        <div style="font-size: 10px; color: #888;">MASUK</div>
                        <div style="font-weight: bold; color: {txt_color};">{d['m']}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 10px; color: #888;">PULANG</div>
                        <div style="font-weight: bold; color: {txt_color};">{d['p']}</div>
                    </div>
                    <div style="text-align: center; min-width: 80px; margin-left: 10px; padding-top: 5px;">
                        <span style="background: {border}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{d['k']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 3. DASHBOARD PEGAWAI ---
def show_pegawai(user):
    render_menu_mandiri_button(user)
    st.divider()
    st.info("Gunakan tombol di atas untuk melakukan Absensi atau mengunduh laporan Kinerja (Lapkin) Anda.")

# --- 4. DASHBOARD BENDAHARA ---
def show_bendahara(user):
    render_menu_mandiri_button(user)
    st.divider()
    st.subheader("💰 Panel Bendahara")
    if st.button("📥 DOWNLOAD REKAP ABSEN KESELURUHAN (EXCEL)", use_container_width=True):
        st.write("Memproses data...")

# --- 5. DASHBOARD ADMIN ---
def show_admin(user, database):
    render_menu_mandiri_button(user)
    st.divider()
    
    tab_mon, tab_down, tab_set = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD CENTER", "🔑 SETTINGS"])
    
    with tab_mon:
        c1, c2 = st.columns([2, 1])
        with c1:
            tgl = st.date_input("Pilih Tanggal Pantau:", datetime.now())
        with c2:
            st.write("") # Spacer
            st.write(f"📅 {tgl.strftime('%A, %d %b %Y')}")

        # Sub-Tabs untuk filter Pegawai
        st.markdown("---")
        sub1, sub2, sub3 = st.tabs(["👥 SEMUA", "👔 PNS", "💼 PPPK"])
        
        # Ambil data dari core_logic
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)

        with sub1:
            render_monitoring_list(list(database.keys()), data_log)
        with sub2:
            render_monitoring_list(MASTER_PNS, data_log)
        with sub3:
            render_monitoring_list(MASTER_PPPK, data_log)

    with tab_down:
        st.subheader("Pusat Unduhan Kolektif")
        st.caption("Lapkin bersifat pribadi dan hanya bisa diunduh oleh pegawai yang bersangkutan di Menu Mandiri.")
        st.button("📥 Download Rekap Absensi Seluruh Pegawai (Excel)", use_container_width=True)

    with tab_set:
        st.subheader("Pengaturan Akun")
        target = st.selectbox("Pilih Nama Pegawai:", list(database.keys()))
        if st.button(f"Reset Password {target}", use_container_width=True):
            st.success(f"Password {target} telah direset.")
