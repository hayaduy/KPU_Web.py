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
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbJ_gHm4clqncelQOKDdHR6UK9wiTXgMNSqLMQnBBNVCg4F-Arnch062h6Xaxo3Excd/exec"

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
    
    # Saran otomatis berdasarkan deteksi kata kunci di Jabatan
    idx = 0
    if any(x in jabatan for x in ["Teknis", "Pemilu", "Humas"]): 
        idx = 1
    elif any(x in jabatan for x in ["Keuangan", "Umum", "Logistik"]): 
        idx = 2
    elif any(x in jabatan for x in ["Hukum", "SDM"]): 
        idx = 3
    elif any(x in jabatan for x in ["Perencanaan", "Data", "Informasi"]): 
        idx = 4
    
    # Jika yang login adalah Sekretaris atau Kasubbag, maka atasan default ke Sekretaris (Index 0)
    if "Sekretaris" in jabatan or "Kepala Sub" in jabatan: 
        idx = 0
        
    return atasan_list, idx

# --- 3. CSS CUSTOM ---
def inject_custom_css():
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 24px; }
        .stButton button { border-radius: 8px; }
        button[data-baseweb="tab"] { font-size: 14px; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

# --- 4. POP-UP MENU MANDIRI (DAPAT DIAKSES SEMUA ROLE) ---
@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    # NIP=index 0, Jabatan=index 1, Status=index 4
    nip, jabatan, status_peg = info[0], info[1], info[4]
    
    tab_abs, tab_lap, tab_dl = st.tabs(["🚀 ABSEN", "📝 LAPKIN", "📥 DOWNLOAD"])
    
    with tab_abs:
        st.write(f"Status: **{status_peg}**")
        if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
            target_url = URL_API_PNS if status_peg == "PNS" else URL_API_PPPK
            payload = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": status_peg}
            with st.spinner("Mengirim data presensi..."):
                try:
                    res = requests.post(target_url, json=payload, timeout=10)
                    if "Success" in res.text:
                        st.success("✅ Presensi Berhasil!")
                        st.balloons()
                    else:
                        st.error(f"Gagal: {res.text}")
                except Exception as e:
                    st.error(f"Kesalahan Koneksi: {e}")

    with tab_lap:
        st.caption("Input Laporan Kinerja Harian")
        stat = st.selectbox("Status Kehadiran:", ["HADIR", "IZIN", "TL", "CUTI"])
        uraian = st.text_area("Uraian Kegiatan:", placeholder="Tuliskan apa yang Anda kerjakan hari ini...")
        if st.button("KIRIM LAPKIN", use_container_width=True):
            if uraian.strip():
                payload = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": stat, "uraian": uraian}
                with st.spinner("Mengirim laporan..."):
                    try:
                        res = requests.post(URL_API_LAPKIN, json=payload, timeout=10)
                        st.success("✅ Laporan Terkirim!")
                    except:
                        st.error("Gagal terhubung ke server.")
            else:
                st.warning("Silakan isi uraian kegiatan!")

    with tab_dl:
        st.caption("Download Laporan Bulanan Format Excel")
        bln = st.selectbox("Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        thn = st.selectbox("Tahun:", [2025, 2026], index=1)
        
        # FITUR: PILIHAN PENANDATANGAN (BISA DIPILIH)
        list_atasan, def_idx = get_approver_options(user['nama'])
        ttd_pilih = st.selectbox("Konfirmasi Penandatangan (Atasan):", list_atasan, index=def_idx)
        
        if st.button("PROSES & UNDUH EXCEL", use_container_width=True, type="primary"):
            st.info(f"Dokumen sedang disiapkan dengan TTD: {ttd_pilih}")
            # Logika pembentukan file Excel (BytesIO) akan memanggil template sesuai format KPU

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
    # Menampilkan rekap khusus untuk user yang login
    data_log = process_attendance([URL_PNS, URL_PPPK], [user['nama']], tgl_now)
    render_monitoring_list([user['nama']], data_log)

# --- B. ROLE: ADMIN (FULL AKSES) ---
def show_admin(user, database):
    inject_custom_css()
    st.subheader("🏛️ Administrator Panel")
    
    if st.button("📂 BUKA MENU MANDIRI SAYA", use_container_width=True):
        pop_menu_mandiri(user)
        
    tab_mon, tab_user, tab_sys = st.tabs(["🔍 MONITORING", "👥 KELOLA USER", "⚙️ SISTEM"])
    
    with tab_mon:
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Pilih Tanggal Pemantauan:", datetime.now())
        search = c2.text_input("🔍 Cari Nama Pegawai:")
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        
        filtered_names = [n for n in list(database.keys()) if search.lower() in n.lower()]
        render_monitoring_list(filtered_names, data_log)

    with tab_user:
        st.write("🔑 **Data Kredensial & Password Pegawai**")
        user_list = []
        for nama, info in database.items():
            # Index 0=NIP, 2=Password, 3=Role, 4=Status
            user_list.append({
                "Nama": nama, 
                "NIP": info[0], 
                "Role": info[3].upper(), 
                "Password": info[2],
                "Status": info[4]
            })
        
        df_user = pd.DataFrame(user_list)
        st.dataframe(df_user, use_container_width=True)
        
        if st.button("🔄 Reset Semua Password ke Default"):
            st.warning("Fitur ini memerlukan akses database write.")

# --- C. ROLE: BENDAHARA (SUB-ADMIN / REKAP) ---
def show_bendahara(user):
    inject_custom_css()
    st.subheader("💰 Menu Bendahara")
    
    if st.button("📂 BUKA MENU MANDIRI SAYA", use_container_width=True):
        pop_menu_mandiri(user)
        
    st.divider()
    st.write("📊 **Rekapitulasi Presensi Seluruh Pegawai**")
    tgl_rekap = st.date_input("Pilih Hari Rekap:", datetime.now())
    data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl_rekap)
    
    if st.button("📥 Unduh Rekap CSV (Untuk Tunjangan)"):
        df_rekap = pd.DataFrame.from_dict(data_log, orient='index')
        st.download_button("Klik untuk Download File", df_rekap.to_csv(), f"rekap_absen_{tgl_rekap}.csv")
    
    render_monitoring_list(list(DATABASE_INFO.keys()), data_log)

# --- 6. HELPER: RENDER LIST ---
def render_monitoring_list(list_nama, data_log):
    if not list_nama:
        st.caption("Data tidak ditemukan.")
        return
        
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        # Warna indikator: Hijau jika HADIR, Merah jika ALPA/Lainnya
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <small style="color:#888;">{DATABASE_INFO[p][1]}</small><br>
                        <b>{p}</b>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-family:monospace;">{d['m']} - {d['p']}</span><br>
                        <span style="color:{color}; font-size:11px; font-weight:bold;">{d['k']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
