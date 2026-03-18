import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import pytz
import time
from math import radians, cos, sin, asin, sqrt

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v132.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- 2. DATABASE LOGIN (Sesuai File CSV) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "197205212009121001": {"nama": "Suwanto, SH., MH.", "pass": "kpuhss2026", "role": "ADMIN"},
        "198606012010121004": {"nama": "Wawan Setiawan, SH", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198310032009122001": {"nama": "Ineke Setiyaningsih, S.Sos", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198408282010122003": {"nama": "Farah Agustina Setiawati, SH", "pass": "kpuhss2026", "role": "ADMIN"},
        "198406212011012013": {"nama": "Rusma Ariati, SE", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198501082010122006": {"nama": "Suci Lestari, S.Ikom", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "200107122025062017": {"nama": "Athaya Insyira Khairani, S.H", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "200106082025061007": {"nama": "Muhammad Ibnu Fahmi, S.H.", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "196803181990032003": {"nama": "Helmalina", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198308292008111001": {"nama": "Ahmad Erwan Rifani, S.HI", "pass": "kpuhss2026", "role": "BENDAHARA"},
        "198506082007012003": {"nama": "Najmi Hidayati", "pass": "kpuhss2026", "role": "BENDAHARA"},
        "200101212025061007": {"nama": "Muhammad Aldi Hudaifi, S.Kom", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "200204152025062007": {"nama": "Firda Aulia, S.Kom.", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198207122009101001": {"nama": "Jainal Abidin", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "197411272007101001": {"nama": "Syaiful Anwar", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198210252007011003": {"nama": "Zainal Hilmi Yustan", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199509032025061005": {"nama": "Alfian Ridhani, S.Kom", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199506172025211036": {"nama": "Saiful Fahmi, S.Pd", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198411222024211010": {"nama": "Sulaiman", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199202072024212044": {"nama": "Sya'bani Rona Baika", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "197705022024211007": {"nama": "Basuki Rahmat", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198008112025211019": {"nama": "Saldoz Yedi", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199106012025211018": {"nama": "Mastoni Ridani", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199803022025211005": {"nama": "Suriadi", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198204042025211031": {"nama": "Ami Aspihani", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198906222025212027": {"nama": "Emaliani", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199906062025212036": {"nama": "Nadianti", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198905262024211016": {"nama": "M Satria Maipadly", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198810122025211031": {"nama": "Abdurrahman", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "198904222024211013": {"nama": "Apriadi Rakhman", "pass": "kpuhss2026", "role": "PEGAWAI"},
        "199603212025211031": {"nama": "Muhammad Hafiz Rijani, S.KOM", "pass": "kpuhss2026", "role": "PEGAWAI"}
    }

# --- 3. DATABASE INFO 31 ORG ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis...", "PNS"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan...", "PNS"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum...", "PNS"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan...", "PNS"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PPPK"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PPPK"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PPPK"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PPPK"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PPPK"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PPPK"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
KPU_COORD = (-2.784824, 115.231263)

# --- 4. HELPERS ---
def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={time.time()}", timeout=10)
        df = pd.read_csv(StringIO(r.text))
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df.dropna(subset=['Timestamp'])
    except: return pd.DataFrame()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2, dphi, dlamb = radians(lat1), radians(lat2), radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlamb/2)**2
    return 2 * R * asin(sqrt(a))

# --- 5. STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; color: white; }
    .employee-card { background: rgba(255, 255, 255, 0.07); padding: 12px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 6px; border: 1px solid rgba(255,255,255,0.1); }
    .emp-name { flex: 3; font-weight: bold; font-size: 14px; color: #f8fafc; }
    .emp-status { flex: 1; text-align: right; font-weight: 800; font-size: 13px; }
    .status-hadir { color: #10B981; } .status-alpa { color: #EF4444; } .status-terlambat { color: #F59E0B; }
    .user-card { background: rgba(255,255,255,0.1); padding: 25px; border-radius: 20px; text-align: center; border: 1px solid #F59E0B; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<h2 style='text-align:center; color:#F59E0B;'>🏛️ KPU HSS LOGIN</h2>", unsafe_allow_html=True)
        u_nip = st.text_input("NIP")
        u_pass = st.text_input("Password", type="password")
        if st.button("MASUK", use_container_width=True):
            if u_nip in st.session_state.user_db and st.session_state.user_db[u_nip]['pass'] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = st.session_state.user_db[u_nip]
                st.rerun()
            else: st.error("Akses Ditolak")
    st.stop()

# --- 7. MAIN APP ---
user = st.session_state.user
role = user['role'].upper()

st.sidebar.title(f"👤 {user['nama']}")
st.sidebar.write(f"Hak Akses: {role}")
if st.sidebar.button("LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()

def render_user_buttons():
    c1, c2 = st.columns(2)
    c1.button("🚀 ABSENSI", use_container_width=True)
    c2.button("📝 LAPKIN", use_container_width=True)
    c3, c4 = st.columns(2)
    c3.button("📅 REKAP SAYA", use_container_width=True)
    c4.button("📥 DOWNLOAD", use_container_width=True)

# --- VIEW ADMIN / BENDAHARA ---
if role in ["ADMIN", "BENDAHARA"]:
    st.subheader(f"🏛️ {role} DASHBOARD")
    
    with st.expander("🔑 MENU MANDIRI (Absen & Lapkin Anda)"):
        render_user_buttons()

    t1, t2, t3 = st.tabs(["📊 MONITORING", "📥 REKAP DATA", "🔑 KELOLA" if role == "ADMIN" else "🔒 INFO"])
    
    with t1:
        st.write("### Status Pegawai Hari Ini")
        pilih_tgl = st.date_input("Tanggal", value=datetime.now(wita_tz).date())
        
        # LOGIKA MONITORING REAL-TIME
        df_pns = get_clean_df(URL_PNS)
        df_pppk = get_clean_df(URL_PPPK)
        df_all = pd.concat([df_pns, df_pppk])
        
        # Filter Hari Ini
        df_today = df_all[df_all['Timestamp'].dt.date == pilih_tgl]
        
        for p_nama in DATABASE_INFO.keys():
            data_p = df_today[df_today['Nama Lengkap (Tanpa Gelar)'] == p_nama.split(',')[0].strip()]
            
            status_txt = "ALPA"
            status_class = "status-alpa"
            jam_txt = "--:--"
            
            if not data_p.empty:
                row = data_p.iloc[-1]
                jam_hadir = row['Timestamp'].time()
                jam_txt = jam_hadir.strftime("%H:%M")
                
                # Cek Lokasi
                try:
                    lat_p, lon_p = map(float, str(row['Lokasi Anda (Titik Koordinat)']).split(','))
                    dist = haversine(KPU_COORD[0], KPU_COORD[1], lat_p, lon_p)
                    if dist > 100: status_txt = "DILUAR RADIUS"
                    elif jam_hadir > datetime.strptime("08:00", "%H:%M").time(): 
                        status_txt = "TERLAMBAT"
                        status_class = "status-terlambat"
                    else:
                        status_txt = "HADIR"
                        status_class = "status-hadir"
                except: status_txt = "KOORDINAT ERROR"

            st.markdown(f"""
                <div class="employee-card">
                    <div class="emp-name">{p_nama}</div>
                    <div class="emp-status {status_class}">{status_txt} ({jam_txt})</div>
                </div>
            """, unsafe_allow_html=True)

    with t2:
        st.subheader("Rekapitulasi")
        st.button("📥 Unduh Semua Data (Excel)")

    if role == "ADMIN":
        with t3:
            st.write("### Daftar Password")
            df_users = pd.DataFrame([{"NIP":k, "Nama":v['nama'], "Pass":v['pass']} for k,v in st.session_state.user_db.items()])
            st.dataframe(df_users, use_container_width=True)

# --- VIEW PEGAWAI ---
else:
    st.markdown("<div class='user-card'>", unsafe_allow_html=True)
    st.subheader(f"Selamat Bekerja, {user['nama']}")
    render_user_buttons()
    st.markdown("</div>", unsafe_allow_html=True)
