import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. KONFIGURASI SEMUA URL ENDPOINT ---
URL_API_PNS = "https://script.google.com/macros/s/AKfycbyWJbg_KceQroTV51pFuM30Ij-K4VwynhjK9NI2R-VBYrLJEA1rh7prec4MvNiKBUJV/exec"
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbwWKNLcFa06rxdCSbr1Ex-6dTUzjxJndEfF_bnBZx0oPOevtXqB6H3nUttupzE2D9yn/exec"
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbzJ_gHm4clqncelQOKDdHR6UK9wiTXgMNSqLMQnBBNVCg4F-Arnch062h6Xaxo3Excd/exec"

# --- 2. LOGIKA PENENTUAN PENANDATANGAN (APPROVAL) ---
def get_approver(user_nama):
    """Logika menentukan siapa yang tanda tangan di bawah laporan"""
    info = DATABASE_INFO[user_nama]
    jabatan = info[1]
    
    # Ambil Nama Sekretaris sebagai otoritas tertinggi
    sekretaris = "Suwanto, SH., MH."
    nip_sekretaris = DATABASE_INFO[sekretaris][0]
    
    # 1. Jika Sekretaris atau Kasubbag -> Tanda Tangan Sekretaris
    if "Sekretaris" in jabatan or "Kepala Sub" in jabatan:
        return sekretaris, nip_sekretaris, "Sekretaris"
    
    # 2. Jika Staf -> Tanda Tangan Kasubbag sesuai bagiannya
    if "Teknis" in jabatan: kasubbag = "Wawan Setiawan, SH"
    elif "Keuangan" in jabatan or "Logistik" in jabatan: kasubbag = "Ineke Setiyaningsih, S.Sos"
    elif "Hukum" in jabatan or "SDM" in jabatan: kasubbag = "Farah Agustina Setiawati, SH"
    elif "Perencanaan" in jabatan or "Data" in jabatan: kasubbag = "Rusma Ariati, SE"
    else: kasubbag = sekretaris # Fallback jika bagian tidak spesifik
    
    return kasubbag, DATABASE_INFO[kasubbag][0], DATABASE_INFO[kasubbag][1]

# --- 3. CSS CUSTOM ---
def inject_custom_css():
    st.markdown("""
        <style>
        button[data-baseweb="tab"] { font-size: 14px; font-weight: 600; flex: 1; text-align: center; }
        button[data-baseweb="tab"] div p { margin: 0 auto; }
        div[data-baseweb="tab-highlight"] { background-color: #EF4444; }
        </style>
    """, unsafe_allow_html=True)

# --- 4. POP-UP MENU MANDIRI (ABSEN, LAPKIN, & DOWNLOAD) ---
@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    nip, jabatan, status_peg = info[0], info[1], info[4]
    
    st.write(f"Pegawai: **{user['nama']}**")
    st.caption(f"{status_peg} | {jabatan}")
    st.divider()
    
    # --- SEKSI ABSENSI ---
    st.subheader("🚀 Presensi Harian")
    if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
        target_url = URL_API_PNS if status_peg == "PNS" else URL_API_PPPK
        payload_absen = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": status_peg}
        
        with st.spinner("Mengirim data presensi..."):
            try:
                res = requests.post(target_url, json=payload_absen, timeout=10)
                if "Success" in res.text:
                    st.success(f"✅ Presensi Berhasil!")
                    st.balloons()
                else:
                    st.error(f"Gagal: {res.text}")
            except Exception as e:
                st.error(f"Kesalahan Koneksi: {e}")

    st.markdown("---")
    
    # --- SEKSI LAPKIN ---
    st.subheader("📝 Laporan Kinerja (LAPKIN)")
    status_lapkin = st.selectbox("Status Kehadiran Lapkin:", ["HADIR", "IZIN", "TL", "CUTI"], index=0)
    uraian = st.text_area("Uraian Kegiatan Hari Ini:", placeholder="Contoh: Mengelola data logistik pemilihan umum...")
    
    if st.button("KIRIM LAPORAN KINERJA", use_container_width=True):
        if uraian.strip():
            payload_lapkin = {
                "nama": user['nama'], "nip": nip, "jabatan": jabatan, 
                "status": status_lapkin, "uraian": uraian
            }
            with st.spinner("Mengirim laporan ke Google Sheets..."):
                try:
                    res = requests.post(URL_API_LAPKIN, json=payload_lapkin, timeout=10)
                    if "Success" in res.text:
                        st.success(f"✅ Laporan Berhasil Dikirim!")
                        st.balloons()
                    else:
                        st.error(f"Gagal mengirim: {res.text}")
                except Exception as e:
                    st.error(f"Kesalahan Koneksi: {e}")
        else:
            st.warning("Silakan isi uraian kegiatan terlebih dahulu!")

    st.markdown("---")

    # --- SEKSI UNDUH LAPORAN (FITUR BARU) ---
    st.subheader("📥 Unduh Laporan Bulanan")
    st.caption("Generate dokumen Excel laporan bulanan sesuai periode.")
    c1, c2 = st.columns(2)
    with c1:
        bln_pilih = st.selectbox("Pilih Bulan:", 
            ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
             "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
    with c2:
        thn_pilih = st.selectbox("Pilih Tahun:", [2025, 2026], index=1)

    if st.button("PROSES LAPORAN (EXCEL)", use_container_width=True):
        with st.spinner("Menyiapkan dokumen..."):
            # Panggil logika penandatangan otomatis
            ttd_nama, ttd_nip, ttd_jabatan = get_approver(user['nama'])
            
            st.info(f"Penandatangan Dokumen: **{ttd_nama}**\n\nJabatan: {ttd_jabatan}")
            # Placeholder untuk fungsi download selanjutnya
            st.warning("Sistem sedang menghubungkan data ke template Excel.")

# --- 5. TAMPILAN DASHBOARD ---
def render_monitoring_list(list_nama, data_log):
    if not list_nama:
        st.caption("Nama tidak ditemukan...")
        return
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#F59E0B" if d['k'] == "TERLAMBAT" else "#EF4444"
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; margin-bottom:8px; border-left:5px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><small style="color:#888;">{DATABASE_INFO[p][1]}</small><br><span style="font-weight:600;">{p}</span></div>
                    <div style="text-align:right; font-family:monospace;"><span style="font-size:12px;">{d['m']} - {d['p']}</span><br><span style="color:{color}; font-size:10px; font-weight:bold;">{d['k']}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_pegawai(user):
    st.markdown("### 📱 Menu Pegawai")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)

def show_admin(user, database):
    inject_custom_css()
    st.markdown("### 🏛️ Menu Administrator")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    tab_mon, tab_down, tab_set = st.tabs(["🔍 MONITORING", "📥 UNDUH DATA", "🔑 PENGATURAN"])
    with tab_mon:
        c1, c2 = st.columns([1, 1])
        tgl = c1.date_input("Tanggal Pemantauan:", datetime.now())
        search = c2.text_input("🔍 Cari Nama Pegawai:")
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list([n for n in list(database.keys()) if search.lower() in n.lower()], data_log)

def show_bendahara(user):
    inject_custom_css()
    st.markdown("### 💰 Menu Bendahara")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    st.button("📥 Unduh Rekap Presensi Kantor", use_container_width=True)
