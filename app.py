import streamlit as st
from database import DATABASE_INFO
from dashboards import show_admin, show_bendahara, show_pegawai
from streamlit_cookies_manager import EncryptedCookieManager
import os

# --- KONFIGURASI COOKIES ---
# Ganti 'secret_password_anda' dengan kata kunci bebas untuk enkripsi
cookies = EncryptedCookieManager(password="kpu_hss_secret_key_2026")
if not cookies.ready():
    st.stop()

# --- INISIALISASI SESSION STATE ---
if 'logged_in' not in st.session_state:
    # Cek apakah ada data login di cookies browser
    saved_user = cookies.get("saved_user")
    saved_role = cookies.get("saved_role")
    
    if saved_user and saved_role:
        st.session_state.logged_in = True
        st.session_state.user = {"nama": saved_user, "role": saved_role}
    else:
        st.session_state.logged_in = False
        st.session_state.user = None

# --- LOGIKA LOGIN ---
if not st.session_state.logged_in:
    st.title("🏛️ LOGIN KPU HSS")
    st.markdown("---")
    
    nip = st.text_input("Masukkan NIP")
    pwd = st.text_input("Password", type="password")
    remember_me = st.checkbox("Simpan Login (7 Hari)")
    
    if st.button("Masuk", use_container_width=True):
        # Pembersihan spasi NIP agar akurat
        clean_nip = nip.replace(" ", "")
        match = next((k for k, v in DATABASE_INFO.items() if clean_nip in v[0].replace(" ", "")), None)
        
        if match and pwd == "kpuhss2026":
            role = DATABASE_INFO[match][7] if len(DATABASE_INFO[match]) > 7 else "Pegawai"
            
            # Set Session State
            st.session_state.logged_in = True
            st.session_state.user = {"nama": match, "role": role}
            
            # Jika checkbox dicentang, simpan ke Cookies Browser
            if remember_me:
                cookies["saved_user"] = match
                cookies["saved_role"] = role
                cookies.save()
            
            st.rerun()
        else:
            st.error("⚠️ NIP atau Password salah!")

else:
    # --- ROUTER DASHBOARD ---
    u = st.session_state.user
    
    # Sidebar Info
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=100)
    st.sidebar.write(f"👤 **{u['nama']}**")
    st.sidebar.caption(f"Role: {u['role']}")
    
    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        # Hapus Session & Hapus Cookies
        st.session_state.logged_in = False
        st.session_state.user = None
        if "saved_user" in cookies:
            del cookies["saved_user"]
            del cookies["saved_role"]
            cookies.save()
        st.rerun()

    st.markdown("---")

    # Jalankan Dashboard sesuai Role
    if u['role'] == "Admin":
        show_admin(u, DATABASE_INFO)
    elif u['role'] == "Bendahara":
        show_bendahara(u)
    else:
        show_pegawai(u)
