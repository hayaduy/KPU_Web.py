import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v16.9",
    page_icon="🏢",
    layout="wide"
)

# --- 2. LUXURY GLASS CSS (COMPACT & CENTERED) ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Header Container */
    .header-container {
        text-align: center;
        padding: 20px 0 5px 0;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
    }
    .main-title { font-size: 40px; font-weight: 850; letter-spacing: -1px; margin-bottom: 0; color: white; }
    .time-glow { font-size: 28px; color: #F59E0B; text-shadow: 0 0 15px rgba(245, 158, 11, 0.4); font-weight: bold; }

    /* Nav & Tab Center */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 10px; }
    .stTabs [aria-selected="true"] { background-color: #8B0000 !important; color: white !important; }

    /* GLASS CARD - COMPACT & NARROW */
    /* Kita batasi lebar maksimal agar tidak terlalu mojok */
    .staff-row-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        padding: 6px 15px !important; /* Padding lebih kecil agar rapat */
        margin: 0 auto 6px auto !important; /* Margin auto agar ke tengah */
        max-width: 900px; /* Membatasi lebar agar tidak mentok kiri-kanan */
        transition: 0.2s;
    }
    .staff-row-card:hover { border-color: rgba(245, 158, 11, 0.3) !important; }
    
    .label-micro { color: #94a3b8; font-size: 8px; text-transform: uppercase; margin: 0; line-height: 1; }
    .val-mini { font-size: 14px; font-weight: 500; color: white; margin: 0; line-height: 1.2; }
    
    .status-hadir { color: #10B981; font-weight: bold; font-size: 13px; }
    .status-terlambat { color: #F59E0B; font-weight: bold; font-size: 13px; }
    .status-alpa { color: #EF4444; font-weight: bold; font-size: 13px; }

    /* Button dalam card */
    div.stButton > button {
        border-radius: 20px !important;
        height: 32px !important;
        font-size: 12px !important;
        padding: 0 10px !important;
    }
    
    /* Nav Buttons di atas */
    .nav-btn button { height: 45px !important; border-radius: 25px !important; font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (Tetap Lengkap) ---
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

# --- 4. DATA LOGIC ---
@st.cache_data(ttl=15)
def fetch_cloud_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        t_col = df.columns[0]
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except: return pd.DataFrame()

def draw_rows(df, master_list, tab_obj, target_date, tab_name):
    log = {}
    limit_in, limit_out = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    
    if not df.empty:
        t_c, n_c = df.columns[0], df.columns[1]
        df_day = df[df[t_c].dt.date == target_date].copy()
        for p in master_list:
            match = df_day[df_day[n_c].str.contains(p, case=False, na=False, regex=False)]
            if not match.empty:
                for _, r in match.iterrows():
                    jam = r[t_c].time()
                    if p not in log:
                        log[p] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < limit_in else "TERLAMBAT"}
                    if jam >= limit_out: log[p]["p"] = jam.strftime("%H:%M")

    with tab_obj:
        # Gunakan spacer columns agar card ke tengah dan tidak terlalu lebar
        for p in master_list:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
            clr_class = "status-hadir" if "HADIR" in d['k'] else "status-terlambat" if "TERLAMBAT" in d['k'] else "status-alpa"
            
            # Membatasi lebar baris dengan kolom kosong di pinggir
            _, center_col, _ = st.columns([1, 8, 1])
            with center_col:
                st.markdown(f'<div class="staff-row-card">', unsafe_allow_html=True)
                c_nm, c_pg, c_sr, c_kt, c_bt = st.columns([3, 1, 1, 1.8, 1.2])
                c_nm.markdown(f"<p class='label-micro'>👤 PEGAWAI</p><p class='val-mini'>{p}</p>", unsafe_allow_html=True)
                c_pg.markdown(f"<p class='label-micro'>PAGI</p><p class='val-mini'>{d['m']}</p>", unsafe_allow_html=True)
                c_sr.markdown(f"<p class='label-micro'>SORE</p><p class='val-mini'>{d['p']}</p>", unsafe_allow_html=True)
                c_kt.markdown(f"<p class='label-micro' style='text-align:right'>KET</p><p class='{clr_class}' style='text-align:right'>{d['k']}</p>", unsafe_allow_html=True)
                if c_bt.button("Update ✅", key=f"upd_{tab_name}_{p}", use_container_width=True):
                    info = DATABASE_INFO.get(p)
                    fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                    requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data={"entry.960346359":p,"entry.468881973":info[0],"entry.159009649":info[1],"submit":"Submit"})
                    st.cache_data.clear(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.markdown("""
    <div class="header-container">
        <p class="main-title">MONITORING ABSENSI KPU HSS</p>
        <p class="time-glow">{} WITA</p>
    </div>
    """.format(datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)

# Navigasi Buttons
_, col_lih, col_ref, col_rek, _ = st.columns([1, 2, 2, 2, 1])
with col_lih:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    with st.expander(f"📅 Tgl: {st.session_state.get('d_tgl', datetime.now().date())}"):
        st.session_state.d_tgl = st.date_input("Pilih", datetime.now().date(), key="input_tgl")
    st.markdown('</div>', unsafe_allow_html=True)
with col_ref:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("🔄 REFRESH DATA", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col_rek:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("📥 EXCEL REKAP", use_container_width=True): st.session_state.show_rekap = not st.session_state.get('show_rekap', False)
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get('show_rekap', False):
    _, c_rek, _ = st.columns([1, 6, 1])
    with c_rek:
        st.markdown("<div style='background-color:rgba(17, 24, 39, 0.7); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.05); margin-bottom:15px;'>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        bln = r1.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
        thn = r2.selectbox("Tahun", range(2024, 2031), index=2)
        kat = r3.selectbox("Kategori", ["SEMUA", "PNS", "PPPK"])
        if st.button("🚀 GENERATE EXCEL", use_container_width=True):
            df_all = pd.concat([fetch_cloud_data(URL_PNS), fetch_cloud_data(URL_PPPK)])
            t_c = df_all.columns[0]
            df_f = df_all[df_all[t_c].dt.year == thn].copy()
            if bln != "SEPANJANG TAHUN": df_f = df_f[df_f[t_c].dt.month == LIST_BULAN.index(bln)]
            if not df_f.empty:
                out = BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as wr: df_f.to_excel(wr, index=False)
                st.download_button("💾 DOWNLOAD", out.getvalue(), f"REKAP_{bln}.xlsx", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. DASHBOARD RENDER ---
df_pns_raw = fetch_cloud_data(URL_PNS)
df_pppk_raw = fetch_cloud_data(URL_PPPK)
df_all_raw = pd.concat([df_pns_raw, df_pppk_raw])

tab_all, tab_pns, tab_pppk = st.tabs([f"🌍 SEMUA (31)", f"👥 PNS (17)", f"👥 PPPK (14)"])
tgl_target = st.session_state.get('d_tgl', datetime.now().date())

draw_rows(df_all_raw, list(DATABASE_INFO.keys()), tab_all, tgl_target, "all")
draw_rows(df_pns_raw, MASTER_PNS, tab_pns, tgl_target, "pns")
draw_rows(df_pppk_raw, MASTER_PPPK, tab_pppk, tgl_target, "pppk")
