import streamlit as st
import pandas as pd

# --- FUNGSI MANDIRI (WAJIB ADA DI SEMUA ROLE) ---
def menu_mandiri(nama):
    st.markdown("### 👤 Menu Mandiri")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 ABSEN SEKARANG", use_container_width=True):
            st.info("Membuka Form Absen...") # Hubungkan ke pop_update nanti
    with c2:
        if st.button("📝 BUAT LAPKIN", use_container_width=True):
            st.info("Membuka Form Lapkin...")

# --- 1. DASHBOARD PEGAWAI ---
def show_pegawai(user):
    st.title(f"📱 Dashboard Pegawai")
    st.write(f"Selamat Datang, **{user['nama']}**")
    menu_mandiri(user['nama'])
    st.divider()
    st.button("📊 Download Rekap Absen SAYA")
    st.button("📄 Download Lapkin SAYA")

# --- 2. DASHBOARD BENDAHARA ---
def show_bendahara(user):
    st.title(f"💰 Dashboard Bendahara")
    st.write(f"Selamat Datang, **{user['nama']}**")
    menu_mandiri(user['nama'])
    st.divider()
    st.subheader("Fitur Khusus Bendahara")
    st.button("📥 DOWNLOAD REKAP KESELURUHAN PEGAWAI")
    st.button("📄 Download Lapkin SAYA")

# --- 3. DASHBOARD ADMIN ---
def show_admin(user, database):
    st.title(f"🏛️ Dashboard Admin")
    st.write(f"Selamat Datang, **{user['nama']}**")
    menu_mandiri(user['nama'])
    st.divider()
    
    t1, t2, t3 = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD", "🔑 SETTINGS"])
    with t1:
        st.subheader("Monitoring 31 Pegawai")
        st.write("Status kehadiran real-time muncul di sini...")
    with t2:
        st.button("📥 Download Hasil Lapkin SEMUA Pegawai")
        st.button("📥 Download Rekap KESELURUHAN")
    with t3:
        st.subheader("Reset Password")
        target = st.selectbox("Pilih Pegawai:", list(database.keys()))
        if st.button(f"Reset Password {target}"):
            st.success(f"Password {target} direset!")
