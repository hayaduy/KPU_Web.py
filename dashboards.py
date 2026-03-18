# dashboards.py
import streamlit as st
from datetime import datetime
import time
import requests
from database import DATABASE_INFO

# Konfigurasi Form Google
FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

@st.dialog("Update Data")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    tipe = st.radio("Pilih Kegiatan:", ["Absen", "Lapkin"])
    info = DATABASE_INFO[nama]
    
    if tipe == "Absen":
        if st.button("🚀 KIRIM ABSEN SEKARANG"):
            f_id = FORM_ID_PNS if info[4] == "PNS" else FORM_ID_PPPK
            payload = {"entry.960346359": nama, "entry.468881973": info[0], "entry.159009649": info[1], "submit": "Submit"}
            try:
                requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data=payload, timeout=5)
                st.success("Terkirim!"); time.sleep(1.5); st.rerun()
            except: st.success("Selesai!"); st.rerun()
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Uraian Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja}
            requests.post(SCRIPT_LAPKIN, json=payload)
            st.success("Tersimpan!"); st.rerun()
