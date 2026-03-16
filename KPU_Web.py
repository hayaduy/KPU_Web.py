import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
import time

# --- SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v36.0", layout="wide", page_icon="🏛️")

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

# --- APP START ---
st.title("🏛️ KPU HSS - MONITORING HUB")
st.write(f"Waktu: **{datetime.now().strftime('%H:%M:%S WITA')}**")

tab_dash, tab_input, tab_cetak = st.tabs(["📊 DASHBOARD", "📝 INPUT", "🖨️ CETAK"])

with tab_dash:
    col1, col2 = st.columns(2)

    def render_safe(url, master, title):
        st.write(f"### {title}")
        try:
            res = requests.get(f"{url}&nc={random.random()}", timeout=15)
            df = pd.read_csv(StringIO(res.text))
            df.columns = df.columns.str.strip()
            
            # --- LOGIKA BARU: FILTER TANPA .DT (ANTI-ERROR) ---
            today_str = datetime.now().strftime('%d/%m/%Y') # Format umum Google Sheets
            today_str_alt = datetime.now().strftime('%Y-%m-%d') # Format alternatif
            
            log = {}
            for _, r in df.iterrows():
                row_raw_time = str(r.iloc[0])
                # Cek apakah baris ini terjadi hari ini
                if today_str in row_raw_time or today_str_alt in row_raw_time:
                    nama = str(r.iloc[1]).strip()
                    try:
                        # Parsing waktu secara manual dari string timestamp
                        # Contoh: "17/03/2026 08:30:00" -> ambil "08:30"
                        full_dt = pd.to_datetime(row_raw_time, dayfirst=True, errors='coerce')
                        if pd.isinstance(full_dt, pd.NaT): continue
                        
                        jam_val = full_dt.hour
                        jam_str = full_dt.strftime("%H:%M")
                        
                        if nama not in log:
                            log[nama] = {"m": jam_str, "p": "--:--", "k": "HADIR" if jam_val < 9 else "TERLAMBAT"}
                        if jam_val >= 15:
                            log[nama]["p"] = jam_str
                    except:
                        continue
            
            rows = []
            for i, p in enumerate(master, 1):
                d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
                rows.append({"No": i, "Nama Pegawai": p, "M": d['m'], "P": d['p'], "Status": d['k']})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Gagal memuat {title}. Pastikan link CSV benar.")

    with col1: render_safe(URL_PNS, MASTER_PNS, "PNS")
    with col2: render_safe(URL_PPPK, MASTER_PPPK, "PPPK")

with tab_input:
    st.subheader("Update Laporan Kehadiran")
    with st.form("in_form"):
        n = st.selectbox("Nama", list(DATABASE_INFO.keys()))
        t = st.radio("Tipe", ["Pagi", "Sore"])
        s = "Hadir"
        h = "-"
        if t == "Sore":
            s = st.selectbox("Status", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
            h = st.text_area("Hasil Kerja")
        
        if st.form_submit_button("KIRIM"):
            info = DATABASE_INFO[n]
            payload = {"nama": n, "nip": info[0], "jabatan": info[1], "status": s, "hasil": h}
            try:
                requests.post(SCRIPT_URL, json=payload, timeout=10)
                st.success(f"Update {n} Berhasil!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("Gagal terhubung ke skrip.")

with tab_cetak:
    st.subheader("Cetak Excel Lapkin")
    c_b = st.selectbox("Bulan", LIST_BULAN, index=datetime.now().month-1)
    c_n = st.selectbox("Pegawai", list(DATABASE_INFO.keys()), key="cetak_n")
    
    if st.button("Generate"):
        try:
            res = requests.get(f"{URL_LAPKIN}&nc={random.random()}")
            df_l = pd.read_csv(StringIO(res.text))
            # Konversi tanggal khusus untuk cetak (paksa)
            df_l.iloc[:, 0] = pd.to_datetime(df_l.iloc[:, 0], dayfirst=True, errors='coerce')
            df_l = df_l.dropna(subset=[df_l.columns[0]])
            
            idx = LIST_BULAN.index(c_b) + 1
            df_f = df_l[(df_l.iloc[:, 1] == c_n) & (df_l.iloc[:, 0].dt.month == idx)].copy()
            df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
            
            if not df_f.empty:
                info = DATABASE_INFO[c_n]
                out = BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as writer:
                    header = [["LAPORAN KERJA"], ["KPU KABUPATEN HSS"], [], ["Nama", c_n], ["Jabatan", info[1]], [], ["No", "Tanggal", "Kegiatan", "Output", "Ket"]]
                    body = [[i+1, r.iloc[0].strftime('%d %B %Y'), f"Tugas {info[1]}", r.iloc[5], r.iloc[4]] for i, (_, r) in enumerate(df_f.iterrows())]
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                    pd.DataFrame(body).to_excel(writer, startrow=8, index=False, header=False, sheet_name="Lapkin")
                st.download_button("📥 Download", out.getvalue(), f"LAPKIN_{c_n}.xlsx")
            else:
                st.warning("Data tidak ditemukan.")
        except:
            st.error("Database Lapkin tidak terbaca.")

if st.button("🔄 REFRESH"):
    st.rerun()
