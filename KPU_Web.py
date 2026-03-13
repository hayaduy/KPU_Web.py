import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v16.2",
    page_icon="🏢",
    layout="wide"
)

# Custom CSS untuk membuat tombol persis seperti gambar
st.markdown("""
    <style>
    .main { background-color: #050505; color: #E2E8F0; }
    
    /* Center Header */
    .header-text {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: white;
        margin-bottom: 0px;
    }
    .wita-text {
        text-align: center;
        font-size: 24px;
        color: #F59E0B;
        margin-bottom: 30px;
    }

    /* Styling Tombol Navigasi Utama */
    div.stButton > button {
        width: 100%;
        height: 55px;
        border-radius: 30px;
        font-weight: bold;
        font-size: 16px;
        border: none;
        transition: 0.3s;
    }
    
    /* Tombol Lihat Tgl (Abu-abu) */
    div[data-testid="column"]:nth-child(1) button {
        background-color: #334155 !important;
        color: white !important;
    }
    
    /* Tombol Refresh (Orange) */
    div[data-testid="column"]:nth-child(2) button {
        background-color: #D97706 !important;
        color: white !important;
    }
    
    /* Tombol Excel Rekap (Biru) */
    div[data-testid="column"]:nth-child(3) button {
        background-color: #1D4ED8 !important;
        color: white !important;
    }

    /* Tabs & Rows */
    .stTabs [aria-selected="true"] { background-color: #EF4444 !important; color: white !important; }
    .staff-row { border-bottom: 1px solid rgba(255,255,255,0.05); padding: 10px 0; }
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

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

@st.cache_data(ttl=20)
def fetch_cloud_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        t_col = df.columns[0]
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except: return pd.DataFrame()

# --- 3. HEADER UI ---
st.markdown('<p class="header-text">MONITORING ABSENSI KPU HSS</p>', unsafe_allow_html=True)
st.markdown(f'<p class="wita-text">{datetime.now().strftime("%H:%M:%S")} WITA</p>', unsafe_allow_html=True)

# --- 4. NAVIGATION BUTTONS (TRIPLE COLUMN) ---
col_lih, col_ref, col_rek = st.columns(3)

with col_lih:
    # Pakai expander kecil untuk pilih tanggal agar hemat ruang
    with st.expander(f"📅 Lihat Tgl: {st.session_state.get('d_tgl', datetime.now().date())}"):
        st.session_state.d_tgl = st.date_input("Pilih", datetime.now().date(), key="input_tgl")

with col_ref:
    if st.button("🔄 REFRESH"):
        st.rerun()

with col_rek:
    # Tombol Excel Rekap membuka expander pilihan rekap
    btn_rekap = st.button("📥 EXCEL REKAP")

if btn_rekap or 'rekap_open' in st.session_state:
    st.session_state.rekap_open = True
    with st.container():
        st.markdown("---")
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        bln = c1.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
        thn = c2.selectbox("Tahun", range(2024, 2031), index=2)
        kat = c3.selectbox("Kategori", ["SEMUA", "PNS", "PPPK"])
        if c4.button("🚀 GENERATE"):
            df_p = fetch_cloud_data(URL_PNS)
            df_pp = fetch_cloud_data(URL_PPPK)
            df_all = pd.concat([df_p, df_pp])
            t_col, n_col = df_all.columns[0], df_all.columns[1]
            df_f = df_all[df_all[t_col].dt.year == thn].copy()
            if bln != "SEPANJANG TAHUN": df_f = df_f[df_f[t_col].dt.month == LIST_BULAN.index(bln)]
            if kat == "PNS": df_f = df_f[df_f[n_col].isin(MASTER_PNS)]
            elif kat == "PPPK": df_f = df_f[df_f[n_col].isin(MASTER_PPPK)]
            
            if not df_f.empty:
                df_f[t_col] = df_f[t_col].dt.strftime('%d/%m/%Y %H:%M')
                out = BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as wr: df_f.to_excel(wr, index=False)
                st.download_button("💾 DOWNLOAD FILE", out.getvalue(), f"REKAP_{bln}.xlsx")
            else: st.error("Data Kosong")
        if st.button("Close ❌"): del st.session_state.rekap_open; st.rerun()
    st.markdown("---")

# --- 5. DASHBOARD ---
df_pns = fetch_cloud_data(URL_PNS)
df_pppk = fetch_cloud_data(URL_PPPK)
df_all_data = pd.concat([df_pns, df_pppk])

tab1, tab2, tab3 = st.tabs(["🌍 SEMUA", "👥 PNS", "👥 PPPK"])

def draw_rows(df, master, tab_obj):
    log = {}
    lim_in, lim_out = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    tgl_target = st.session_state.get('d_tgl', datetime.now().date())
    
    if not df.empty:
        t_c = df.columns[0]
        df_day = df[df[t_c].dt.date == tgl_target]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_c].time()
            if n not in log: log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < lim_in else "TERLAMBAT"}
            if jam >= lim_out: log[n]["p"] = jam.strftime("%H:%M")

    with tab_obj:
        for p in master:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            clr = "#10B981" if "HADIR" in d['k'] else "#F59E0B" if "TERLAMBAT" in d['k'] else "#EF4444"
            
            c_nm, c_pg, c_sr, c_kt, c_bt = st.columns([3, 1.5, 1.5, 2, 1])
            c_nm.markdown(f"<p style='color:#64748B; font-size:10px; margin:0'>👤 PEGAWAI</p><p style='font-size:16px;'>{p}</p>", unsafe_allow_html=True)
            c_pg.markdown(f"<p style='color:#64748B; font-size:10px; margin:0'>PAGI</p><p style='font-size:16px;'>{d['m']}</p>", unsafe_allow_html=True)
            c_sr.markdown(f"<p style='color:#64748B; font-size:10px; margin:0'>SORE</p><p style='font-size:16px;'>{d['p']}</p>", unsafe_allow_html=True)
            c_kt.markdown(f"<p style='color:#64748B; font-size:10px; margin:0; text-align:right'>KET</p><p style='color:{clr}; font-weight:bold; text-align:right'>{d['k']}</p>", unsafe_allow_html=True)
            if c_bt.button("Update ✅", key=f"upd_{p}"):
                info = DATABASE_INFO.get(p)
                fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data={"entry.960346359":p,"entry.468881973":info[0],"entry.159009649":info[1],"submit":"Submit"})
                st.rerun()
            st.markdown("<hr style='margin:5px 0; border-color:rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

draw_rows(df_all_data, list(DATABASE_INFO.keys()), tab1)
draw_rows(df_pns, MASTER_PNS, tab2)
draw_rows(df_pppk, MASTER_PPPK, tab3)
