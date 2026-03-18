import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import calendar
import pytz
import random
import time
from math import radians, cos, sin, asin, sqrt
from streamlit_js_eval import get_geolocation

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v119.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- 2. CSS CUSTOM (v93.0 Style) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .header-box { text-align: center; color: #F59E0B; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 12px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #cbd5e1; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { background: rgba(255, 255, 255, 0.1) !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIG & DATABASE (31 PEGAWAI LENGKAP) ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

LAT_KANTOR, LON_KANTOR, RADIUS_METER = -2.775087, 115.228639, 100
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. HSS", "-", "PNS", "Ketua KPU", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum...", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum...", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan...", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem...", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem...", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem...", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis...", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI...", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan...", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN...", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum...", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER...", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU...", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan...", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]

# --- 4. HELPERS ---
def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=15)
        df = pd.read_csv(StringIO(r.text))
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how='all')
    except: return None

def clean_logic(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

# --- 5. DIALOGS ---
@st.dialog("Update Data")
def pop_update(nama):
    st.write(f"Update: **{nama}**")
    loc = get_geolocation()
    jarak = hitung_jarak(loc['coords']['latitude'], loc['coords']['longitude'], LAT_KANTOR, LON_KANTOR) if loc else 999
    
    tab_u1, tab_u2 = st.tabs(["Absen", "Lapkin"])
    with tab_u1:
        if jarak <= RADIUS_METER:
            if st.button("🚀 KIRIM ABSEN"):
                st.success("Berhasil!"); time.sleep(1); st.rerun()
        else: st.error(f"Luar Jangkauan ({int(jarak)}m)")
    with tab_u2:
        uraian = st.text_area("Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            st.success("Tersimpan!"); time.sleep(1); st.rerun()

@st.dialog("Rekap Excel", width="large")
def pop_rekap():
    st.write("### Filter Rekap Excel")
    bulan = st.selectbox("Bulan", LIST_BULAN)
    if st.button("GENERATE EXCEL"):
        st.info("Fitur rekap sedang memproses data...")

# --- 6. MAIN UI ---
st.markdown('<div class="header-box">🏛️ MONITORING KPU HSS</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns([2,1,1])
with col_m1: pilih_tgl = st.date_input("Tanggal", label_visibility="collapsed")
with col_m2: 
    if st.button("📊 REKAP"): pop_rekap()
with col_m3:
    if st.button("🔄 REFRESH"): st.rerun()

st.write("---")
tabs = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])

def render_list(urls, masters, tgl, tab_id):
    all_data = []
    for u in urls:
        df = get_clean_df(u)
        if df is not None: all_data.append(df)
    
    df_final = pd.concat(all_data) if all_data else pd.DataFrame()
    t_str = tgl.strftime('%d/%m/%Y')
    
    # Matching Logic
    status_map = {}
    if not df_final.empty:
        for _, r in df_final.iterrows():
            if t_str in str(r.iloc[0]):
                status_map[clean_logic(r.iloc[1])] = "HADIR"

    for i, name in enumerate(masters, 1):
        st_val = status_map.get(clean_logic(name), "ALPA")
        st_color = "status-hadir" if st_val == "HADIR" else "status-alpa"
        
        c_left, c_right = st.columns([8.5, 1.5])
        with c_left:
            st.markdown(f'''
                <div class="employee-card">
                    <div class="emp-name">{i}. {name}</div>
                    <div class="emp-status {st_color}">{st_val}</div>
                </div>
            ''', unsafe_allow_html=True)
        with c_right:
            if st.button("Update", key=f"btn_{tab_id}_{i}"): pop_update(name)

with tabs[0]: render_list([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), pilih_tgl, "all")
with tabs[1]: render_list([URL_PNS], MASTER_PNS, pilih_tgl, "pns")
with tabs[2]: render_list([URL_PPPK], MASTER_PPPK, pilih_tgl, "pppk")
