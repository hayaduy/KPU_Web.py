import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- CONFIGURATION WEB ---
st.set_page_config(
    page_title="KPU HSS Presence Hub",
    page_icon="📅",
    layout="wide"
)

# Custom CSS agar tampilan di HP lebih cakep & tombol membulat
st.markdown("""
    <style>
    .main { background-color: #0F172A; }
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
    .status-hadir { color: #10B981; font-weight: bold; }
    .status-terlambat { color: #F59E0B; font-weight: bold; }
    .status-alpa { color: #EF4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE PEGAWAI (31 ORANG) ---
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

# --- FUNGSI AMBIL DATA ---
def fetch_data(url):
    try:
        response = requests.get(f"{url}&nc={random.random()}")
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        t_col = df.columns[0]
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except:
        return pd.DataFrame()

# --- HEADER ---
st.title("📊 MONITORING ABSENSI KPU HSS")
st.subheader(f"Waktu: {datetime.now().strftime('%H:%M:%S')} WITA")

# --- SIDEBAR: REKAP EXCEL ---
st.sidebar.header("📥 Download Rekap Excel")
bln_pilih = st.sidebar.selectbox("Pilih Bulan", LIST_BULAN)
thn_pilih = st.sidebar.selectbox("Pilih Tahun", range(2024, 2031), index=2) # Default 2026

kat_pegawai = st.sidebar.selectbox("Kategori", ["SEMUA PEGAWAI", "PNS", "PPPK"])
nama_list = ["-- Semua --"]
if kat_pegawai == "PNS": nama_list += MASTER_PNS
elif kat_pegawai == "PPPK": nama_list += MASTER_PPPK
nama_pilih = st.sidebar.selectbox("Pilih Nama (Opsional)", nama_list)

if st.sidebar.button("Generate Rekap"):
    df_pns = fetch_data(URL_PNS)
    df_pppk = fetch_data(URL_PPPK)
    df_all = pd.concat([df_pns, df_pppk])
    
    # Filter Waktu
    t_col = df_all.columns[0]
    df_res = df_all[df_all[t_col].dt.year == thn_pilih].copy()
    if bln_pilih != "SEPANJANG TAHUN":
        m_idx = LIST_BULAN.index(bln_pilih)
        df_res = df_res[df_res[t_col].dt.month == m_idx]
    
    # Filter Pegawai
    nama_col = df_all.columns[1]
    if kat_pegawai == "PNS": df_res = df_res[df_res[nama_col].isin(MASTER_PNS)]
    elif kat_pegawai == "PPPK": df_res = df_res[df_res[nama_col].isin(MASTER_PPPK)]
    
    if nama_pilih != "-- Semua --":
        df_res = df_res[df_res[nama_col] == nama_pilih]

    if not df_res.empty:
        df_res[t_col] = df_res[t_col].dt.strftime('%d/%m/%Y %H:%M')
        # Buat File Excel di Memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False)
        
        st.sidebar.download_button(
            label="💾 Klik untuk Simpan Excel",
            data=output.getvalue(),
            file_name=f"REKAP_KPU_{bln_pilih}_{thn_pilih}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.sidebar.error("Data tidak ditemukan untuk filter ini.")

# --- DASHBOARD HARIAN ---
st.divider()
tgl_dash = st.date_input("📅 Lihat Pantauan Tanggal:", datetime.now().date())

tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])

def show_dashboard(df, master_list, tab_obj):
    log = {}
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("15:30", "%H:%M").time()
    
    if not df.empty:
        t_col = df.columns[0]
        df_day = df[df[t_col].dt.date == tgl_dash]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_col].time()
            if n not in log:
                log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < t_limit else "TERLAMBAT"}
            if jam >= t_pulang:
                log[n]["p"] = jam.strftime("%H:%M")

    with tab_obj:
        for p in master_list:
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
            with st.expander(f"{p} | {d['k']}"):
                col1, col2 = st.columns(2)
                col1.metric("Jam Pagi", d['m'])
                col2.metric("Jam Sore", d['p'])
                
                # Fitur Update manual via Web
                if st.button(f"Update ✅", key=p):
                    info = DATABASE_INFO.get(p)
                    fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                    payload = {"entry.960346359": p, "entry.468881973": info[0], "entry.159009649": info[1], "submit": "Submit"}
                    requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data=payload)
                    st.success(f"Absen {p} berhasil di-update!")
                    st.rerun()

show_dashboard(fetch_data(URL_PNS), MASTER_PNS, tab1)
show_dashboard(fetch_data(URL_PPPK), MASTER_PPPK, tab2)