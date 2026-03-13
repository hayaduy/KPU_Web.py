import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION & CYBER THEME ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v15.0",
    page_icon="⚡",
    layout="wide"
)

# Mantra CSS untuk tampilan Ultra-Modern
st.markdown("""
    <style>
    /* Background Animasi Gradient */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Styling Header Center */
    .main-header {
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Card Pegawai ala Cyberpunk */
    div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        margin-bottom: 12px !important;
    }
    
    div[data-testid="stExpander"]:hover {
        border: 1px solid #f59e0b !important;
        background: rgba(30, 41, 59, 0.6) !important;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.2) !important;
    }

    /* Metric Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #f59e0b !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.6);
        transform: scale(1.02);
    }

    /* Status Text Glow */
    .status-hadir { color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.4); font-weight: bold; }
    .status-terlambat { color: #f59e0b; text-shadow: 0 0 10px rgba(245, 158, 11, 0.4); font-weight: bold; }
    .status-alpa { color: #ef4444; text-shadow: 0 0 10px rgba(239, 68, 68, 0.4); font-weight: bold; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE PEGAWAI (31 ORANG) ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris KPU"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum dan SDM"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
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
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN"]
}

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]
LIST_BULAN = ["SEPANJANG TAHUN", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# --- 3. LOGIKA AMBIL DATA ---
@st.cache_data(ttl=60)
def fetch_cloud_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        t_col = df.columns[0]
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except:
        return pd.DataFrame()

# --- 4. HEADER ---
st.markdown('<div class="main-header"><h1>MONITORING ABSENSI KPU HSS</h1></div>', unsafe_allow_html=True)

# Grid Layout Atas (Jam & Filter Tanggal Dashboard)
col_clock, col_date = st.columns([2, 1])
with col_clock:
    st.markdown(f"### 🕒 {datetime.now().strftime('%H:%M:%S')} WITA")
with col_date:
    tgl_dash = st.date_input("📌 Lihat Tanggal:", datetime.now().date())

# --- 5. SIDEBAR EXCEL REKAP ---
st.sidebar.title("💎 MENU REKAP")
with st.sidebar.container():
    bln_r = st.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
    thn_r = st.selectbox("Tahun", range(2024, 2031), index=2)
    kat_r = st.radio("Kategori", ["SEMUA", "PNS", "PPPK"])
    
    if st.button("✨ GENERATE LAPORAN"):
        df_p = fetch_cloud_data(URL_PNS)
        df_pp = fetch_cloud_data(URL_PPPK)
        df_all = pd.concat([df_p, df_pp])
        t_c = df_all.columns[0]
        
        df_f = df_all[df_all[t_c].dt.year == thn_r].copy()
        if bln_r != "SEPANJANG TAHUN":
            df_f = df_f[df_f[t_c].dt.month == LIST_BULAN.index(bln_r)]
            
        if not df_f.empty:
            df_f[t_c] = df_f[t_c].dt.strftime('%d/%m/%Y %H:%M')
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as wr:
                df_f.to_excel(wr, index=False)
            st.sidebar.download_button("📥 DOWNLOAD EXCEL", out.getvalue(), f"REKAP_KPU_{bln_r}.xlsx")
        else:
            st.sidebar.error("Data tidak ditemukan!")

# --- 6. DASHBOARD AREA ---
st.divider()
tab1, tab2 = st.tabs(["👤 STATUS PNS", "👤 STATUS PPPK"])

def render_staff(df, master, tab):
    log = {}
    limit_in = datetime.strptime("09:00", "%H:%M").time()
    limit_out = datetime.strptime("15:30", "%H:%M").time()
    
    if not df.empty:
        t_c = df.columns[0]
        df_day = df[df[t_c].dt.date == tgl_dash]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_col].time() if 't_col' in locals() else r.iloc[0].time()
            if n not in log:
                log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < limit_in else "TERLAMBAT"}
            if jam >= limit_out:
                log[n]["p"] = jam.strftime("%H:%M")

    with tab:
        for p in master:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
            c_tag = "status-hadir" if "HADIR" in d['k'] else "status-terlambat" if "TERLAMBAT" in d['k'] else "status-alpa"
            
            with st.expander(f"**{p}**"):
                c1, c2, c3 = st.columns([1,1,1])
                c1.metric("MASUK", d['m'])
                c2.metric("PULANG", d['p'])
                c3.markdown(f"STATUS:<br><span class='{c_tag}'>{d['k']}</span>", unsafe_allow_html=True)
                
                if st.button(f"SINKRONISASI DATA: {p[:12]}...", key=p):
                    info = DATABASE_INFO.get(p)
                    fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                    requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", 
                                  data={"entry.960346359": p, "entry.468881973": info[0], "entry.159009649": info[1], "submit": "Submit"})
                    st.success("Berhasil!")
                    st.rerun()

render_staff(fetch_cloud_data(URL_PNS), MASTER_PNS, tab1)
render_staff(fetch_cloud_data(URL_PPPK), MASTER_PPPK, tab2)
