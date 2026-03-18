# app.py
import streamlit as st
from datetime import datetime
import pytz
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK
from dashboards import pop_update, view_admin, view_pegawai

st.set_page_config(page_title="KPU HSS Hub", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- CSS PREMIUM ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .employee-card { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 15px; border-radius: 10px; 
        margin-bottom: 10px; border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex; justify-content: space-between; align-items: center;
    }
    .status-hadir { color: #10B981; font-weight: bold; }
    .status-alpa { color: #EF4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
# --- 1. INISIALISASI SESSION STATE (WAJIB ADA DI ATAS) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 2. LOGIKA LOGIN ---
if not st.session_state.logged_in:
    st.title("🏛️ LOGIN KPU HSS")
    # ... isi kode login Abang (nip_in, pass_in, tombol login, dll) ...
    
    nip_in = st.text_input("Masukkan NIP")
    pass_in = st.text_input("Password", type="password")
    
    if st.button("LOGIN"):
        # Cari pegawai berdasarkan NIP (hilangkan spasi agar akurat)
        match = next((k for k, v in DATABASE_INFO.items() if nip_in.replace(" ","") in v[0].replace(" ","")), None)
        
        if match and pass_in == "kpuhss2026":
            # Sekarang variabel ini sudah aman untuk diisi
            st.session_state.logged_in = True
            
            # Ambil role dari kolom ke-8 (index 7), default 'Pegawai'
            u_data = DATABASE_INFO[match]
            u_role = u_data[7] if len(u_data) > 7 else "Pegawai"
            
            st.session_state.user = {"nama": match, "role": u_role}
            st.rerun()
        else:
            st.error("NIP atau Password Salah")
else:
    # --- 3. JIKA SUDAH LOGIN ---
    st.sidebar.write(f"Logged in as: **{st.session_state.user['nama']}**")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
        
    # Lanjutkan ke Dashboard
    role = st.session_state.user['role']
    if role == "Admin":
        st.title("DASHBOARD ADMIN")
    else:
        st.title("DASHBOARD PEGAWAI")
    # Sidebar Logout
    if st.sidebar.button("🚪 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # Dashboard Router
    role = st.session_state.user['role']
    tgl_now = datetime.now(wita_tz)
    
    if role == "Admin":
        st.title("🏛️ DASHBOARD ADMIN")
        # Contoh Render List
        data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl_now)
        for p in list(DATABASE_INFO.keys())[:5]: # Contoh 5 dulu
            d = data_log.get(p, {"m": "--", "p": "--", "k": "ALPA"})
            st.markdown(f'<div class="employee-card"><span>{p}</span><span class="status-hadir">{d["k"]}</span></div>', unsafe_allow_html=True)
    else:
        view_pegawai(st.session_state.user)
