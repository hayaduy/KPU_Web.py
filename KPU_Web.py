import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="KPU HSS Presence Hub", layout="wide")

# Custom CSS untuk tampilan Dark Mode ala KPU
st.markdown("""
    <style>
    .main { background-color: #0F172A; color: white; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .status-hadir { color: #10B981; font-weight: bold; }
    .status-terlambat { color: #F59E0B; font-weight: bold; }
    .status-alpa { color: #EF4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

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

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysGislOC0219H1_sqib7TblYTTUngiYYIzaUtLG4_tEfxUl6OsnYLzjvqpj1POCRc/exec"

def format_tgl_indo(dt):
    return f"{dt.day:02d} {LIST_BULAN[dt.month-1]} {dt.year}"

def send_data(nama, status, hasil):
    info = DATABASE_INFO.get(nama)
    payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": status, "hasil": hasil}
    try:
        res = requests.post(SCRIPT_URL, json=payload, timeout=10)
        return "Success" in res.text
    except:
        return False

# --- UI STREAMLIT ---
st.title("🏛️ MONITORING ABSENSI & KINERJA KPU HSS")
st.subheader(f"🕒 {datetime.now().strftime('%H:%M:%S WITA')}")

col_dash, col_action = st.columns([3, 1])

with col_action:
    st.write("### 📝 Input Laporan")
    with st.expander("Klik untuk Update"):
        target_name = st.selectbox("Pilih Pegawai", list(DATABASE_INFO.keys()))
        opt_type = st.radio("Tipe Update", ["Absen Pagi (Datang)", "Laporan Sore (Lapkin)"])
        
        if opt_type == "Laporan Sore (Lapkin)":
            stat_fix = st.selectbox("Status", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
            hasil_kerja = st.text_area("Hasil Kerja/Output")
        else:
            stat_fix = "Hadir"
            hasil_kerja = "-"
            
        if st.button("Kirim Update"):
            if opt_type == "Laporan Sore (Lapkin)" and not hasil_kerja.strip():
                st.error("Hasil kerja wajib diisi!")
            else:
                success = send_data(target_name, stat_fix, hasil_kerja)
                if success:
                    st.success(f"Berhasil update {target_name}!")
                    st.rerun()
                else:
                    st.error("Gagal mengirim data.")

    st.write("---")
    st.write("### 📥 Cetak Lapkin")
    pilih_bulan = st.selectbox("Bulan Cetak", LIST_BULAN, index=datetime.now().month-1)
    pilih_nama = st.selectbox("Pegawai Lapkin", list(DATABASE_INFO.keys()))
    
    if st.button("Generate Excel Lapkin"):
        try:
            raw = requests.get(f"{URL_LAPKIN}&nc={random.random()}").text
            df = pd.read_csv(StringIO(raw))
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
            
            bulan_idx = LIST_BULAN.index(pilih_bulan) + 1
            df_f = df[(df.iloc[:, 1] == pilih_nama) & (df.iloc[:, 0].dt.month == bulan_idx)].copy()
            df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
            
            if df_f.empty:
                st.warning("Data tidak ditemukan.")
            else:
                # Logika pembuatan file Excel (Header + Body)
                info = DATABASE_INFO[pilih_nama]
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    header_data = [
                        ["LAPORAN KERJA HARIAN BULANAN"],
                        ["SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN"], [],
                        ["", "Bulan", f": {pilih_bulan}"],
                        ["", "Nama", f": {pilih_nama.upper()}"],
                        ["", "NIP", f": {info[0]}"],
                        ["", "Jabatan", f": {info[1]}"],
                        ["", "Unit Kerja", f": {info[2]}"], [],
                        ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja / Output", "Keterangan"]
                    ]
                    body = []
                    for i, (_, row) in enumerate(df_f.iterrows(), 1):
                        body.append([i, format_tgl_indo(row.iloc[0]), f"Melaksanakan tugas sebagai {info[1]}", row.iloc[5], row.iloc[4]])
                    
                    pd.DataFrame(header_data).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                    pd.DataFrame(body).to_excel(writer, startrow=10, index=False, header=False, sheet_name="Lapkin")
                
                st.download_button(label="📥 Download File", data=output.getvalue(), file_name=f"LAPKIN_{pilih_nama}_{pilih_bulan}.xlsx")
        except Exception as e:
            st.error(f"Error: {e}")

with col_dash:
    tab1, tab2 = st.tabs(["PNS", "PPPK"])
    
    def fetch_and_draw(url, master):
        try:
            res = requests.get(f"{url}&nc={random.random()}", timeout=10)
            df = pd.read_csv(StringIO(res.text))
            df.columns = df.columns.str.strip()
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
            
            today = datetime.now().date()
            df_day = df[df.iloc[:, 0].dt.date == today]
            
            log = {}
            for _, r in df_day.iterrows():
                n, jam = str(r.iloc[1]).strip(), r.iloc[0].time()
                if n not in log:
                    log[n] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam.hour < 9 else "TERLAMBAT"}
                if jam.hour >= 15:
                    log[n]["p"] = jam.strftime("%H:%M")
            
            display_data = []
            for i, p in enumerate(master, 1):
                d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
                display_data.append({
                    "No": i, "Nama Pegawai": p, "Masuk": d["m"], "Pulang": d["p"], "Status": d["k"]
                })
            st.table(pd.DataFrame(display_data))
        except:
            st.error("Gagal mengambil data dari Google Sheets.")

    with tab1:
        fetch_and_draw(URL_PNS, MASTER_PNS)
    with tab2:
        fetch_and_draw(URL_PPPK, MASTER_PPPK)

if st.button("🔄 Refresh Data"):
    st.rerun()
