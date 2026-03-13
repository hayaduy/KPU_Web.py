import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v16.5",
    page_icon="🏢",
    layout="wide"
)

# --- 2. DATABASE UTAMA ---
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

# --- 3. CUSTOM UI CSS ---
st.markdown("""
    <style>
    .main { background-color: #050505; color: #E2E8F0; }
    .header-text { text-align: center; font-size: 38px; font-weight: bold; color: white; margin-bottom: 0px; }
    .wita-text { text-align: center; font-size: 22px; color: #F59E0B; margin-bottom: 30px; }
    div.stButton > button { width: 100%; height: 50px; border-radius: 25px; font-weight: bold; border: none; }
    div[data-testid="column"]:nth-child(1) button { background-color: #334155 !important; }
    div[data-testid="column"]:nth-child(2) button { background-color: #D97706 !important; }
    div[data-testid="column"]:nth-child(3) button { background-color: #1D4ED8 !important; }
    .rekap-container { background-color: #111827; border: 1px solid #374151; border-radius: 15px; padding: 25px; margin: 20px 0; }
    .stTabs [aria-selected="true"] { background-color: #EF4444 !important; color: white !important; }
    .status-hadir { color: #10B981; font-weight: bold; }
    .status-terlambat { color: #F59E0B; font-weight: bold; }
    .status-alpa { color: #EF4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC FUNCTIONS ---
@st.cache_data(ttl=20)
def fetch_cloud_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        t_col = df.columns[0]
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except: return pd.DataFrame()

# FIX: Tambahkan parameter 'tab_name' untuk membuat key tombol unik
def draw_rows(df, master_list, tab_obj, target_date, tab_name):
    log = {}
    lim_in, lim_out = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    if not df.empty:
        t_c = df.columns[0]
        df_day = df[df[t_c].dt.date == target_date]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_c].time()
            if n not in log: log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < lim_in else "TERLAMBAT"}
            if jam >= lim_out: log[n]["p"] = jam.strftime("%H:%M")

    with tab_obj:
        for p in master_list:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            clr = "status-hadir" if "HADIR" in d['k'] else "status-terlambat" if "TERLAMBAT" in d['k'] else "status-alpa"
            
            c_nm, c_pg, c_sr, c_kt, c_bt = st.columns([3, 1.5, 1.5, 2, 1.2])
            c_nm.markdown(f"<p style='color:#64748B; font-size:10px; margin:0'>👤 PEGAWAI</p><p style='font-size:16px;'>{p}</p>", unsafe_allow_html=True)
            c_pg.markdown(f"<p style='color:#64748B; font-size:10px; margin:0'>PAGI</p><p style='font-size:16px;'>{d['m']}</p>", unsafe_allow_html=True)
            c_sr.markdown(f"<p style='color:#64748B; font-size:10px; margin:0'>SORE</p><p style='font-size:16px;'>{d['p']}</p>", unsafe_allow_html=True)
            c_kt.markdown(f"<p style='color:#64748B; font-size:10px; margin:0; text-align:right'>KET</p><p class='{clr}' style='text-align:right; font-size:15px;'>{d['k']}</p>", unsafe_allow_html=True)
            
            # FIX: Gunakan f"upd_{tab_name}_{p}" agar key selalu unik di setiap tab
            if c_bt.button("Update ✅", key=f"upd_{tab_name}_{p}"):
                info = DATABASE_INFO.get(p)
                fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data={"entry.960346359":p,"entry.468881973":info[0],"entry.159009649":info[1],"submit":"Submit"})
                st.rerun()
            st.markdown("<hr style='margin:5px 0; border-color:rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.markdown('<p class="header-text">MONITORING ABSENSI KPU HSS</p>', unsafe_allow_html=True)
st.markdown(f'<p class="wita-text">{datetime.now().strftime("%H:%M:%S")} WITA</p>', unsafe_allow_html=True)

col_lih, col_ref, col_rek = st.columns(3)
with col_lih:
    with st.expander(f"📅 Lihat Tgl: {st.session_state.get('d_tgl', datetime.now().date())}"):
        st.session_state.d_tgl = st.date_input("Pilih", datetime.now().date(), key="input_tgl")
with col_ref:
    if st.button("🔄 REFRESH"): st.rerun()
with col_rek:
    if st.button("📥 EXCEL REKAP"): st.session_state.show_adv = not st.session_state.get('show_adv', False)

# Advanced Rekap Panel (Simulation Popup)
if st.session_state.get('show_adv', False):
    st.markdown('<div class="rekap-container">', unsafe_allow_html=True)
    st.markdown('<p style="color:#F59E0B; text-align:center; font-weight:bold; font-size:18px;">ADVANCED REKAP EXCEL</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    bln_r = c1.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
    thn_r = c2.selectbox("Tahun", range(2024, 2031), index=2)
    c3, c4 = st.columns(2)
    kat_p = c3.selectbox("Kategori", ["SEMUA PEGAWAI", "PNS", "PPPK"])
    opt_n = ["-- Semua --"]; 
    if kat_p == "PNS": opt_n += MASTER_PNS
    elif kat_p == "PPPK": opt_n += MASTER_PPPK
    nm_p = c4.selectbox("Nama Spesifik", opt_n)
    
    ca, cb = st.columns([2,1])
    if ca.button("🚀 GENERATE EXCEL"):
        df_all = pd.concat([fetch_cloud_data(URL_PNS), fetch_cloud_data(URL_PPPK)])
        t_c, n_c = df_all.columns[0], df_all.columns[1]
        df_f = df_all[df_all[t_c].dt.year == thn_r].copy()
        if bln_r != "SEPANJANG TAHUN": df_f = df_f[df_f[t_c].dt.month == LIST_BULAN.index(bln_r)]
        if kat_p == "PNS": df_f = df_f[df_f[n_c].isin(MASTER_PNS)]
        elif kat_p == "PPPK": df_f = df_f[df_f[n_c].isin(MASTER_PPPK)]
        if "-- Semua" not in nm_p: df_f = df_f[df_f[n_c] == nm_p]
        
        if not df_f.empty:
            df_f[t_c] = df_f[t_c].dt.strftime('%d/%m/%Y %H:%M')
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as wr: df_f.to_excel(wr, index=False)
            st.download_button("💾 KLIK DOWNLOAD", out.getvalue(), f"REKAP_{bln_r}.xlsx", use_container_width=True)
        else: st.error("Data Kosong")
    if cb.button("CLOSE ❌"): st.session_state.show_adv = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. DASHBOARD RENDER ---
df_pns_raw = fetch_cloud_data(URL_PNS)
df_pppk_raw = fetch_cloud_data(URL_PPPK)
df_all_raw = pd.concat([df_pns_raw, df_pppk_raw])

tab1, tab2, tab3 = st.tabs([f"🌍 SEMUA (31)", f"👥 PNS (17)", f"👥 PPPK (14)"])
tgl_target = st.session_state.get('d_tgl', datetime.now().date())

# FIX: Masukkan 'tab_name' yang unik untuk setiap pemanggilan fungsi
draw_rows(df_all_raw, list(DATABASE_INFO.keys()), tab1, tgl_target, "all")
draw_rows(df_pns_raw, MASTER_PNS, tab2, tgl_target, "pns")
draw_rows(df_pppk_raw, MASTER_PPPK, tab3, tgl_target, "pppk")
