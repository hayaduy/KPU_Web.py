import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. KONFIGURASI URL ---
URL_API_PNS = "https://script.google.com/macros/s/AKfycbyWJbg_KceQroTV51pFuM30Ij-K4VwynhjK9NI2R-VBYrLJEA1rh7prec4MvNiKBUJV/exec"
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbwWKNLcFa06rxdCSbr1Ex-6dTUzjxJndEfF_bnBZx0oPOevtXqB6H3nUttupzE2D9yn/exec"
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbzJ_gHm4clqncelQOKDdHR6UK9wiTXgMNSqLMQnBBNVCg4F-Arnch062h6Xaxo3Excd/exec"

# --- 2. LOGIKA PENANDATANGAN (BISA DIPILIH) ---
def get_approver_options(user_nama):
    info = DATABASE_INFO[user_nama]
    jabatan = info[1]
    
    atasan_list = [
        "Suwanto, SH., MH.", 
        "Wawan Setiawan, SH", 
        "Ineke Setiyaningsih, S.Sos", 
        "Farah Agustina Setiawati, SH", 
        "Rusma Ariati, SE"
    ]
    
    # Saran otomatis berdasarkan bagian
    idx = 0
    if "Teknis" in jabatan: idx = 1
    elif "Keuangan" in jabatan or "Logistik" in jabatan: idx = 2
    elif "Hukum" in jabatan or "SDM" in jabatan: idx = 3
    elif "Perencanaan" in jabatan or "Data" in jabatan: idx = 4
    
    if "Kepala Sub" in jabatan: idx = 0
    return atasan_list, idx

# --- 3. CSS CUSTOM ---
def inject_custom_css():
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 24px; }
        .stButton button { border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)

# --- 4. POP-UP MENU MANDIRI (DAPAT DIAKSES SEMUA ROLE) ---
@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    nip, jabatan, status_peg = info[0], info[1], info[4]
    
    tab_abs, tab_lap, tab_dl = st.tabs(["🚀 ABSEN", "📝 LAPKIN", "📥 DOWNLOAD"])
    
    with tab_abs:
        if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
            target_url = URL_API_PNS if status_peg == "PNS" else URL_API_PPPK
            payload = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": status_peg}
            with st.spinner("Mengirim..."):
                try:
                    res = requests.post(target_url, json=payload, timeout=10)
                    st.success("Presensi Berhasil!") if "Success" in res.text else st.error(res.text)
                except: st.error("Koneksi Gagal")

    with tab_lap:
        st.caption("Input Laporan Harian")
        stat = st.selectbox("Status:", ["HADIR", "IZIN", "TL", "CUTI"])
        uraian = st.text_area("Uraian Kegiatan:")
        if st.button("KIRIM LAPKIN", use_container_width=True):
            if uraian:
                payload = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": stat, "uraian": uraian}
                requests.post(URL_API_LAPKIN, json=payload)
                st.success("Terkirim!")
            else: st.warning("Isi uraian!")

    with tab_dl:
        bln = st.selectbox("Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        thn = st.selectbox("Tahun:", [2025, 2026], index=1)
        
        # FITUR: PILIHAN PENANDATANGAN
        list_atasan, def_idx = get_approver_options(user['nama'])
        ttd_pilih = st.selectbox("Pilih Penandatangan:", list_atasan, index=def_idx)
        
        if st.button("GENERATE EXCEL", use_container_width=True):
            st.info(f"Menyiapkan Laporan dengan TTD: {ttd_pilih}")
            # Logika Excel diletakkan di sini (BytesIO)

# --- 5. TAMPILAN DASHBOARD PER ROLE ---

# --- A. ROLE: PEGAWAI (MINIMALIS) ---
def show_pegawai(user):
    inject_custom_css()
    st.subheader(f"Halo, {user['nama']} 👋")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 ABSEN / HADIR", use_container_width=True, type="primary"):
            pop_menu_mandiri(user)
    with col2:
        if st.button("📝 ISI LAPKIN", use_container_width=True):
            pop_menu_mandiri(user)
            
    st.divider()
    st.caption("📊 Rekap Presensi Anda (Hari Ini)")
    tgl_now = datetime.now()
    data_log = process_attendance([URL_PNS, URL_PPPK], [user['nama']], tgl_now)
    render_monitoring_list([user['nama']], data_log)

# --- B. ROLE: ADMIN (FULL AKSES) ---
def show_admin(user, database):
    inject_custom_css()
    st.subheader("🏛️ Administrator Panel")
    
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True):
        pop_menu_mandiri(user)
        
    tab_mon, tab_user, tab_sys = st.tabs(["🔍 MONITORING", "👥 KELOLA USER", "⚙️ SISTEM"])
    
    with tab_mon:
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Pilih Tanggal:", datetime.now())
        search = c2.text_input("Cari Nama:")
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list([n for n in list(database.keys()) if search.lower() in n.lower()], data_log)

    with tab_user:
        st.write("🔑 **Data Login & Password Pegawai**")
        # Menampilkan tabel password (asumsi password default atau dari db)
        user_list = []
        for nama, info in database.items():
            user_list.append({"Nama": nama, "NIP": info[0], "Role": info[7] if len(info)>7 else "Pegawai", "Password": "kpuhss2026"})
        
        df_user = pd.DataFrame(user_list)
        st.dataframe(df_user, use_container_width=True)
        
        if st.button("Reset Semua Password ke Default"):
            st.warning("Fitur ini akan mereset kredensial sistem.")

# --- C. ROLE: BENDAHARA (SUB-ADMIN / REKAP) ---
def show_bendahara(user):
    inject_custom_css()
    st.subheader("💰 Menu Bendahara")
    
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True):
        pop_menu_mandiri(user)
        
    st.divider()
    st.write("📊 **Rekapitulasi Presensi Kantor**")
    tgl_rekap = st.date_input("Pilih Hari Rekap:", datetime.now())
    data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl_rekap)
    
    if st.button("📥 Unduh Rekap CSV"):
        df_rekap = pd.DataFrame.from_dict(data_log, orient='index')
        st.download_button("Klik Download", df_rekap.to_csv(), "rekap.csv")
    
    render_monitoring_list(list(DATABASE_INFO.keys()), data_log)

# --- 6. HELPER: RENDER LIST ---
def render_monitoring_list(list_nama, data_log):
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid {color};">
                <small>{p}</small> <br> <b>{d['m']} - {d['p']}</b> | <span style="color:{color}">{d['k']}</span>
            </div>
        """, unsafe_allow_html=True)
