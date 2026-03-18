import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from database import DATABASE_INFO
from dashboards import show_admin, show_bendahara, show_pegawai

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem KPU HSS", page_icon="🏛️", layout="centered")

# --- 2. KONFIGURASI COOKIES ---
# Gunakan password yang konsisten agar user tidak ter-logout otomatis saat deploy ulang
cookies = EncryptedCookieManager(password="kpu_hss_secret_key_2026_secure")

if not cookies.ready():
    st.stop()

# --- 3. INISIALISASI SESSION STATE ---
if 'logged_in' not in st.session_state:
    saved_user = cookies.get("saved_user")
    saved_role = cookies.get("saved_role")
    
    if saved_user and saved_role:
        st.session_state.logged_in = True
        st.session_state.user = {"nama": saved_user, "role": saved_role}
    else:
        st.session_state.logged_in = False
        st.session_state.user = None

# --- 4. LOGIKA LOGIN ---
if not st.session_state.logged_in:
    # CSS Custom untuk Login Box
    st.markdown("""
        <style>
        .stApp { max-width: 450px; margin: 0 auto; }
        .login-header { text-align: center; margin-bottom: 30px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-header'>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=90)
    st.title("🏛️ LOGIN KPU HSS")
    st.caption("Aplikasi Presensi & Laporan Kinerja Mandiri")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    nip_input = st.text_input("Masukkan NIP", placeholder="Contoh: 1990xxxx")
    pwd_input = st.text_input("Password", type="password", placeholder="******")
    remember_me = st.checkbox("Simpan Login (7 Hari)")
    
    if st.button("Masuk", use_container_width=True, type="primary"):
        clean_nip = nip_input.replace(" ", "").strip()
        
        # Cari user berdasarkan NIP (NIP di indeks 0)
        match_nama = next((k for k, v in DATABASE_INFO.items() if clean_nip == str(v[0]).replace(" ", "").strip()), None)
        
        if match_nama:
            user_data = DATABASE_INFO[match_nama]
            
            # --- PROTEKSI INDEX ERROR ---
            # Kita cek dulu apakah jumlah data dalam list [...] cukup (minimal 7 item)
            # Indeks: [0:NIP, 1:Jabatan, 2:Unit, 3:Subbag, 4:Status, 5:Password, 6:Role]
            if len(user_data) >= 7:
                db_pwd = str(user_data[5]).strip() 
                role = str(user_data[6]).strip().title() # Menghindari error huruf besar/kecil
                
                if pwd_input == db_pwd:
                    st.session_state.logged_in = True
                    st.session_state.user = {"nama": match_nama, "role": role}
                    
                    if remember_me:
                        cookies["saved_user"] = match_nama
                        cookies["saved_role"] = role
                        cookies.save()
                    
                    st.success("Berhasil masuk! Mengalihkan...")
                    st.rerun()
                else:
                    st.error("⚠️ Password salah!")
            else:
                # Jika data di database.py kurang dari 7 item
                st.error(f"⚠️ Data `{match_nama}` tidak lengkap! Ditemukan {len(user_data)} kolom, butuh minimal 7 kolom (NIP s/d Role).")
                with st.expander("Detail Error untuk Developer"):
                    st.write(f"Isi data saat ini: {user_data}")
        else:
            st.error("⚠️ NIP tidak ditemukan!")

else:
    # --- 5. ROUTER DASHBOARD (SESUAI ROLE) ---
    u = st.session_state.user
    
    # Sidebar Profile & Logout
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/46/KPU_Logo.svg", width=80)
    st.sidebar.markdown(f"### 👤 {u['nama']}")
    st.sidebar.caption(f"📍 Role: {u['role']}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        if "saved_user" in cookies: del cookies["saved_user"]
        if "saved_role" in cookies: del cookies["saved_role"]
        cookies.save()
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Jalankan Dashboard dengan penanganan Error
    try:
        if u['role'] == "Admin":
            show_admin(u, DATABASE_INFO)
        elif u['role'] == "Bendahara":
            show_bendahara(u)
        else:
            show_pegawai(u)
    except Exception as e:
        st.error(f"❌ Error Dashboard: {e}")
        st.info("Saran: Pastikan fungsi dashboard sudah di-import dengan benar.")
