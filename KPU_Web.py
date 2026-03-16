import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
import time

# --- SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v34.0", layout="wide", page_icon="🏛️")

# --- KONFIGURASI URL ---
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

def get_safe_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=15)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        # Perbaikan Error di Gambar: Memaksa kolom 0 menjadi datetime dan buang data rusak
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        return df.dropna(subset=[df.columns[0]])
    except:
        return None

# --- UI START ---
st.title("🏛️ KPU HSS - MONITORING HUB")
st.write(f"Waktu Sekarang: **{datetime.now().strftime('%H:%M:%S WITA')}**")

tab_dash, tab_input, tab_cetak = st.tabs(["📊 DASHBOARD MONITORING", "📝 INPUT LAPORAN", "🖨️ CETAK LAPKIN"])

with tab_dash:
    col1, col2 = st.columns(2)
    def render_dash(url, master, title):
        df = get_safe_data(url)
        st.write(f"### {title}")
        if df is not None:
            today = datetime.now().date()
            # Filter tanggal hari ini dengan aman
            df_today = df[df.iloc[:, 0].dt.date == today]
            log = {}
            for _, r in df_today.iterrows():
                nama, jam = str(r.iloc[1]).strip(), r.iloc[0]
                if nama not in log:
                    log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam.hour < 9 else "TERLAMBAT"}
                if jam.hour >= 15:
                    log[nama]["p"] = jam.strftime("%H:%M")
            
            final_rows = []
            for i, p in enumerate(master, 1):
                d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
                final_rows.append({"No": i, "Nama Pegawai": p, "M": d['m'], "P": d['p'], "Status": d['k']})
            st.dataframe(pd.DataFrame(final_rows), use_container_width=True, hide_index=True)
        else:
            st.error(f"Gagal memuat data {title}")

    with col1: render_dash(URL_PNS, MASTER_PNS, "PNS")
    with col2: render_dash(URL_PPPK, MASTER_PPPK, "PPPK")

with tab_input:
    st.subheader("Form Update Laporan")
    with st.form("input_form"):
        f_nama = st.selectbox("Nama Pegawai", list(DATABASE_INFO.keys()))
        f_tipe = st.radio("Tipe Laporan", ["Datang (Pagi)", "Sore (Lapkin)"])
        f_stat = "Hadir"
        f_hasil = "-"
        if f_tipe == "Sore (Lapkin)":
            f_stat = st.selectbox("Status", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
            f_hasil = st.text_area("Uraian Hasil Kerja/Output")
        
        if st.form_submit_button("KIRIM KE SPREADSHEET"):
            info = DATABASE_INFO[f_nama]
            payload = {"nama": f_nama, "nip": info[0], "jabatan": info[1], "status": f_stat, "hasil": f_hasil}
            try:
                requests.post(SCRIPT_URL, json=payload, timeout=10)
                st.success(f"Sukses mengupdate {f_nama}!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("Gagal mengirim data.")

with tab_cetak:
    st.subheader("Generate Laporan Excel")
    c_bulan = st.selectbox("Pilih Bulan", LIST_BULAN, index=datetime.now().month-1)
    c_nama = st.selectbox("Nama Pegawai", list(DATABASE_INFO.keys()), key="c_p")
    
    if st.button("Download Excel"):
        df_l = get_safe_data(URL_LAPKIN)
        if df_l is not None:
            idx_b = LIST_BULAN.index(c_bulan) + 1
            # Filter Nama, Bulan, dan Pastikan ada isi Hasil Kerja
            df_f = df_l[(df_l.iloc[:, 1] == c_nama) & (df_l.iloc[:, 0].dt.month == idx_b)].copy()
            df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
            
            if not df_f.empty:
                info = DATABASE_INFO[c_nama]
                out = BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as writer:
                    header = [["LAPORAN KERJA HARIAN"], ["KPU KABUPATEN HSS"], [], ["Nama", c_nama], ["Jabatan", info[1]], [], ["No", "Tanggal", "Kegiatan", "Hasil", "Ket"]]
                    body = [[i+1, r.iloc[0].strftime('%d %B %Y'), f"Tugas {info[1]}", r.iloc[5], r.iloc[4]] for i, (_, r) in enumerate(df_f.iterrows())]
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                    pd.DataFrame(body).to_excel(writer, startrow=7, index=False, header=False, sheet_name="Lapkin")
                st.download_button("📥 Klik Download", out.getvalue(), f"LAPKIN_{c_nama}.xlsx")
            else:
                st.warning("Data sore tidak ditemukan.")

if st.button("🔄 REFRESH SEMUA DATA"):
    st.rerun()
