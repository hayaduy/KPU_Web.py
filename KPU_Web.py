import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- 1. CONFIGURATION & PREMIUM THEME (Custom CSS) ---
st.set_page_config(
    page_title="KPU HSS Presence Hub v12.2",
    page_icon="📊",
    layout="wide", # Pakai wide mode agar lega di desktop
    initial_sidebar_state="expanded"
)

# Mantra Sakti CSS untuk mengubah Streamlit jadi Premium Navy & Amber
st.markdown("""
    <style>
    /* Background Utama */
    .main {
        background-color: #0F172A;
        color: white;
    }
    
    /* Font Global */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
    }

    /* Styling Header */
    h1 {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        text-align: center;
        padding-bottom: 0px !important;
    }
    h3 {
        color: #F59E0B !important; /* Warna Amber untuk Jam */
        text-align: center;
        margin-top: 0px !important;
    }

    /* Styling Expander (Kartu Pegawai) -> Ini Kunci Keren-nya */
    div[data-testid="stExpander"] {
        background-color: rgba(30, 41, 59, 0.5) !important; /* Transparan ala Glass */
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
        transition: transform 0.2s;
    }
    div[data-testid="stExpander"]:hover {
        transform: translateY(-3px); /* Efek melayang saat di-hover */
        border-color: rgba(245, 158, 11, 0.4) !important;
    }
    
    /* Styling Tombol Standar */
    .stButton>button {
        width: 100%;
        border-radius: 20px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    
    /* Warna Status (Hadir, Terlambat, Alpa) */
    .status-hadir { color: #10B981 !important; font-weight: bold; }
    .status-terlambat { color: #F59E0B !important; font-weight: bold; }
    .status-alpa { color: #EF4444 !important; font-weight: bold; }

    /* Menyembunyikan elemen standar Streamlit agar lebih bersih */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE PEGAWAI (31 ORANG) ---
# [KODE DATABASE SAMA SEPERTI SEBELUMNYA, TIDAK DIUBAH]
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

# Link Database (Tidak Berubah)
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# --- 3. LOGIKA AMBIL DATA (Sama) ---
@st.cache_data(ttl=60) # Cache 1 menit agar tidak crash server Google
def fetch_cloud_data(url):
    try:
        response = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        t_col = df.columns[0]
        # Fix Error Datetime Accessor (Anti-Crash)
        df[t_col] = pd.to_datetime(df[t_col], dayfirst=True, errors='coerce')
        return df.dropna(subset=[t_col]).sort_values(by=t_col)
    except Exception as e:
        return pd.DataFrame() # Kembalikan DF kosong jika error

# --- 4. UI SIDEBAR (Premium Sidebar) ---
st.sidebar.title("📥 Rekapitulasi Excel")
with st.sidebar.expander("⚙️ Advanced Filter", expanded=True):
    bln_p = st.selectbox("Bulan", LIST_BULAN, index=datetime.now().month)
    thn_p = st.selectbox("Tahun", range(2024, 2031), index=2) # Default 2026
    
    kat_p = st.radio("Kategori Pegawai", ["SEMUA", "PNS", "PPPK"])
    
    nama_options = ["-- Semua Pegawai di Kategori --"]
    if kat_p == "PNS": nama_options += MASTER_PNS
    elif kat_p == "PPPK": nama_options += MASTER_PPPK
    nama_p = st.selectbox("Pilih Nama (Opsional)", nama_options)

    # Tombol Generate yang Premium
    if st.button("🚀 SIAPKAN FILE EXCEL"):
        df_pns = fetch_cloud_data(URL_PNS)
        df_pppk = fetch_cloud_data(URL_PPPK)
        df_all = pd.concat([df_pns, df_pppk])
        t_col = df_all.columns[0]
        nama_col = df_all.columns[1]

        # Filter Waktu
        df_f = df_all[df_all[t_col].dt.year == thn_p].copy()
        if bln_p != "SEPANJANG TAHUN":
            m_idx = LIST_BULAN.index(bln_p)
            df_f = df_f[df_f[t_col].dt.month == m_idx]

        # Filter Pegawai
        if kat_p == "PNS": df_f = df_f[df_f[nama_col].isin(MASTER_PNS)]
        elif kat_p == "PPPK": df_f = df_f[df_f[nama_col].isin(MASTER_PPPK)]
        
        if nama_p != "-- Semua Pegawai di Kategori --":
            df_f = df_f[df_f[nama_col] == nama_p]

        if not df_f.empty:
            df_f[t_col] = df_f[t_col].dt.strftime('%d/%m/%Y %H:%M')
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_f.to_excel(writer, index=False)
            
            # Tombol Download Hijau Mantap
            st.download_button(
                label="✅ KLIK UNTUK DOWNLOAD (Folder Downloads HP)",
                data=output.getvalue(),
                file_name=f"REKAP_ABSEN_{kat_p}_{bln_p}_{thn_p}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Data tidak ditemukan untuk kriteria tersebut.")

# --- 5. DASHBOARD HARIAN (Premium Dashboard ala HP) ---
st.header("MONITORING ABSENSI KPU HSS")
st.subheader(f"{datetime.now().strftime('%H:%M:%S')} WITA")

st.divider() # Garis pembatas clean

# Filter Tanggal Dashboard yang simple
tgl_d = st.date_input("📅 Pantau Tanggal Dashboard:", datetime.now().date())

# Tabs dengan gaya membulat
tab1, tab2 = st.tabs(["👥 STATUS PNS", "👥 STATUS PPPK"])

# Fungsi untuk merender daftar pegawai dalam bentuk "Kartu" (Mobile Friendly)
def render_staff_cards(df, master, tab_obj):
    log = {}
    t_limit, t_pulang = [datetime.strptime(x, "%H:%M").time() for x in ["09:00", "15:30"]]
    
    if not df.empty:
        t_col = df.columns[0]
        df_day = df[df[t_col].dt.date == tgl_d]
        for _, r in df_day.iterrows():
            n, jam = str(r.iloc[1]).strip(), r[t_col].time()
            if n not in log:
                log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam < t_limit else "TERLAMBAT"}
            if jam >= t_pulang:
                log[n]["p"] = jam.strftime("%H:%M")

    with tab_obj:
        # Loop Pegawai - Membuat kartu individual
        for idx, p in enumerate(master, 1):
            d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
            
            # Menentukan warna status
            status_style = "status-hadir" if "HADIR" in d['k'] else "status-terlambat" if "TERLAMBAT" in d['k'] else "status-alpa"
            
            # MEMBUAT KARTU DENGAN EXPANDER (Ini yang bikin Mobile Friendly)
            with st.expander(f"{p}"):
                # Susunan Kolom di dalam kartu
                c1, c2, c3 = st.columns([1, 1, 1.5]) # Kolom 3 sedikit lebih lebar untuk status
                
                c1.metric(label="Jam Pagi", value=d['m'])
                c2.metric(label="Jam Sore", value=d['p'])
                c3.markdown(f"Status:<br><span class='{status_style}'>{d['k']}</span>", unsafe_allow_html=True)
                
                # Tombol Update di dalam kartu (sedikit dikecilkan agar responsif)
                if st.button(f"Update ✅ {p[:10]}...", key=p): # key=p agar tombol unik
                    info = DATABASE_INFO.get(p)
                    fid = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if p in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
                    payload = {"entry.960346359": p, "entry.468881973": info[0], "entry.159009649": info[1], "submit": "Submit"}
                    
                    try:
                        requests.post(f"https://docs.google.com/forms/d/e/{fid}/formResponse", data=payload, timeout=5)
                        st.success(f"Absen {p} berhasil di-update!")
                        st.rerun() # Refresh dashboard
                    except:
                        st.error("Gagal terhubung ke Cloud!")

# Menampilkan data
render_staff_cards(fetch_cloud_data(URL_PNS), MASTER_PNS, tab1)
render_staff_cards(fetch_cloud_data(URL_PPPK), MASTER_PPPK, tab2)
