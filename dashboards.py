import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. KONFIGURASI SEMUA URL ENDPOINT ---
URL_API_PNS = "https://script.google.com/macros/s/AKfycbxjZ8flZ-x_swbHDN4QtCLmLXaNixEej9vpJFWr74ilkLyvnxkjuFhmMsfz10EGnS8aAQ/exec"
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbzfBtzxkav_uDsJcKv-nTO5i8Yt_AebAxSCEJ6HRKfqXJOJ0FL7e5easfQT7fd-LZ1A/exec"
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbzJ_gHm4clqncelQOKDdHR6UK9wiTXgMNSqLMQnBBNVCg4F-Arnch062h6Xaxo3Excd/exec"

# --- 2. CSS CUSTOM ---
def inject_custom_css():
    st.markdown("""
        <style>
        button[data-baseweb="tab"] { font-size: 14px; font-weight: 600; flex: 1; text-align: center; }
        button[data-baseweb="tab"] div p { margin: 0 auto; }
        div[data-baseweb="tab-highlight"] { background-color: #EF4444; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. POP-UP MENU MANDIRI (ABSEN & LAPKIN) ---
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
        
        with st.spinner("Mengirim data absen..."):
            try:
                res = requests.post(target_url, json=payload_absen, timeout=10)
                if "Success" in res.text:
                    st.success(f"✅ Absen Berhasil!")
                    st.balloons()
                else:
                    st.error(f"Gagal: {res.text}")
            except Exception as e:
                st.error(f"Ralat Sambungan: {e}")

    st.markdown("---")
    
    # --- SEKSI LAPKIN (DENGAN DROPDOWN STATUS) ---
    st.subheader("📝 Laporan Kinerja (LAPKIN)")
    
    # Tambahan Dropdown Status sesuai permintaan
    status_lapkin = st.selectbox(
        "Status Kehadiran Lapkin:",
        ["HADIR", "IZIN", "TL", "CUTI"],
        index=0
    )
    
    uraian = st.text_area("Huraian Aktiviti Hari Ini:", placeholder="Contoh: Mengemaskini data logistik pilihan raya...")
    
    if st.button("HANTAR LAPORAN KINERJA", use_container_width=True):
        if uraian.strip():
            # Data JSON dikirim ke Apps Script
            payload_lapkin = {
                "nama": user['nama'], 
                "nip": nip, 
                "jabatan": jabatan, 
                "status": status_lapkin, # Status dari dropdown dikirim di sini
                "uraian": uraian
            }
            with st.spinner("Menghantar laporan ke Google Sheets..."):
                try:
                    res = requests.post(URL_API_LAPKIN, json=payload_lapkin, timeout=10)
                    if "Success" in res.text:
                        st.success(f"✅ Laporan Berhasil Dikirim (Status: {status_lapkin})!")
                        st.balloons()
                    else:
                        st.error(f"Gagal menghantar: {res.text}")
                except Exception as e:
                    st.error(f"Ralat Sambungan: {e}")
        else:
            st.warning("Sila isi huraian aktiviti terlebih dahulu!")

# --- 4. TAMPILAN DASHBOARD (SAMA SEPERTI SEBELUMNYA) ---
def render_monitoring_list(list_nama, data_log):
    if not list_nama:
        st.caption("Nama tidak dijumpai...")
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
    st.markdown("### 📱 Hub Pegawai")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)

def show_admin(user, database):
    inject_custom_css()
    st.markdown("### 🏛️ Hub Administrator")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    tab_mon, tab_down, tab_set = st.tabs(["🔍 MONITORING", "📥 DOWNLOAD", "🔑 SETTINGS"])
    with tab_mon:
        c1, c2 = st.columns([1, 1])
        tgl = c1.date_input("Tarikh Pantau:", datetime.now())
        search = c2.text_input("🔍 Cari Nama Pegawai:")
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list([n for n in list(database.keys()) if search.lower() in n.lower()], data_log)

def show_bendahara(user):
    inject_custom_css()
    st.markdown("### 💰 Hub Bendahara")
    if st.button("📂 BUKA MENU MANDIRI", use_container_width=True, type="primary"):
        pop_menu_mandiri(user)
    st.divider()
    st.button("📥 Muat Turun Rekap Absen Kantor", use_container_width=True)
