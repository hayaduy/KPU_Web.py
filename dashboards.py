import streamlit as st
import pandas as pd
from datetime import datetime
from database import DATABASE_INFO
# Import fungsi dari core_logic.py milik Abang
from core_logic import (
    process_attendance, 
    get_lapkin_data, 
    create_excel_file, 
    URL_PNS, 
    URL_PPPK
)

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbyXtsnv9OQ1qDkF41iCsqWzcQbqy0YKmrdrzzR4bAno19g3RRWjhpxxeKTDW1c05Irz/exec"

def get_approver_options(user_nama):
    """Menentukan daftar atasan dan default pilihan berdasarkan subbag"""
    info = DATABASE_INFO.get(user_nama, ["", ""])
    atasan_list = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE"]
    idx = 0
    subbag = str(info[3]).lower() if len(info) > 3 else ""
    
    if "teknis" in subbag or "hupmas" in subbag: idx = 1
    elif "keuangan" in subbag or "umum" in subbag: idx = 2
    elif "hukum" in subbag or "sdm" in subbag: idx = 3
    elif "perencanaan" in subbag or "data" in subbag: idx = 4
    return atasan_list, idx

@st.dialog("📋 MENU MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    tab_abs, tab_lap, tab_dl = st.tabs(["🚀 ABSEN", "📝 LAPKIN", "📥 DOWNLOAD"])
    
    with tab_abs:
        st.info("Fitur absensi otomatis sedang sinkron dengan Google Sheets.")
        if st.button("KLIK HADIR (SIMULASI)", use_container_width=True):
            st.success("Data kehadiran akan terbaca pada proses sinkronisasi berikutnya.")

    with tab_lap:
        stat = st.selectbox("Status Kehadiran:", ["HADIR", "IZIN", "TL", "CUTI"])
        hasil = st.text_area("Uraian Hasil Kerja Hari Ini:", placeholder="Contoh: Menyusun draf laporan keuangan...") 
        if st.button("KIRIM DATA LAPKIN", use_container_width=True, type="primary"):
            if hasil:
                try:
                    import requests
                    requests.post(URL_API_LAPKIN, json={"nama": user['nama'], "uraian": hasil, "status": stat})
                    st.success("Laporan berhasil dikirim ke database!")
                except:
                    st.error("Gagal mengirim data. Cek koneksi internet.")
            else: st.warning("Uraian kegiatan tidak boleh kosong, Bang!")

    with tab_dl:
        bln = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now().month-1)
        thn = st.selectbox("Pilih Tahun:", [2025, 2026], index=1)
        list_atasan, def_idx = get_approver_options(user['nama'])
        ttd = st.selectbox("Penandatangan (Atasan):", list_atasan, index=def_idx)
        
        if st.button("🔍 PROSES DATA EXCEL", use_container_width=True):
            with st.spinner("Sedang menyusun laporan..."):
                # Memanggil fungsi get_lapkin_data dari core_logic
                data = get_lapkin_data(URL_API_LAPKIN, LIST_BULAN, user['nama'], bln, thn)
                # Memanggil fungsi create_excel_file dari core_logic
                excel_data = create_excel_file(DATABASE_INFO, LIST_BULAN, user['nama'], bln, thn, ttd, data)
                st.session_state['ready_file'] = excel_data
                st.success("Laporan siap diunduh!")

        if 'ready_file' in st.session_state and st.session_state['ready_file']:
            st.download_button(
                label="📥 DOWNLOAD SEKARANG",
                data=st.session_state['ready_file'],
                file_name=f"LAPKIN_{user['nama']}_{bln}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# --- FUNGSI TAMPILAN DASHBOARD ---

def show_pegawai(user):
    st.subheader(f"Halo, {user['nama']} 👋")
    st.caption(f"Jabatan: {DATABASE_INFO[user['nama']][1]}")
    
    if st.button("📂 BUKA MENU MANDIRI (ABSEN/LAPKIN)", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    
    st.divider()
    st.subheader("📊 Monitoring Kehadiran Saya")
    data_log = process_attendance([URL_PNS, URL_PPPK], [user['nama']], datetime.now())
    render_monitoring_list([user['nama']], data_log)

def show_admin(user, database):
    st.subheader("🏛️ Panel Admin KPU")
    if st.button("📂 MENU MANDIRI SAYA"): pop_menu_mandiri(user)
    
    t1, t2 = st.tabs(["🔍 MONITORING HARIAN", "👥 DAFTAR PEGAWAI"])
    with t1:
        tgl = st.date_input("Pilih Tanggal Pantau:", datetime.now())
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list(list(database.keys()), data_log)
    with t2:
        df_user = pd.DataFrame([{"Nama": k, "NIP": v[0], "Jabatan": v[1], "Subbag": v[3]} for k, v in database.items()])
        st.dataframe(df_user, use_container_width=True)

def show_bendahara(user):
    st.subheader("💰 Panel Bendahara")
    if st.button("📂 MENU MANDIRI SAYA"): pop_menu_mandiri(user)
    
    tgl = st.date_input("Rekap Absensi Tanggal:", datetime.now())
    data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl)
    render_monitoring_list(list(DATABASE_INFO.keys()), data_log)

def render_monitoring_list(list_nama, data_log):
    """Menampilkan list pegawai dengan indikator warna"""
    for p in sorted(list_nama):
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:10px; margin-bottom:8px; border-left:6px solid {color};">
                <div style="display: flex; justify-content: space-between;">
                    <b>{p}</b>
                    <span style="color:{color}; font-weight:bold;">{d['k']}</span>
                </div>
                <small>🕒 Masuk: {d['m']} | 🕒 Pulang: {d['p']}</small>
            </div>
        """, unsafe_allow_html=True)
