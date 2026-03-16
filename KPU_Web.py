import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
import time

# --- SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v33.0", layout="wide")

# Link yang Abang berikan (Sudah saya masukkan kembali)
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

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def get_data(url):
    """ Fungsi penarik data dengan proteksi timeout dan anti-cache """
    try:
        # Tambahkan header User-Agent agar tidak dianggap bot oleh Google
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Tambahkan angka acak di URL agar Google memberikan data terbaru (anti-cache)
        clean_url = f"{url}&cache_bust={random.randint(1, 99999)}"
        response = requests.get(clean_url, headers=headers, timeout=15)
        if response.status_code == 200:
            return pd.read_csv(StringIO(response.text))
        else:
            return None
    except:
        return None

# --- UI ---
st.title("🏛️ KPU HSS - MONITORING HUB")
st.write(f"Tanggal: **{datetime.now().strftime('%d %B %Y')}** | Waktu: **{datetime.now().strftime('%H:%M:%S WITA')}**")

tab_dash, tab_input, tab_cetak = st.tabs(["📊 DASHBOARD", "📝 INPUT LAPORAN", "🖨️ CETAK LAPKIN"])

with tab_dash:
    col1, col2 = st.columns(2)
    
    def display_status(url, master, title):
        df = get_data(url)
        if df is not None:
            df.columns = df.columns.str.strip()
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
            df_today = df[df.iloc[:, 0].dt.date == datetime.now().date()]
            
            log = {}
            for _, r in df_today.iterrows():
                nama_p, jam_p = str(r.iloc[1]).strip(), r.iloc[0]
                if nama_p not in log:
                    log[nama_p] = {"m": jam_p.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam_p.hour < 9 else "TERLAMBAT"}
                if jam_p.hour >= 15:
                    log[nama_p]["p"] = jam_p.strftime("%H:%M")
            
            final = []
            for i, p in enumerate(master, 1):
                d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
                final.append({"No": i, "Nama": p, "M": d['m'], "P": d['p'], "Status": d['k']})
            
            st.write(f"### {title}")
            st.dataframe(pd.DataFrame(final), use_container_width=True, hide_index=True)
        else:
            st.error(f"⚠️ Gagal memuat data {title}. Silakan cek status 'Publish to Web' di Google Sheets.")

    with col1: display_status(URL_PNS, MASTER_PNS, "PNS")
    with col2: display_status(URL_PPPK, MASTER_PPPK, "PPPK")

with tab_input:
    st.subheader("Form Update Kehadiran & Lapkin")
    with st.form("form_input"):
        nama_in = st.selectbox("Pilih Nama", list(DATABASE_INFO.keys()))
        tipe_in = st.radio("Jenis Laporan", ["Datang (Pagi)", "Lapkin (Sore)"])
        status_in = "Hadir"
        hasil_in = "-"
        if tipe_in == "Lapkin (Sore)":
            status_in = st.selectbox("Status", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
            hasil_in = st.text_area("Uraian Hasil Kerja")
        
        if st.form_submit_button("KIRIM DATA"):
            info = DATABASE_INFO[nama_in]
            payload = {"nama": nama_in, "nip": info[0], "jabatan": info[1], "status": status_in, "hasil": hasil_in}
            try:
                res = requests.post(SCRIPT_URL, json=payload, timeout=10)
                st.success(f"Data {nama_in} berhasil dikirim!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("Gagal mengirim data.")

with tab_cetak:
    st.subheader("Cetak Laporan Kinerja (Excel)")
    c_bln = st.selectbox("Pilih Bulan", LIST_BULAN, index=datetime.now().month-1)
    c_nama = st.selectbox("Pilih Nama Pegawai", list(DATABASE_INFO.keys()))
    
    if st.button("Generate Excel"):
        df_lap = get_data(URL_LAPKIN)
        if df_lap is not None:
            df_lap.iloc[:, 0] = pd.to_datetime(df_lap.iloc[:, 0], errors='coerce')
            idx_bln = LIST_BULAN.index(c_bln) + 1
            df_f = df_lap[(df_lap.iloc[:, 1] == c_nama) & (df_lap.iloc[:, 0].dt.month == idx_bln)].copy()
            df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
            
            if not df_f.empty:
                info = DATABASE_INFO[c_nama]
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    header = [["LAPORAN KERJA HARIAN"], ["KPU KABUPATEN HSS"], [], ["Bulan", c_bln], ["Nama", c_nama], ["Jabatan", info[1]], [], ["No", "Tanggal", "Kegiatan", "Output", "Ket"]]
                    body = []
                    for i, (_, r) in enumerate(df_f.iterrows(), 1):
                        body.append([i, f"{r.iloc[0].day} {c_bln} {r.iloc[0].year}", f"Tugas {info[1]}", r.iloc[5], r.iloc[4]])
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                    pd.DataFrame(body).to_excel(writer, startrow=8, index=False, header=False, sheet_name="Lapkin")
                st.download_button("📥 Download Excel", output.getvalue(), f"LAPKIN_{c_nama}.xlsx")
            else:
                st.warning("Data tidak ditemukan.")

if st.button("🔄 REFRESH DASHBOARD"):
    st.rerun()
