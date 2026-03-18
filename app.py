import streamlit as st
from database import DATABASE_INFO
from dashboards import show_admin, show_bendahara, show_pegawai

# --- INISIALISASI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIKA LOGIN ---
if not st.session_state.logged_in:
    st.title("🏛️ LOGIN KPU HSS")
    nip = st.text_input("NIP")
    pwd = st.text_input("Password", type="password")
    if st.button("Masuk"):
        match = next((k for k, v in DATABASE_INFO.items() if nip.replace(" ","") in v[0].replace(" ","")), None)
        if match and pwd == "kpuhss2026":
            st.session_state.logged_in = True
            role = DATABASE_INFO[match][7] if len(DATABASE_INFO[match]) > 7 else "Pegawai"
            st.session_state.user = {"nama": match, "role": role}
            st.rerun()
else:
    # --- ROUTER DASHBOARD ---
    u = st.session_state.user
    if u['role'] == "Admin":
        show_admin(u, DATABASE_INFO)
    elif u['role'] == "Bendahara":
        show_bendahara(u)
    else:
        show_pegawai(u)
    
    if st.sidebar.button("Keluar"):
        st.session_state.logged_in = False
        st.rerun()
