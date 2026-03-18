import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v111.0", layout="wide", page_icon="🏛️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = None

# --- 2. CONFIGURATION ---
SHEET_ID = "1Gn7DKaT71-ePG7uQPdWOgrKiKZK5qTXWrolXQRIs4s4"
URL_SCRIPT_AUTH = "https://script.google.com/macros/s/AKfycbxUQjn_F4S1PCVvNAekKqo-vWzgHMFn81ri3VOMWTgbTe_nDmOrb9NLbd41UjQZ5npl/exec"

# --- 3. FUNGSI AMBIL DATA (ROBUST VERSION) ---
def load_auth_db():
    export_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        response = requests.get(f"{export_url}&t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            # Baca data mentah
            raw_data = StringIO(response.text)
            df = pd.read_csv(raw_data)
            
            # Hapus baris yang semuanya kosong
            df = df.dropna(how='all')
            
            # Pastikan minimal ada 3-4 kolom (Nama, NIP, Pass)
            if len(df.columns) < 3:
                st.error(f"Kolom di sheet terdeteksi cuma {len(df.columns)}. Minimal harus 3 (Nama, NIP, Password).")
                return pd.DataFrame()

            # PAKSA penamaan kolom berdasarkan posisi agar tidak KeyError lagi
            # Kolom 0 = Nama, Kolom 1 = NIP, Kolom 2 = Password, Kolom 3 = Role (opsional)
            cols_mapping = {df.columns[0]: 'Nama', df.columns[1]: 'NIP', df.columns[2]: 'Password'}
            if len(df.columns) >= 4:
                cols_mapping[df.columns[3]] = 'Role'
            
            df = df.rename(columns=cols_mapping)
            
            # Bersihkan NIP (hapus spasi, pastikan string)
            df['NIP'] = df['NIP'].astype(str).str.strip().str.replace(".0", "", regex=False)
            df['Password'] = df['Password'].astype(str).str.strip()
            
            return df
        else:
            st.error("Gagal terhubung ke Google Sheets.")
    except Exception as e:
        st.error(f"Error Database: {e}")
    return pd.DataFrame()

# --- 4. TAMPILAN LOGIN ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:#F59E0B;'>🏛️ LOGIN KPU HSS</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            u_in = st.text_input("Username / NIP")
            p_in = st.text_input("Password", type="password")
            
            if st.button("MASUK SISTEM", use_container_width=True):
                if u_in and p_in:
                    with st.spinner("Mengecek Database..."):
                        df_u = load_auth_db()
                        if not df_u.empty:
                            # Cari NIP yang cocok
                            user_nip = str(u_in).strip()
                            match = df_u[df_u['NIP'] == user_nip]
                            
                            if not match.empty:
                                db_pass = str(match.iloc[0]['Password'])
                                if str(p_in).strip() == db_pass:
                                    st.session_state.logged_in = True
                                    st.session_state.user_data = match.iloc[0].to_dict()
                                    st.rerun()
                                else:
                                    st.error("❌ Password Salah!")
                            else:
                                st.error(f"❓ NIP '{user_nip}' tidak ditemukan.")
                                # Opsional: st.write("Data NIP di Sheet:", df_u['NIP'].tolist()) # Debug
                else:
                    st.warning("Isi NIP dan Password dulu, Bang!")
    st.stop()

# --- 5. DASHBOARD ---
u = st.session_state.user_data
st.title(f"🏛️ Selamat Datang, {u.get('Nama', 'Pegawai')}")
st.success(f"Berhasil Login sebagai {u.get('Role', 'User')}")

if st.button("🚪 LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
