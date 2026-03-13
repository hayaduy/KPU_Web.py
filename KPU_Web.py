import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
from streamlit_autorefresh import st_autorefresh
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="KPU HSS Presence Hub v18.17", page_icon="🏢", layout="wide")

# --- 2. MASTER DATA ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

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
MASTER_PNS, MASTER_PPPK = list(DATABASE_INFO.keys())[:17], list(DATABASE_INFO.keys())[17:]
LIST_BULAN = ["SEPANJANG TAHUN", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 3. THEME CSS (SOLID BOX & CENTER) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #800000 0%, #1a0208 50%, #000000 85%, #ff8c00 100%) !important;
        background-attachment: fixed !important;
    }
    
    .header-container { text-align: center; width: 100%; padding-top: 10px; }
    .main-title { font-size: clamp(30px, 7vw, 60px) !important; font-weight: 900; color: white !important; margin: 0; }
    .time-glow { font-size: clamp(35px, 9vw, 60px) !important; color: #fbbf24 !important; text-shadow: 0 0 30px rgba(251, 191, 36, 0.9) !important; font-weight: bold; margin-bottom: 20px; font-family: 'JetBrains Mono', monospace; }

    /* Nav & Tabs Center */
    [data-testid="stHorizontalBlock"] { justify-content: center !important; display: flex !important; }
    .stTabs [data-baseweb="tab-list"] { display: flex !important; justify-content: center !important; width: 100% !important; gap: 10px !important; }
    .stTabs [aria-selected="true"] { background-color: #8B0000 !important; border: 1px solid #fbbf24 !important; color: white !important; }

    /* BARIS PANJANG BERBUNGKUS HITAM TIPIS */
    .staff-row-card {
        background: rgba(0, 0, 0, 0.5) !important; /* Box Hitam sepanjang baris */
        border: 1px solid rgba(251, 191, 36, 0.2) !important;
        border-left: 6px solid #fbbf24 !important; /* Aksen oranye tetap ada */
        border-radius: 12px; 
        padding: 12px 18px; 
        margin: 0 auto 10px auto; 
        max-width: 1080px;
        transition: 0.3s ease; 
        display: flex; 
        align-items: center;
    }
    .staff-row-card:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #fbbf24 !important;
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
    }

    .val-nama { font-size: clamp(18px, 4vw, 24px) !important; font-weight: 900; color: white; margin: 0; }
    .label-micro { color: #94a3b8; font-size: 10px; text-transform: uppercase; margin: 0; font-weight: bold; }
    .val-mini { color: #fbbf24; font-weight: bold; font-size: 18px; margin: 0; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
@st.cache_data(ttl=5)
def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        t_c = df.columns[0]
        df[t_c] = pd.to_datetime(df[t_c], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_c]).sort_values(by=t_c)
    except: return pd.DataFrame()

@st.fragment(run_every="1s")
def clock_fragment():
    tz = pytz.timezone('Asia/Makassar')
    now = datetime.now(tz)
    st.markdown(f'<div style="text-align:center;"><p class="time-glow">{now.strftime("%H:%M:%S")} WITA</p></div>', unsafe_allow_html=True)

def draw_rows(df, master, tab_obj, target_date, tab_name):
    log = {}
    l_in, l_out = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    if not df.empty:
        t_c, n_c = df.columns[0], df.columns[1]
        df_day = df[df[t_c].dt.date == target_date].copy()
        for p in master:
            match = df_day[df_day[n_c].str.contains(p, case=False, na=False)]
            if not match.empty:
                for _, r in match.iterrows():
                    jam = r[t_c].time()
                    if p not in log: log[p] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < l_in else "TERLAMBAT"}
                    if jam >= l_out: log[p]["p"] = jam.strftime("%H:%M")
    with tab_obj:
        for p in master:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            clr = "#10B981" if "HADIR" in d['k'] else "#F59E0B" if "TERLAMBAT" in d['k'] else "#EF4444"
            
            st.markdown(f'<div class="staff-row-card">', unsafe_allow_html=True)
            cn, cp, cs, ck, cb = st.columns([3.5, 1.2, 1.2, 2.5, 1.2])
            with cn:
                st.markdown(f'<div><p class="label-micro">PEGAWAI</p><p class="val-nama">{p}</p></div>', unsafe_allow_html=True)
            cp.markdown(f"<p class='label-micro'>PAGI</p><p class='val-mini'>{d['m']}</p>", unsafe_allow_html=True)
            cs.markdown(f"<p class='label-micro'>SORE</p><p class='val-mini'>{d['p']}</p>", unsafe_allow_html=True)
            ck.markdown(f"<p class='label-micro' style='text-align:right'>STATUS</p><p style='color:{clr}; text-align:right; font-weight:bold; font-size:16px;'>{d['k']}</p>", unsafe_allow_html=True)
            if cb.button("Update ✅", key=f"u_{tab_name}_{p}"):
                info = DATABASE_INFO.get(p)
                fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data={"entry.960346359":p,"entry.468881973":info[0],"entry.159009649":info[1],"submit":"Submit"})
                st.cache_data.clear(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 5. EXECUTION ---
st_autorefresh(interval=2 * 60 * 1000, key="datarefresh")
st.markdown('<div class="header-container"><p class="main-title">MONITORING ABSENSI KPU HSS</p></div>', unsafe_allow_html=True)
clock_fragment()

c1, c2, c3 = st.columns([1.5, 1, 1.5])
with c1:
    with st.expander(f"📅 Tgl: {st.session_state.get('d_tgl', datetime.now().date())}"):
        st.session_state.d_tgl = st.date_input("Pilih", datetime.now().date(), key="input_tgl")
with c2:
    if st.button("🔄 REFRESH"): st.cache_data.clear(); st.rerun()
with c3:
    if st.button("📥 EXCEL REKAP"): st.session_state.show_rekap = not st.session_state.get('show_rekap', False)

# PANEL REKAP DENGAN FILTER NAMA (RESTORATION)
if st.session_state.get('show_rekap', False):
    st.markdown("<div style='background-color:rgba(0,0,0,0.8); padding:20px; border-radius:15px; border:1px solid #fbbf24; margin-bottom:15px;'>", unsafe_allow_html=True)
    st.write("### ADVANCED REKAP EXCEL")
    r1, r2 = st.columns(2)
    bln_r = r1.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
    thn_r = r2.selectbox("Tahun", range(2024, 2031), index=2)
    
    r3, r4 = st.columns(2)
    kat_r = r3.selectbox("Kategori", ["SEMUA PEGAWAI", "PNS", "PPPK"])
    nm_opts = ["-- Semua --"]
    if kat_r == "PNS": nm_opts += MASTER_PNS
    elif kat_r == "PPPK": nm_opts += MASTER_PPPK
    nm_r = r4.selectbox("Pilih Nama Spesifik (Opsional)", nm_opts)
    
    if st.button("🚀 GENERATE EXCEL"):
        df_all_f = pd.concat([fetch_data(URL_PNS), fetch_data(URL_PPPK)])
        t_c, n_c = df_all_f.columns[0], df_all_f.columns[1]
        df_f = df_all_f[df_all_f[t_c].dt.year == thn_r].copy()
        if bln_r != "SEPANJANG TAHUN": df_f = df_f[df_f[t_c].dt.month == LIST_BULAN.index(bln_r)]
        if kat_r == "PNS": df_f = df_f[df_f[n_c].isin(MASTER_PNS)]
        elif kat_r == "PPPK": df_f = df_f[df_f[n_c].isin(MASTER_PPPK)]
        if "-- Semua" not in nm_r: df_f = df_f[df_f[n_c].str.contains(nm_r, case=False, na=False)]
        
        if not df_f.empty:
            df_f[t_c] = df_f[t_c].dt.strftime('%d/%m/%Y %H:%M')
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as wr: df_f.to_excel(wr, index=False)
            st.download_button("💾 DOWNLOAD", out.getvalue(), f"REKAP_{bln_r}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

df_all = pd.concat([fetch_data(URL_PNS), fetch_data(URL_PPPK)])
t1, t2, t3 = st.tabs([f"🌍 SEMUA (31)", f"👥 PNS (17)", f"👥 PPPK (14)"])
tgl = st.session_state.get('d_tgl', datetime.now().date())
draw_rows(df_all, list(DATABASE_INFO.keys()), t1, tgl, "all")
draw_rows(fetch_data(URL_PNS), MASTER_PNS, t2, tgl, "pns")
draw_rows(fetch_data(URL_PPPK), MASTER_PPPK, t3, tgl, "pppk")
