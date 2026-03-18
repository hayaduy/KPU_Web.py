import streamlit as st
from database import DATABASE_INFO
# PERBAIKAN: Ubah 'dashboards' menjadi 'dashboard' agar sesuai nama file
from dashboards import show_admin, show_bendahara, show_pegawai
from streamlit_cookies_manager import EncryptedCookieManager
import os

# --- 1. KONFIGURASI COOKIES ---
cookies = EncryptedCookieManager(password="kpu_hss_secret_key_2026")
if not cookies.ready():
    st.stop()

# --- 2. INISIALISASI SESSION STATE ---
if 'logged_in' not in st.session_state:
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
    st.title("🏛️ LOGIN KPU HSS")
    st.markdown("---")
    
    nip = st.text_input("Masukkan NIP")
    pwd = st.text_input("Password", type="password")
    remember_me = st.checkbox("Simpan Login (7 Hari)")
    
    if st.button("Masuk", use_container_width=True):
        clean_nip = nip.replace(" ", "")
        
        # Cari user berdasarkan NIP (NIP di indeks 0)
        match = next((k for k, v in DATABASE_INFO.items() if clean_nip in v[0].replace(" ", "")), None)
        
        if match:
            user_data = DATABASE_INFO[match]
            
            # --- PERBAIKAN INDEKS DATABASE ---
            # Berdasarkan struktur: [0:NIP, 1:Jabatan, 2:Unit, 3:Subbag, 4:Status, 5:Password, 6:Role]
            db_pwd = str(user_data[5]) # Password ada di indeks 5
            role = str(user_data[6]).strip().title() # Role ada di indeks 6
            
            if pwd == db_pwd:
                st.session_state.logged_in = True
                st.session_state.user = {"nama": match, "role": role}
                
                if remember_me:
                    cookies["saved_user"] = match
                    cookies["saved_role"] = role
                    cookies.save()
                
                st.rerun()
            else:
                st.error("⚠️ Password salah!")
        else:
            st.error("⚠️ NIP tidak terdaftar!")

else:
    # --- 4. ROUTER DASHBOARD ---
    u = st.session_state.user
    
    # Sidebar Info
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=100)
    st.sidebar.write(f"👤 **{u['nama']}**")
    st.sidebar.caption(f"Role: {u['role']}")
    
    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        # Bersihkan session & cookies
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if "saved_user" in cookies:
            del cookies["saved_user"]
            del cookies["saved_role"]
            cookies.save()
        st.rerun()

    # Jalankan Dashboard sesuai Role
    if u['role'] == "Admin":
        show_admin(u, DATABASE_INFO)
    elif u['role'] == "Bendahara":
        show_bendahara(u)
    else:
        show_pegawai(u)
