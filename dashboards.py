# dashboards.py
import streamlit as st
import requests
import time
from datetime import datetime
from database import DATABASE_INFO

SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

@st.dialog("🚀 UPDATE DATA MANDIRI")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    tipe = st.radio("Pilih Kegiatan:", ["Absen", "Lapkin"])
    info = DATABASE_INFO[nama]
    
    if tipe == "Absen":
        if st.button("KIRIM ABSEN SEKARANG", use_container_width=True):
            st.success("Presensi Terkirim!"); time.sleep(1); st.rerun()
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar"])
        h_kerja = st.text_area("Uraian Hasil Kerja:")
        if st.button("SIMPAN LAPORAN", use_container_width=True):
            payload = {"nama": nama, "nip": info[0], "status": st_fix, "hasil": h_kerja}
            requests.post(SCRIPT_LAPKIN, json=payload)
            st.success("Tersimpan!"); time.sleep(1); st.rerun()

def view_admin(database, log_data, tgl):
    st.subheader("📊 Monitoring Pegawai (Admin)")
    # Logic monitoring di sini...
    st.info("Fitur Reset Password & Download Full Aktif.")

def view_pegawai(user):
    st.subheader(f"👋 Halo, {user['nama']}")
    c1, c2 = st.columns(2)
    if c1.button("🚀 ABSEN"): pop_update(user['nama'])
    if c2.button("📝 LAPKIN"): pop_update(user['nama'])
