import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import pytz
import random
import time

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v43.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

# --- 2. CSS CUSTOM: GRADIENT & GLASSMORPHISM ---
st.markdown("""
    <style>
    /* Background Gradient Oranye, Hitam, Marun */
    .stApp {
        background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%);
        background-attachment: fixed;
    }
    
    .header-box { text-align: center; color: #F59E0B; font-size: 32px; font-weight: bold; margin-bottom: 0px; }
    .clock-box { text-align: center; color: white; font-size: 18px; margin-bottom: 15px; font-family: monospace; }
    
    /* Efek Kaca untuk Baris Pegawai */
    .employee-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 10px 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        margin-bottom: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #cbd5e1; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; }
    
    .status-hadir { color: #10B981; text-shadow: 0 0 10px rgba(16,185,129,0.5); }
    .status-alpa { color: #EF4444; text-shadow: 0 0 10px rgba(239,68,68,0.5); }
    .status-terlambat { color: #F59E0B; text-shadow: 0 0 10px rgba(245,158,11,0.5); }
    
    /* Efek Kaca untuk Tombol */
    .stButton>button {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid #F59E0B !important;
    }
    
    .block-container { max-width: 1050px; padding-top: 1.5rem; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURATION & DATABASE ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysGislOC0219H1_sqib7TblYTTUngiYYIzaUtLG4_tEfxUl6OsnYLzjvqpj1POCRc/exec"

DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris KPU", "Sekretariat KPU Kab. HSS"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. HSS"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. HSS"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum dan SDM", "Sekretariat KPU Kab. HSS"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. HSS"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. HSS"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. HSS"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. HSS"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional", "Sekretariat KPU Kab. HSS"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. HSS"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. HSS"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. HSS"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. HSS"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. HSS"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "Basuki Rahmat": ["197705222024211007", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. HSS"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. HSS"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL", "Sekretariat KPU Kab. HSS"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. HSS"],
    "Abdurrahman": ["198810122025211031", "Staf Subbag Sosdiklih, Parmas dan SDM", "Sekretariat KPU Kab. HSS"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. HSS"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. HSS"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. HSS"]
}

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 4. DIALOGS (POP-UPS) ---

@st.dialog("Update Data Pegawai")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    tipe = st.radio("Pilih Update:", ["Pagi (Absen Datang)", "Sore (Laporan Kerja)"])
    st_fix = "Hadir"
    h_kerja = "-"
    if tipe == "Sore (Laporan Kerja)":
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Uraian Hasil Kerja/Output:")
    if st.button("🚀 KIRIM DATA"):
        info = DATABASE_INFO[nama]
        payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja}
        res = requests.post(SCRIPT_URL, json=payload)
        if "Success" in res.text:
            st.success("Berhasil!")
            time.sleep(1); st.rerun()

@st.dialog("Rekap Absensi Bulanan")
def pop_rekap():
    st.write("### Download Rekap Seluruh Pegawai")
    r_b = st.selectbox("Pilih Bulan Rekap:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    if st.button("📥 GENERATE REKAP EXCEL"):
        try:
            r1 = requests.get(f"{URL_PNS}&nc={random.random()}").text
            r2 = requests.get(f"{URL_PPPK}&nc={random.random()}").text
            df = pd.concat([pd.read_csv(StringIO(r1)), pd.read_csv(StringIO(r2))], ignore_index=True)
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
            bulan_idx = LIST_BULAN.index(r_b) + 1
            df_f = df[df.iloc[:, 0].dt.month == bulan_idx].copy()
            
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                df_f.to_excel(writer, index=False, sheet_name=f"Rekap_{r_b}")
            st.download_button("📂 Download Rekap", out.getvalue(), f"REKAP_ABSENSI_{r_b}.xlsx")
        except: st.error("Gagal menarik data absensi.")

@st.dialog("Cetak Lapkin Bulanan")
def pop_cetak():
    c_b = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    c_n = st.selectbox("Pilih Pegawai:", list(DATABASE_INFO.keys()))
    if st.button("📊 GENERATE EXCEL"):
        raw = requests.get(f"{URL_LAPKIN}&nc={random.random()}").text
        df_l = pd.read_csv(StringIO(raw))
        df_l.iloc[:, 0] = pd.to_datetime(df_l.iloc[:, 0], dayfirst=True, errors='coerce')
        idx = LIST_BULAN.index(c_b) + 1
        df_f = df_l[(df_l.iloc[:, 1] == c_n) & (df_l.iloc[:, 0].dt.month == idx)].copy()
        df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
        if not df_f.empty:
            info = DATABASE_INFO[c_n]
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                header = [["LAPORAN KERJA"], ["KPU HSS"], [], ["Nama", c_n], ["Jabatan", info[1]], [], ["No", "Tanggal", "Kegiatan", "Hasil", "Ket"]]
                body = [[i+1, r.iloc[0].strftime('%d %B %Y'), f"Tugas {info[1]}", r.iloc[5], r.iloc[4]] for i, (_, r) in enumerate(df_f.iterrows())]
                pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                pd.DataFrame(body).to_excel(writer, startrow=8, index=False, header=False, sheet_name="Lapkin")
            st.download_button("📥 DOWNLOAD", out.getvalue(), f"LAPKIN_{c_n}.xlsx")
        else: st.warning("Data tidak ditemukan.")

# --- 5. MAIN UI ---
st.markdown('<div class="header-box">🏛️ MONITORING KPU HSS</div>', unsafe_allow_html=True)
st.markdown(f'<div class="clock-box">{datetime.now(wita_tz).strftime("%H:%M:%S WITA")}</div>', unsafe_allow_html=True)

# BARIS TOMBOL UTAMA (CENTER)
_, mid, _ = st.columns([0.1, 5, 0.1])
with mid:
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a: 
        if st.button("🔄 REFRESH"): st.rerun()
    with col_b: 
        pilih_tgl = st.date_input("Tgl", value=datetime.now(wita_tz).date(), label_visibility="collapsed")
    with col_c: 
        if st.button("📥 REKAP"): pop_rekap()
    with col_d: 
        if st.button("🖨️ LAPKIN"): pop_cetak()

st.write("---")
tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PNS", "👥 PPPK"])

def render_ui(urls, masters, tgl_target, tab_id):
    all_dfs = []
    for u in urls:
        try:
            r = requests.get(f"{u}&nc={random.random()}", timeout=15)
            all_dfs.append(pd.read_csv(StringIO(r.text)))
        except: continue
    
    if not all_dfs: return
    df = pd.concat(all_dfs, ignore_index=True)
    t_str, t_alt = tgl_target.strftime('%d/%m/%Y'), tgl_target.strftime('%Y-%m-%d')
    
    log = {}
    df.columns = df.columns.str.strip()
    for _, r in df.iterrows():
        ts = str(r.iloc[0])
        if t_str in ts or t_alt in ts:
            nama = str(r.iloc[1]).strip()
            dt = pd.to_datetime(ts, dayfirst=True, errors='coerce')
            if pd.isna(dt): continue
            if nama not in log:
                log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
            if dt.hour >= 15: log[nama]["p"] = dt.strftime("%H:%M")

    for i, p in enumerate(masters, 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        st_cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        
        c_main, c_side = st.columns([8.5, 1.5])
        with c_main:
            st.markdown(f"""
                <div class="employee-card">
                    <div class="emp-name">{i}. {p}</div>
                    <div class="emp-time">M: <b>{d['m']}</b></div>
                    <div class="emp-time">P: <b>{d['p']}</b></div>
                    <div class="emp-status {st_cls}">{d['k']}</div>
                </div>
            """, unsafe_allow_html=True)
        with c_side:
            if st.button("Update", key=f"btn_{p}_{tab_id}"): pop_update(p)

with tab_all: render_ui([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), pilih_tgl, "all")
with tab_pns: render_ui([URL_PNS], list(DATABASE_INFO.keys())[:17], pilih_tgl, "pns")
with tab_pppk: render_ui([URL_PPPK], list(DATABASE_INFO.keys())[17:], pilih_tgl, "pppk")
