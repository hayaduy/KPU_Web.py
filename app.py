import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from database import DATABASE_INFO
from dashboards import show_admin, show_bendahara, show_pegawai

# --- 1. KONFIGURASI COOKIES ---
# Pastikan password ini unik dan kuat
cookies = EncryptedCookieManager(password="kpu_hss_secret_key_2026_secure")

if not cookies.ready():
    st.stop()

# --- 2. INISIALISASI SESSION STATE ---
if 'logged_in' not in st.session_state:
    # Coba ambil data dari cookies (fitur Remember Me)
    saved_user = cookies.get("saved_user")
    saved_role = cookies.get("saved_role")
    
    if saved_user and saved_role:
        st.session_state.logged_in = True
        st.session_state.user = {"nama": saved_user, "role": saved_role}
    else:
        st.session_state.logged_in = False
        st.session_state.user = None

# --- 3. LOGIKA LOGIN ---
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login KPU HSS", page_icon="🏛️")
    
    # CSS agar tampilan login lebih rapi di tengah
    st.markdown("""
        <style>
        .stApp { max-width: 400px; margin: 0 auto; }
        </style>
    """, unsafe_allow_html=True)
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.title("🏛️ LOGIN KPU HSS")
    st.caption("Sistem Informasi Presensi & Lapkin")
    st.markdown("---")
    
    nip_input = st.text_input("Masukkan NIP", placeholder="Contoh: 1990xxxx")
    pwd_input = st.text_input("Password", type="password")
    remember_me = st.checkbox("Simpan Login (7 Hari)")
    
    if st.button("Masuk Sekarang", use_container_width=True, type="primary"):
        clean_nip = nip_input.replace(" ", "").strip()
        
        # Cari user berdasarkan NIP (NIP di indeks 0)
        match_nama = next((k for k, v in DATABASE_INFO.items() if clean_nip == str(v[0]).replace(" ", "").strip()), None)
        
        if match_nama:
            user_data = DATABASE_INFO[match_nama]
            
            # STRUKTUR DATABASE: [0:NIP, 1:Jabatan, 2:Unit, 3:Subbag, 4:Status, 5:Password, 6:Role]
            db_pwd = str(user_data[5]).strip() 
            role = str(user_data[6]).strip()
            
            if pwd_input == db_pwd:
                # Set Session
                st.session_state.logged_in = True
                st.session_state.user = {"nama": match_nama, "role": role}
                
                # Set Cookies jika Remember Me dicentang
                if remember_me:
                    cookies["saved_user"] = match_nama
                    cookies["saved_role"] = role
                    cookies.save()
                
                st.rerun()
            else:
                st.error("⚠️ Password yang Anda masukkan salah!")
        else:
            st.error("⚠️ NIP tidak ditemukan di database!")

else:
    # --- 4. ROUTER DASHBOARD (SESUAI ROLE) ---
    u = st.session_state.user
    
    # Sidebar Navigation & Profile
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=100)
    st.sidebar.markdown(f"### 👤 {u['nama']}")
    st.sidebar.info(f"Role: **{u['role']}**")
    
    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        # 1. Hapus Cookies
        if "saved_user" in cookies:
            del cookies["saved_user"]
        if "saved_role" in cookies:
            del cookies["saved_role"]
        cookies.save()
        
        # 2. Hapus Session
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
        st.rerun()

    # Jalankan Fungsi Dashboard (Diambil dari dashboards.py)
    try:
        if u['role'] == "Admin":
            show_admin(u, DATABASE_INFO)
        elif u['role'] == "Bendahara":
            show_bendahara(u)
        else:
            show_pegawai(u)
    except Exception as e:
        st.error(f"Gagal memuat dashboard: {e}")
