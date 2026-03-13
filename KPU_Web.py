import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION & DARK THEME ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v16.0",
    page_icon="🏢",
    layout="wide"
)

# Mantra CSS untuk tampilan MIRIP GAMBAR (Hitam, Merah, Elegant)
st.markdown("""
    <style>
    /* Reset & Background */
    .main {
        background-color: #050505;
        color: #E2E8F0;
    }
    
    /* Center Clock & Date */
    .time-header {
        text-align: center;
        padding: 40px 0;
    }
    .time-val {
        font-size: 80px;
        font-weight: bold;
        color: white;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
        margin-bottom: 0px;
    }
    .date-val {
        font-size: 24px;
        color: #F59E0B;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px 5px 0 0;
        color: #94A3B8;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EF4444 !important; /* Merah sesuai gambar */
        color: white !important;
    }

    /* ROW CARD PEGAWAI (Mirip Gambar) */
    .staff-row {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        transition: 0.3s;
    }
    .staff-row:hover {
        background-color: rgba(255, 255, 255, 0.07);
        border-color: rgba(239, 68, 68, 0.3);
    }

    /* Labels */
    .label-small {
        font-size: 10px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .val-main {
        font-size: 20px;
        font-weight: 500;
    }
    .status-text {
        font-size: 16px;
        font-weight: bold;
        text-align: right;
    }

    /* Button Hidden in Card */
    .stButton>button {
        background-color: #1E293B;
        color: white;
        border-radius: 8px;
        border: none;
        height: 35px;
        font-size: 12px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0A0A0A;
        border-right: 1px solid #1A1A1A;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE PEGAWAI (31 ORANG) ---
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

# --- 3. LOGIKA AMBIL DATA ---
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

# --- 4. HEADER (WAKTU & TANGGAL) ---
st.markdown(f"""
    <div class="time-header">
        <p class="time-val">{datetime.now().strftime('%H:%M:%S')}</p>
        <p class="date-val">{datetime.now().strftime('%A, %d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# Filter Tanggal Dashboard
tgl_dash = st.date_input("", datetime.now().date(), label_visibility="collapsed")

# --- 5. TABS ---
tab_all, tab_pns, tab_pppk = st.tabs([f"🌍 SEMUA ({len(DATABASE_INFO)})", f"👥 PNS ({len(MASTER_PNS)})", f"👥 PPPK ({len(MASTER_PPPK)})"])

def render_staff_rows(df, master_list, tab_obj):
    log = {}
    limit_in = datetime.strptime("09:00", "%H:%M").time()
    limit_out = datetime.strptime("15:30", "%H:%M").time()
    
    if not df.empty:
        t_col = df.columns[0]
        df_day = df[df[t_col].dt.date == tgl_dash]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_col].time()
            # Logika Pagi/Sore (Tetap sesuai tujuan aplikasi)
            if n not in log:
                log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < limit_in else "TERLAMBAT"}
            if jam >= limit_out:
                log[n]["p"] = jam.strftime("%H:%M")

    with tab_obj:
        for p in master_list:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            status_color = "#10B981" if "HADIR" in d['k'] else "#F59E0B" if "TERLAMBAT" in d['k'] else "#EF4444"
            
            # Memulai Baris Pegawai
            with st.container():
                col_nama, col_pagi, col_sore, col_ket, col_btn = st.columns([3, 1.5, 1.5, 2, 1])
                
                with col_nama:
                    st.markdown(f"<p style='margin-bottom:0; color:#94A3B8; font-size:12px;'>👤 PEGAWAI</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='val-main'>{p}</p>", unsafe_allow_html=True)
                
                with col_pagi:
                    st.markdown(f"<p class='label-small'>PAGI</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='val-main'>{d['m']}</p>", unsafe_allow_html=True)
                
                with col_sore:
                    st.markdown(f"<p class='label-small'>SORE</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='val-main'>{d['p']}</p>", unsafe_allow_html=True)
                
                with col_ket:
                    st.markdown(f"<p class='label-small' style='text-align:right'>KET</p>", unsafe_allow_html=True)
                    st.markdown(f"<p class='status-text' style='color:{status_color}'>{d['k']}</p>", unsafe_allow_html=True)
                
                with col_btn:
                    if st.button("Update ✅", key=p):
                        info = DATABASE_INFO.get(p)
                        fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                        requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", 
                                      data={"entry.960346359": p, "entry.468881973": info[0], "entry.159009649": info[1], "submit": "Submit"})
                        st.rerun()
                st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

# Jalankan Dashboard
df_pns = fetch_cloud_data(URL_PNS)
df_pppk = fetch_cloud_data(URL_PPPK)
df_all_data = pd.concat([df_pns, df_pppk])

render_staff_rows(df_all_data, list(DATABASE_INFO.keys()), tab_all)
render_staff_rows(df_pns, MASTER_PNS, tab_pns)
render_staff_rows(df_pppk, MASTER_PPPK, tab_pppk)

# --- 6. SIDEBAR REKAP ---
with st.sidebar:
    st.title("📥 EXCEL REKAP")
    bln = st.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
    thn = st.selectbox("Tahun", range(2024, 2031), index=2)
    kat = st.radio("Download Kategori", ["SEMUA", "PNS", "PPPK"])
    
    if st.button("🚀 GENERATE FILE"):
        t_col = df_all_data.columns[0]
        n_col = df_all_data.columns[1]
        df_f = df_all_data[df_all_data[t_col].dt.year == thn].copy()
        if bln != "SEPANJANG TAHUN":
            df_f = df_f[df_f[t_col].dt.month == LIST_BULAN.index(bln)]
        
        if kat == "PNS": df_f = df_f[df_f[n_col].isin(MASTER_PNS)]
        elif kat == "PPPK": df_f = df_f[df_f[n_col].isin(MASTER_PPPK)]

        if not df_f.empty:
            df_f[t_col] = df_f[t_col].dt.strftime('%d/%m/%Y %H:%M')
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as wr:
                df_f.to_excel(wr, index=False)
            st.download_button("💾 KLIK UNTUK SIMPAN", out.getvalue(), f"REKAP_{bln}_{thn}.xlsx")
        else:
            st.error("Data tidak ditemukan!")
