import streamlit as st
import pandas as pd
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. CSS CUSTOM UNTUK TAMPILAN CENTER TAB & WARNA KPU ---
def inject_custom_css():
    st.markdown("""
        <style>
        /* Mengatur wadah tab agar memenuhi lebar (Center Look) */
        button[data-baseweb="tab"] {
            font-size: 14px;
            font-weight: 600;
            flex: 1; 
            text-align: center;
        }
        
        /* Mengatur teks di dalam tab agar benar-benar di tengah */
        button[data-baseweb="tab"] div p {
            margin: 0 auto;
        }

        /* Warna garis bawah tab saat aktif (Merah KPU) */
        div[data-baseweb="tab-highlight"] {
            background-color: #EF4444; 
        }

        /* Efek hover pada tab */
        button[data-baseweb="tab"]:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. POP-UP MENU MANDIRI (Sama untuk SEMUA Role) ---
@st.dialog("📋 AKSES MANDIRI PEGAWAI")
def pop_menu_mandiri(user):
    st.write(f"Nama: **{user['nama']}**")
    st.caption(f"NIP: {DATABASE_INFO[user['nama']][0]}")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚀 ABSEN SEKARANG", "https://link-google-form-absen-anda.com", use_container_width=True)
        if st.button("📊 REKAP ABSEN SAYA", use_container_width=True):
            st.info("Fitur unduh absen pribadi sedang disiapkan...")

    with col2:
        st.link_button("📝 BUAT LAPKIN", "https://link-google-form-lapkin-anda.com", use_container_width=True)
        if st.button("📄 LAPKIN SAYA", use_container_width=True):
            st.info("File Lapkin Anda sedang diproses...")

# --- 3. FUNGSI RENDER LIST (Visual Card Monitoring) ---
def render_monitoring_list(list_nama, data_log):
    if not list_nama:
        st.caption("Nama tidak ditemukan...")
        return
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        # Warna Hijau jika Hadir, Kuning jika Terlambat, Merah jika Alpa
        color = "#10B981" if d['k'] == "HADIR" else "#F59E0B" if d['k'] == "TERLAMBAT" else "#EF4444"
        
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; margin-bottom:8px; border-left:5px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <small style="color:#bbb;">{DATABASE_INFO[p][1]}</small><br>
                        <span style="font-weight:600;">{p}</span>
                    </div>
                    <div style="text-align:right; font-family:monospace;">
                        <span style="font-size:12px;">{d['m']} - {d['p']}</span><br>
                        <span style="color:{color}; font-size:11px; font-weight:bold;">{d['k']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 4. DASHBOARD PEGAWAI ---
def show_pegawai(user):
    st.markdown(f"### 📱 Hub Pegawai")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    st.subheader("📢 Pengumuman")
    st.write("Belum ada pengumuman hari ini.")

# --- 5. DASHBOARD BENDAHARA ---
def show_bendahara(user):
    inject_custom_css()
    st.markdown(f"### 💰 Hub Bendahara")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    
    t1, t2 = st.tabs(["📊 DATA KANTOR", "📥 DOWNLOAD"])
    with t1:
        st.subheader("Rekap Kehadiran Kantor")
        st.caption("Gunakan data ini untuk keperluan amprah.")
    with t2:
        if st.button("📥 DOWNLOAD REKAP ABSEN KESELURUHAN (EXCEL)", use_container_width=True):
            st.success("File Rekap Berhasil Dibuat!")

# --- 6. DASHBOARD ADMIN ---
def show_admin(user, database):
    inject_custom_css()
    st.markdown(f"### 🏛️ Hub Administrator")
    
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    
    tab_mon, tab_down, tab_set = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD CENTER", "🔑 SETTINGS"])
    
    with tab_mon:
        c1, c2 = st.columns([1, 1])
        tgl = c1.date_input("Tanggal Pantau:", datetime.now())
        search = c2.text_input("🔍 Cari Nama:")
        
        # Ambil data REAL dari Sheets
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        
        s1, s2, s3 = st.tabs(["SEMUA", "PNS", "PPPK"])
        
        with s1:
            names = [n for n in list(database.keys()) if search.lower() in n.lower()]
            render_monitoring_list(names, data_log)
        with s2:
            names = [n for n in MASTER_PNS if search.lower() in n.lower()]
            render_monitoring_list(names, data_log)
        with s3:
            names = [n for n in MASTER_PPPK if search.lower() in n.lower()]
            render_monitoring_list(names, data_log)

    with tab_down:
        st.subheader("Pusat Unduhan Admin")
        st.button("📥 Download Rekap Absen Bulanan (Semua)", use_container_width=True)

    with tab_set:
        st.subheader("Manajemen Sistem")
        target = st.selectbox("Pilih Pegawai:", list(database.keys()))
        if st.button(f"Reset Password {target}", use_container_width=True):
            st.success(f"Password {target} direset ke default.")
