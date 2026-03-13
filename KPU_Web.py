import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
import time

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v18.2",
    page_icon="🏢",
    layout="wide"
)

# --- 2. LUXURY CSS (MOBILE RESPONSIVE) ---
st.markdown("""
    <style>
    /* Background & Global */
    .main { background: linear-gradient(135deg, #4c0519 0%, #1e0000 100%); color: #f8fafc; }
    
    /* Header Container */
    .header-container { text-align: center; padding: 10px 0; }
    
    /* Responsive Title & Clock */
    .main-title { font-size: clamp(30px, 8vw, 65px) !important; font-weight: 900; color: white; margin: 0; line-height: 1; }
    .time-glow { font-size: clamp(35px, 10vw, 60px) !important; color: #fbbf24; text-shadow: 0 0 20px rgba(251, 191, 36, 0.6); font-weight: bold; font-family: 'JetBrains Mono', monospace; }

    /* Navigasi Buttons Responsive */
    div.stButton > button {
        width: 100% !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
    }

    /* BARIS PEGAWAI - AUTO CENTER & NARROW */
    .staff-row-card {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 8px 15px;
        margin: 0 auto 6px auto;
        max-width: 1000px;
        transition: 0.3s ease;
    }
    .staff-row-card:hover {
        background: rgba(251, 191, 36, 0.1) !important;
        border: 1px solid #fbbf24 !important;
    }
    
    /* Font Size untuk HP */
    .val-nama { font-size: clamp(16px, 4vw, 26px) !important; font-weight: 800; color: white; margin: 0; }
    .val-mini { font-size: clamp(14px, 3vw, 18px) !important; font-weight: 600; color: #fbbf24; margin: 0; }
    .label-micro { color: #94a3b8; font-size: 9px; text-transform: uppercase; margin: 0; }
    
    /* Status Colors */
    .status-hadir { color: #10B981; font-weight: bold; }
    .status-terlambat { color: #F59E0B; font-weight: bold; }
    .status-alpa { color: #EF4444; font-weight: bold; }

    /* Hilangkan Spasi Standar Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE ---
DATABASE_INFO = {
    "Suwanto": ["19720521 200912 1 001", "Sekretaris KPU"],
    "Wawan Setiawan": ["19860601 201012 1 004", "Kasubbag TP-Hupmas"],
    "Ineke Setiyaningsih": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik"],
    "Farah Agustina Setiawati": ["19840828 201012 2 003", "Kasubbag Hukum dan SDM"],
    "Rusma Ariati": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan"],
    "Ahmad Erwan Rifani": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional"],
    "Suci Lestari": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan"],
    "Athaya Insyira Khairani": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Muhammad Ibnu Fahmi": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Alfian Ridhani": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Muhammad Aldi Hudaifi": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Firda Aulia": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Basuki Rahmat": ["197705222024211007", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN"],
    "Muhammad Hafiz Rijani": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Saiful Fahmi": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN"]
}

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]
LIST_BULAN = ["SEPANJANG TAHUN", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# --- 4. LOGIC ---
@st.cache_data(ttl=15)
def fetch_cloud_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        t_col = df.columns[0]
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except: return pd.DataFrame()

def draw_rows(df, master_list, tab_obj, target_date, tab_name):
    log = {}
    lim_in, lim_out = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    if not df.empty:
        t_c, n_c = df.columns[0], df.columns[1]
        df_day = df[df[t_c].dt.date == target_date].copy()
        for p in master_list:
            match = df_day[df_day[n_c].str.contains(p, case=False, na=False, regex=False)]
            if not match.empty:
                for _, r in match.iterrows():
                    jam = r[t_c].time()
                    if p not in log: log[p] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < lim_in else "TERLAMBAT"}
                    if jam >= lim_out: log[p]["p"] = jam.strftime("%H:%M")
    with tab_obj:
        for p in master_list:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            clr = "status-hadir" if "HADIR" in d['k'] else "status-terlambat" if "TERLAMBAT" in d['k'] else "status-alpa"
            st.markdown(f'<div class="staff-row-card">', unsafe_allow_html=True)
            c_nm, c_pg, c_sr, c_kt, c_bt = st.columns([4, 1.2, 1.2, 2.5, 1.2])
            c_nm.markdown(f"<p class='label-micro'>👤 PEGAWAI</p><p class='val-nama'>{p}</p>", unsafe_allow_html=True)
            c_pg.markdown(f"<p class='label-micro'>PAGI</p><p class='val-mini'>{d['m']}</p>", unsafe_allow_html=True)
            c_sr.markdown(f"<p class='label-micro'>SORE</p><p class='val-mini'>{d['p']}</p>", unsafe_allow_html=True)
            c_kt.markdown(f"<p class='label-micro' style='text-align:right'>STATUS</p><p class='{clr}' style='text-align:right; font-size:15px;'>{d['k']}</p>", unsafe_allow_html=True)
            if c_bt.button("Update ✅", key=f"upd_{tab_name}_{p}"):
                info = DATABASE_INFO.get(p)
                fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data={"entry.960346359":p,"entry.468881973":info[0],"entry.159009649":info[1],"submit":"Submit"})
                st.cache_data.clear(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN UI ---
# JAM REAL-TIME FIX (Tanpa rerun yang merusak layout)
st.markdown("""
    <div class="header-container">
        <p class="main-title">MONITORING ABSENSI KPU HSS</p>
        <p id="clock-display" class="time-glow">00:00:00 WITA</p>
    </div>
    <script>
        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const clock = document.getElementById('clock-display');
            if(clock) clock.innerText = hours + ':' + minutes + ':' + seconds + ' WITA';
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """, unsafe_allow_html=True)

# NAVIGASI SEJAJAR FULL WIDTH
col_lih, col_ref, col_rek = st.columns([1,1,1])
with col_lih:
    with st.expander(f"📅 Tgl: {st.session_state.get('d_tgl', datetime.now().date())}"):
        st.session_state.d_tgl = st.date_input("Pilih", datetime.now().date(), key="input_tgl")
with col_ref:
    if st.button("🔄 REFRESH DATA"): st.cache_data.clear(); st.rerun()
with col_rek:
    if st.button("📥 EXCEL REKAP"): st.session_state.show_rekap = not st.session_state.get('show_rekap', False)

# Advanced Rekap Panel
if st.session_state.get('show_rekap', False):
    st.markdown("<div style='background-color:rgba(0,0,0,0.6); padding:20px; border-radius:15px; border:1px solid #fbbf24; margin-bottom:10px;'>", unsafe_allow_html=True)
    r1, r2 = st.columns(2); bln = r1.selectbox("Bulan", LIST_BULAN, index=datetime.now().month); thn = r2.selectbox("Tahun", range(2024, 2031), index=2)
    r3, r4 = st.columns(2); kat_r = r3.selectbox("Kategori", ["SEMUA PEGAWAI", "PNS", "PPPK"])
    nm_opts = ["-- Semua --"]; nm_opts += MASTER_PNS if kat_r == "PNS" else MASTER_PPPK if kat_r == "PPPK" else []
    nm_r = r4.selectbox("Nama Spesifik", nm_opts)
    if st.button("🚀 GENERATE EXCEL"):
        df_all = pd.concat([fetch_cloud_data(URL_PNS), fetch_cloud_data(URL_PPPK)])
        t_c, n_c = df_all.columns[0], df_all.columns[1]
        df_f = df_all[df_all[t_c].dt.year == thn].copy()
        if bln != "SEPANJANG TAHUN": df_f = df_f[df_f[t_c].dt.month == LIST_BULAN.index(bln)]
        if kat_r == "PNS": df_f = df_f[df_f[n_c].isin(MASTER_PNS)]
        elif kat_r == "PPPK": df_f = df_f[df_f[n_c].isin(MASTER_PPPK)]
        if "-- Semua" not in nm_r: df_f = df_f[df_f[n_c].str.contains(nm_r, case=False, na=False)]
        if not df_f.empty:
            df_f[t_c] = df_f[t_c].dt.strftime('%d/%m/%Y %H:%M')
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as wr: df_f.to_excel(wr, index=False)
            st.download_button("💾 KLIK DOWNLOAD", out.getvalue(), f"REKAP_{bln}.xlsx", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. DASHBOARD ---
df_all_raw = pd.concat([fetch_cloud_data(URL_PNS), fetch_cloud_data(URL_PPPK)])
tab1, tab2, tab3 = st.tabs([f"🌍 SEMUA (31)", f"👥 PNS (17)", f"👥 PPPK (14)"])
tgl_target = st.session_state.get('d_tgl', datetime.now().date())

draw_rows(df_all_raw, list(DATABASE_INFO.keys()), tab1, tgl_target, "all")
draw_rows(fetch_cloud_data(URL_PNS), MASTER_PNS, tab2, tgl_target, "pns")
draw_rows(fetch_cloud_data(URL_PPPK), MASTER_PPPK, tab3, tgl_target, "pppk")
