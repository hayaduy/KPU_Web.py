import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
import time

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="KPU HSS Presence Hub v32.0", layout="wide", page_icon="🏛️")

# CSS Custom agar tampilan tetap profesional dan gelap
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #F59E0B; }
    .stTab { background-color: transparent !important; }
    .stButton>button { border-radius: 12px; height: 3em; font-weight: bold; }
    .stTable { background-color: #1E293B; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE PEGAWAI ---
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

# --- URL KONFIGURASI ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbysGislOC0219H1_sqib7TblYTTUngiYYIzaUtLG4_tEfxUl6OsnYLzjvqpj1POCRc/exec"

def format_tgl_indo(dt):
    return f"{dt.day:02d} {LIST_BULAN[dt.month-1]} {dt.year}"

# --- UI HEADER ---
st.title("🏛️ KPU HSS - MONITORING ABSENSI & KINERJA")
st.write(f"Waktu Sekarang: **{datetime.now().strftime('%H:%M:%S WITA')}**")

# Layout: Dashboard Utama & Panel Kontrol
col_main, col_ctrl = st.columns([2.2, 1])

with col_ctrl:
    st.subheader("📝 Update Pegawai")
    with st.expander("Buka Form Laporan", expanded=True):
        nama = st.selectbox("Pilih Nama Pegawai", list(DATABASE_INFO.keys()))
        tipe = st.radio("Jenis Laporan", ["Datang (Pagi)", "Sore (Lapkin)"])
        
        status_fix = "Hadir"
        hasil_kerja = "-"
        
        if tipe == "Sore (Lapkin)":
            status_fix = st.selectbox("Status Kehadiran", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
            hasil_kerja = st.text_area("Uraian Hasil Kerja/Output")
            
        if st.button("🚀 KIRIM LAPORAN"):
            if tipe == "Sore (Lapkin)" and not hasil_kerja.strip():
                st.warning("Uraian hasil kerja tidak boleh kosong!")
            else:
                info = DATABASE_INFO[nama]
                payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": status_fix, "hasil": hasil_kerja}
                try:
                    r = requests.post(SCRIPT_URL, json=payload)
                    if "Success" in r.text:
                        st.success(f"Berhasil! Data {nama} telah diperbarui di Spreadsheet.")
                        time.sleep(1)
                        st.rerun()
                except:
                    st.error("Gagal mengirim data ke Google Sheets.")

    st.write("---")
    st.subheader("📥 Download Lapkin")
    bulan_sel = st.selectbox("Bulan", LIST_BULAN, index=datetime.now().month-1)
    nama_sel = st.selectbox("Nama Pegawai", list(DATABASE_INFO.keys()), key="lapkin_name")
    
    if st.button("🖨️ GENERATE EXCEL"):
        try:
            raw = requests.get(f"{URL_LAPKIN}&nc={random.random()}").text
            df_raw = pd.read_csv(StringIO(raw))
            df_raw.iloc[:, 0] = pd.to_datetime(df_raw.iloc[:, 0], errors='coerce')
            
            bulan_idx = LIST_BULAN.index(bulan_sel) + 1
            df_f = df_raw[(df_raw.iloc[:, 1] == nama_sel) & (df_raw.iloc[:, 0].dt.month == bulan_idx)].copy()
            df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
            
            if df_f.empty:
                st.error("Data kinerja sore tidak ditemukan untuk filter ini.")
            else:
                info = DATABASE_INFO[nama_sel]
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    header = [
                        ["LAPORAN KERJA HARIAN BULANAN"], ["SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN"], [],
                        ["", "Bulan", f": {bulan_sel}"], ["", "Nama", f": {nama_sel.upper()}"],
                        ["", "NIP", f": {info[0]}"], ["", "Jabatan", f": {info[1]}"],
                        ["", "Unit Kerja", f": {info[2]}"], [],
                        ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja / Output", "Keterangan"]
                    ]
                    body = []
                    for i, (_, row) in enumerate(df_f.iterrows(), 1):
                        body.append([i, format_tgl_indo(row.iloc[0]), f"Melaksanakan tugas sebagai {info[1]}", row.iloc[5], row.iloc[4]])
                    
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                    pd.DataFrame(body).to_excel(writer, startrow=10, index=False, header=False, sheet_name="Lapkin")
                
                st.download_button(label="📁 Download File Excel", data=output.getvalue(), file_name=f"LAPKIN_{nama_sel}_{bulan_sel}.xlsx")
        except:
            st.error("Terjadi masalah saat menarik data database.")

with col_main:
    st.subheader("📊 Dashboard Monitoring Hari Ini")
    tab_pns, tab_pppk = st.tabs(["PNS (ASN)", "PPPK (NON-ASN)"])
    
    def render_absensi(url, master):
        try:
            res = requests.get(f"{url}&nc={random.random()}", timeout=10)
            df = pd.read_csv(StringIO(res.text))
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
            
            final_data = []
            for i, p in enumerate(master, 1):
                d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
                final_data.append({"No": i, "Nama": p, "M": d['m'], "P": d['p'], "Status": d['k']})
            
            st.table(pd.DataFrame(final_data))
        except:
            st.error("Gagal terhubung ke Database Google Sheets. Cek Publish CSV-nya.")

    with tab_pns:
        render_absensi(URL_PNS, MASTER_PNS)
    with tab_pppk:
        render_absensi(URL_PPPK, MASTER_PPPK)

if st.button("🔄 Segarkan Data Dashboard"):
    st.rerun()
