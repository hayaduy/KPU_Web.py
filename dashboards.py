import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from database import DATABASE_INFO
# Import semua fungsi logic dari file core_logic.py
from core_logic import (
    process_attendance, 
    get_lapkin_data, 
    create_excel_file, 
    URL_PNS, 
    URL_PPPK
)

# Konfigurasi konstanta
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
# URL API LAPKIN sudah diperbarui sesuai input terakhir Abang
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbyXtsnv9OQ1qDkF41iCsqWzcQbqy0YKmrdrzzR4bAno19g3RRWjhpxxeKTDW1c05Irz/exec"
URL_API_PNS = "https://script.google.com/macros/s/AKfycbyWJbg_KceQroTV51pFuM30Ij-K4VwynhjK9NI2R-VBYrLJEA1rh7prec4MvNiKBUJV/exec"
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbwWKNLcFa06rxdCSbr1Ex-6dTUzjxJndEfF_bnBZx0oPOevtXqB6H3nUttupzE2D9yn/exec"

# --- 1. LOGIKA PENANDATANGAN (KHUSUS UI) ---
def get_approver_options(user_nama):
    if user_nama not in DATABASE_INFO:
        return ["Suwanto, SH., MH."], 0
    info = DATABASE_INFO[user_nama]
    jabatan = info[1]
    atasan_list = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE"]
    idx = 0
    if any(x in jabatan for x in ["Teknis", "Pemilu"]): idx = 1
    elif any(x in jabatan for x in ["Keuangan", "Umum", "Logistik"]): idx = 2
    elif any(x in jabatan for x in ["Hukum", "SDM"]): idx = 3
    elif any(x in jabatan for x in ["Perencanaan", "Data"]): idx = 4
    return atasan_list, idx

# --- 2. UI COMPONENTS ---
def inject_custom_css():
    st.markdown("""<style>[data-testid="stMetricValue"] { font-size: 24px; } .stButton button { border-radius: 8px; }</style>""", unsafe_allow_html=True)

@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    tab_abs, tab_lap, tab_dl = st.tabs(["🚀 ABSEN", "📝 LAPKIN", "📥 DOWNLOAD"])
    
    with tab_abs:
        if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
            target_url = URL_API_PNS if info[4] == "PNS" else URL_API_PPPK
            payload = {"nama": user['nama'], "nip": info[0], "jabatan": info[1], "status": info[4]}
            try:
                res = requests.post(target_url, json=payload, timeout=10)
                st.success("Presensi Berhasil!") if "Success" in res.text else st.error(res.text)
            except: st.error("Gagal terhubung")

    with tab_lap:
        stat = st.selectbox("Status Kehadiran:", ["HADIR", "IZIN", "TL", "CUTI"])
        hasil = st.text_input("Hasil Kerja / Output Hari Ini:") 
        if st.button("KIRIM DATA LAPKIN", use_container_width=True):
            if hasil:
                payload = {"nama": user['nama'], "nip": info[0], "jabatan": info[1], "status": stat, "uraian": hasil}
                try:
                    requests.post(URL_API_LAPKIN, json=payload, timeout=10)
                    st.success("Lapkin Terkirim!")
                except: st.error("Gagal mengirim")
            else: st.warning("Mohon isi hasil kerja!")

    with tab_dl:
        bln = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now().month-1)
        thn = st.selectbox("Tahun:", [2025, 2026], index=1)
        list_atasan, def_idx = get_approver_options(user['nama'])
        ttd_pilih = st.selectbox("Penandatangan:", list_atasan, index=def_idx)
        
        if st.button("🔍 PROSES EXCEL", use_container_width=True):
            with st.spinner("Menyusun Laporan..."):
                # 1. Ambil data dari API GSheet via core_logic
                data = get_lapkin_data(URL_API_LAPKIN, LIST_BULAN, user['nama'], bln, thn)
                
                if not data:
                    st.warning(f"Data Lapkin untuk {bln} {thn} tidak ditemukan. Excel akan tetap dibuat tanpa rincian kegiatan.")
                
                # 2. Buat file Excel
                excel_data = create_excel_file(DATABASE_INFO, LIST_BULAN, user['nama'], bln, thn, ttd_pilih, data)
                
                if excel_data:
                    st.success(f"Laporan {bln} {thn} siap diunduh!")
                    st.download_button(
                        label="📥 DOWNLOAD FILE SEKARANG", 
                        data=excel_data, 
                        file_name=f"LAPKIN_{user['nama']}_{bln}_{thn}.xlsx", 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                        use_container_width=True
                    )
                else:
                    st.error("Terjadi kesalahan saat membuat file Excel.")

# --- 3. DASHBOARD VIEWS ---
def show_pegawai(user):
    inject_custom_css()
    st.subheader(f"Halo, {user['nama']} 👋")
    c1, c2 = st.columns(2)
    if c1.button("🚀 ABSEN / HADIR", use_container_width=True, type="primary"): pop_menu_mandiri(user)
    if c2.button("📝 ISI LAPKIN", use_container_width=True): pop_menu_mandiri(user)
    st.divider()
    # Manggil logic presensi
    data_log = process_attendance([URL_PNS, URL_PPPK], [user['nama']], datetime.now())
    render_monitoring_list([user['nama']], data_log)

def show_admin(user, database):
    inject_custom_css()
    st.subheader("🏛️ Administrator Panel")
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True): pop_menu_mandiri(user)
    tab1, tab2 = st.tabs(["🔍 MONITORING", "👥 KELOLA USER"])
    with tab1:
        tgl = st.date_input("Pilih Tanggal Monitoring:", datetime.now())
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list(list(database.keys()), data_log)
    with tab2:
        st.dataframe(pd.DataFrame([{"Nama": k, "NIP": v[0], "Jabatan": v[1], "Role": v[3]} for k, v in database.items()]), use_container_width=True)

def show_bendahara(user):
    inject_custom_css()
    st.subheader("💰 Menu Bendahara")
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True): pop_menu_mandiri(user)
    tgl = st.date_input("Rekap Kehadiran Tanggal:", datetime.now())
    data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl)
    render_monitoring_list(list(DATABASE_INFO.keys()), data_log)

def render_monitoring_list(list_nama, data_log):
    # Urutkan nama agar rapi
    for p in sorted(list_nama):
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid {color};">
            <small style="color:#888;">{p}</small><br>
            <div style="display:flex; justify-content:space-between;">
                <span><b>{d['m']} - {d['p']}</b></span>
                <span style="color:{color}; font-weight:bold;">{d['k']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
