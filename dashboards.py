import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. KONFIGURASI SEMUA URL ENDPOINT ---
# URL Absen PNS
URL_API_PNS = "https://script.google.com/macros/s/AKfycbxjZ8flZ-x_swbHDN4QtCLmLXaNixEej9vpJFWr74ilkLyvnxkjuFhmMsfz10EGnS8aAQ/exec"
# URL Absen PPPK
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbzfBtzxkav_uDsJcKv-nTO5i8Yt_AebAxSCEJ6HRKfqXJOJ0FL7e5easfQT7fd-LZ1A/exec"
# URL Lapkin (PNS & PPPK masuk ke sini)
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbysGislOC0219H1_sqib7TblYTTUngiYYIzaUtLG4_tEfxUl6OsnYLzjvqpj1POCRc/exec"

# --- 2. CSS CUSTOM (TAB CENTER & KPU RED) ---
def inject_custom_css():
    st.markdown("""
        <style>
        /* Membuat Label Tab Rata Tengah & Lebar Sama */
        button[data-baseweb="tab"] {
            font-size: 14px; font-weight: 600; flex: 1; text-align: center;
        }
        button[data-baseweb="tab"] div p { margin: 0 auto; }
        
        /* Garis Bawah Tab Aktif Warna Merah KPU */
        div[data-baseweb="tab-highlight"] { background-color: #EF4444; }
        
        /* Efek Hover */
        button[data-baseweb="tab"]:hover {
            background-color: rgba(255, 255, 255, 0.05); border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI RENDER LIST MONITORING (VISUAL CARD) ---
def render_monitoring_list(list_nama, data_log):
    if not list_nama:
        st.caption("Nama tidak ditemukan...")
        return
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        # Warna indikator status
        color = "#10B981" if d['k'] == "HADIR" else "#F59E0B" if d['k'] == "TERLAMBAT" else "#EF4444"
        
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; margin-bottom:8px; border-left:5px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <small style="color:#888;">{DATABASE_INFO[p][1]}</small><br>
                        <span style="font-weight:600;">{p}</span>
                    </div>
                    <div style="text-align:right; font-family:monospace;">
                        <span style="font-size:12px;">{d['m']} - {d['p']}</span><br>
                        <span style="color:{color}; font-size:10px; font-weight:bold;">{d['k']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 4. POP-UP MENU MANDIRI (ABSEN & LAPKIN) ---
@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    nip, jabatan, status_peg = info[0], info[1], info[4]
    
    st.write(f"Pegawai: **{user['nama']}**")
    st.caption(f"{status_peg} | {jabatan}")
    st.divider()
    
    # SEKSI ABSENSI
    st.subheader("🚀 Presensi Harian")
    if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
        target_url = URL_API_PNS if status_peg == "PNS" else URL_API_PPPK
        payload_absen = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": status_peg}
        
        with st.spinner("Mengirim data absen..."):
            try:
                res = requests.post(target_url, json=payload_absen, timeout=10)
                if "Success" in res.text:
                    st.success(f"✅ Absen {status_peg} Berhasil Dicatat!")
                    st.balloons()
                else:
                    st.error(f"Gagal: {res.text}")
            except Exception as e:
                st.error(f"Koneksi Error: {e}")

    st.markdown("---")
    
    # SEKSI LAPKIN
    st.subheader("📝 Laporan Kinerja")
    uraian = st.text_area("Uraian Kegiatan Hari Ini:", placeholder="Ketik rincian pekerjaan Anda di sini...")
    
    if st.button("KIRIM LAPORAN KINERJA", use_container_width=True):
        if uraian.strip():
            payload_lapkin = {
                "nama": user['nama'], 
                "nip": nip, 
                "jabatan": jabatan, 
                "uraian": uraian
            }
            with st.spinner("Mengirim laporan ke Google Sheets..."):
                try:
                    res = requests.post(URL_API_LAPKIN, json=payload_lapkin, timeout=10)
                    if "Success" in res.text:
                        st.success("✅ Laporan Kinerja Berhasil Terkirim!")
                    else:
                        st.error("Gagal mengirim laporan.")
                except Exception as e:
                    st.error(f"Koneksi Error: {e}")
        else:
            st.warning("Mohon isi uraian kegiatan terlebih dahulu!")

# --- 5. TAMPILAN DASHBOARD PER ROLE ---

def show_pegawai(user):
    st.markdown("### 📱 Hub Pegawai")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    st.info("Gunakan tombol di atas untuk melakukan Absensi dan mengisi Laporan Kinerja (Lapkin).")

def show_bendahara(user):
    inject_custom_css()
    st.markdown("### 💰 Hub Bendahara")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    t1, t2 = st.tabs(["📊 DATA KANTOR", "📥 DOWNLOAD"])
    with t1:
        st.write("Gunakan data ini untuk verifikasi kehadiran pegawai.")
    with t2:
        st.button("📥 Download Rekap Absen Kantor (Excel)", use_container_width=True)

def show_admin(user, database):
    inject_custom_css()
    st.markdown("### 🏛️ Hub Administrator")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    
    tab_mon, tab_down, tab_set = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD", "🔑 SETTINGS"])
    
    with tab_mon:
        c1, c2 = st.columns([1, 1])
        tgl = c1.date_input("Tanggal Pantau:", datetime.now())
        search = c2.text_input("🔍 Cari Nama Pegawai:")
        
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        s1, s2, s3 = st.tabs(["SEMUA", "PNS", "PPPK"])
        
        with s1:
            render_monitoring_list([n for n in list(database.keys()) if search.lower() in n.lower()], data_log)
        with s2:
            render_monitoring_list([n for n in MASTER_PNS if search.lower() in n.lower()], data_log)
        with s3:
            render_monitoring_list([n for n in MASTER_PPPK if search.lower() in n.lower()], data_log)

    with tab_down:
        st.subheader("Pusat Unduhan Kolektif")
        st.button("📥 Download Rekap Absen Bulanan", use_container_width=True)

    with tab_set:
        st.subheader("Manajemen Akun")
        target = st.selectbox("Pilih Pegawai untuk Reset:", list(database.keys()))
        if st.button(f"Reset Password {target}", use_container_width=True):
            st.success(f"Password {target} dikembalikan ke default.")
