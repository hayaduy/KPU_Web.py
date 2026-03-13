import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v16.1",
    page_icon="🏢",
    layout="wide"
)

# Mantra CSS (Hitam, Merah, Elegant + Sidebar Fix)
st.markdown("""
    <style>
    .main { background-color: #050505; color: #E2E8F0; }
    
    /* Center Clock */
    .time-header { text-align: center; padding: 20px 0; }
    .time-val { font-size: 60px; font-weight: bold; color: white; margin-bottom: 0px; }
    .date-val { font-size: 20px; color: #F59E0B; text-transform: uppercase; letter-spacing: 2px; }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px 5px 0 0;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] { background-color: #EF4444 !important; color: white !important; }

    /* Row Design */
    .val-main { font-size: 18px; font-weight: 500; }
    .label-small { font-size: 10px; color: #64748B; text-transform: uppercase; }
    
    /* Status Colors */
    .status-hadir { color: #10B981; font-weight: bold; }
    .status-terlambat { color: #F59E0B; font-weight: bold; }
    .status-alpa { color: #EF4444; font-weight: bold; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #0A0A0A; border-right: 1px solid #1A1A1A; }
    .stDownloadButton>button {
        background-color: #10B981 !important;
        color: white !important;
        width: 100%;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
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

# --- 3. LOGIKA FETCH ---
@st.cache_data(ttl=30)
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

df_pns = fetch_cloud_data(URL_PNS)
df_pppk = fetch_cloud_data(URL_PPPK)
df_all_data = pd.concat([df_pns, df_pppk])

# --- 4. SIDEBAR (INI YANG TADI HILANG) ---
with st.sidebar:
    st.markdown("<h2 style='color:#F59E0B;'>📥 MENU REKAP</h2>", unsafe_allow_html=True)
    st.divider()
    rekap_bln = st.selectbox("Pilih Bulan Rekap", LIST_BULAN, index=datetime.now().month)
    rekap_thn = st.selectbox("Pilih Tahun Rekap", range(2024, 2031), index=2)
    rekap_kat = st.radio("Kategori Download", ["SEMUA", "PNS", "PPPK"])
    
    if st.button("🚀 PROSES DATA EXCEL"):
        t_col = df_all_data.columns[0]
        n_col = df_all_data.columns[1]
        df_f = df_all_data[df_all_data[t_col].dt.year == rekap_thn].copy()
        if rekap_bln != "SEPANJANG TAHUN":
            df_f = df_f[df_f[t_col].dt.month == LIST_BULAN.index(rekap_bln)]
        
        if rekap_kat == "PNS": df_f = df_f[df_f[n_col].isin(MASTER_PNS)]
        elif rekap_kat == "PPPK": df_f = df_f[df_f[n_col].isin(MASTER_PPPK)]

        if not df_f.empty:
            df_f[t_col] = df_f[t_col].dt.strftime('%d/%m/%Y %H:%M')
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as wr:
                df_f.to_excel(wr, index=False)
            st.download_button("💾 DOWNLOAD SEKARANG", out.getvalue(), f"REKAP_KPU_{rekap_bln}.xlsx")
        else:
            st.error("Data tidak ditemukan!")

# --- 5. DASHBOARD ---
st.markdown(f"""
    <div class="time-header">
        <p class="time-val">{datetime.now().strftime('%H:%M:%S')}</p>
        <p class="date-val">{datetime.now().strftime('%A, %d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

tgl_dash = st.date_input("", datetime.now().date(), label_visibility="collapsed")

tab_all, tab_pns, tab_pppk = st.tabs([f"🌍 SEMUA (31)", f"👥 PNS (17)", f"👥 PPPK (14)"])

def render_rows(df, master, tab):
    log = {}
    limit_in, limit_out = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    if not df.empty:
        t_col = df.columns[0]
        df_day = df[df[t_col].dt.date == tgl_dash]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_col].time()
            if n not in log:
                log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < limit_in else "TERLAMBAT"}
            if jam >= limit_out: log[n]["p"] = jam.strftime("%H:%M")

    with tab:
        for p in master:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            st_cl = "status-hadir" if "HADIR" in d['k'] else "status-terlambat" if "TERLAMBAT" in d['k'] else "status-alpa"
            
            c_nm, c_pg, c_sr, c_kt, c_bt = st.columns([3, 1.5, 1.5, 2, 1])
            c_nm.markdown(f"<p class='label-small'>👤 PEGAWAI</p><p class='val-main'>{p}</p>", unsafe_allow_html=True)
            c_pg.markdown(f"<p class='label-small'>PAGI</p><p class='val-main'>{d['m']}</p>", unsafe_allow_html=True)
            c_sr.markdown(f"<p class='label-small'>SORE</p><p class='val-main'>{d['p']}</p>", unsafe_allow_html=True)
            c_kt.markdown(f"<p class='label-small' style='text-align:right'>KET</p><p class='{st_cl}' style='text-align:right; font-size:16px;'>{d['k']}</p>", unsafe_allow_html=True)
            if c_bt.button("Update ✅", key=p):
                info = DATABASE_INFO.get(p)
                fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data={"entry.960346359":p,"entry.468881973":info[0],"entry.159009649":info[1],"submit":"Submit"})
                st.rerun()
            st.markdown("<hr style='margin:5px 0; border-color:rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

render_rows(df_all_data, list(DATABASE_INFO.keys()), tab_all)
render_rows(df_pns, MASTER_PNS, tab_pns)
render_rows(df_pppk, MASTER_PPPK, tab_pppk)
