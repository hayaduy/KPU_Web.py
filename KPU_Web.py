import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import random
import time

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub Web", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; }
    .header-box { text-align: center; padding: 10px; color: #F59E0B; font-size: 38px; font-weight: bold; margin-bottom: 20px; }
    .employee-card {
        background-color: #1E293B;
        padding: 12px 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        margin-bottom: 2px;
        border: 1px solid #334155;
    }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 15px; }
    .emp-time { flex: 1.5; color: #94A3B8; text-align: center; font-size: 14px; }
    .emp-status { flex: 1.5; text-align: right; font-weight: bold; font-size: 14px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    /* Menghilangkan padding sidebar agar bersih */
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
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

# --- 3. DIALOGS (POP-UPS) ---

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
        if tipe == "Sore (Laporan Kerja)" and not h_kerja.strip():
            st.error("Uraian kerja wajib diisi!")
        else:
            info = DATABASE_INFO[nama]
            payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja}
            with st.spinner("Mengirim..."):
                res = requests.post(SCRIPT_URL, json=payload)
                if "Success" in res.text:
                    st.success("Berhasil!")
                    time.sleep(1)
                    st.rerun()

@st.dialog("Cetak Lapkin Bulanan")
def pop_cetak():
    st.write("Silakan pilih periode dan pegawai")
    c_b = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now().month-1)
    c_n = st.selectbox("Pilih Pegawai:", list(DATABASE_INFO.keys()))
    
    if st.button("📊 GENERATE EXCEL"):
        try:
            raw = requests.get(f"{URL_LAPKIN}&nc={random.random()}").text
            df_l = pd.read_csv(StringIO(raw))
            df_l.iloc[:, 0] = pd.to_datetime(df_l.iloc[:, 0], dayfirst=True, errors='coerce')
            bulan_idx = LIST_BULAN.index(c_b) + 1
            df_f = df_l[(df_l.iloc[:, 1] == c_n) & (df_l.iloc[:, 0].dt.month == bulan_idx)].copy()
            df_f = df_f[df_f.iloc[:, 5].notna() & (df_f.iloc[:, 5] != "-")]
            
            if df_f.empty:
                st.warning("Data tidak ditemukan.")
            else:
                info = DATABASE_INFO[c_n]
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    header = [
                        ["LAPORAN KERJA HARIAN BULANAN"], ["SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN"], [],
                        ["", "Bulan", f": {c_b}"], ["", "Nama", f": {c_n.upper()}"],
                        ["", "NIP", f": {info[0]}"], ["", "Jabatan", f": {info[1]}"], [],
                        ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja", "Keterangan"]
                    ]
                    body = []
                    for i, (_, row) in enumerate(df_f.iterrows(), 1):
                        body.append([i, row.iloc[0].strftime('%d %B %Y'), f"Tugas {info[1]}", row.iloc[5], row.iloc[4]])
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Lapkin")
                    pd.DataFrame(body).to_excel(writer, startrow=9, index=False, header=False, sheet_name="Lapkin")
                
                st.download_button(label="📥 DOWNLOAD SEKARANG", data=output.getvalue(), file_name=f"LAPKIN_{c_n}_{c_b}.xlsx")
        except:
            st.error("Gagal menarik data.")

# --- 4. MAIN UI ---
st.markdown(f'<div class="header-box">🏛️ MONITORING KPU HSS<br><span style="font-size:20px; color:white;">{datetime.now().strftime("%H:%M:%S WITA")}</span></div>', unsafe_allow_html=True)

# BARIS TOMBOL UTAMA
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🔄 REFRESH DATA"): st.rerun()
with c2:
    st.button("📅 " + datetime.now().strftime("%d %b %Y"))
with c3:
    st.button("📥 REKAP ABSENSI")
with c4:
    # TOMBOL CETAK LAPKIN DI SINI
    if st.button("🖨️ CETAK LAPKIN"):
        pop_cetak()

# --- 5. DASHBOARD PEGAWAI ---
tab_pns, tab_pppk = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])

def render_ui(url, master):
    res = requests.get(f"{url}&nc={random.random()}", timeout=15)
    df = pd.read_csv(StringIO(res.text))
    today_str = datetime.now().strftime('%d/%m/%Y')
    today_alt = datetime.now().strftime('%Y-%m-%d')
    
    log = {}
    df.columns = df.columns.str.strip()
    for _, r in df.iterrows():
        ts = str(r.iloc[0])
        if today_str in ts or today_alt in ts:
            nama = str(r.iloc[1]).strip()
            dt = pd.to_datetime(ts, dayfirst=True, errors='coerce')
            if pd.isna(dt): continue
            if nama not in log:
                log[nama] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
            if dt.hour >= 15: log[nama]["p"] = dt.strftime("%H:%M")

    for i, p in enumerate(master, 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        st_cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        
        st.markdown(f"""
            <div class="employee-card">
                <div class="emp-name">{i}. {p}</div>
                <div class="emp-time">Masuk: <b>{d['m']}</b></div>
                <div class="emp-time">Pulang: <b>{d['p']}</b></div>
                <div class="emp-status {st_cls}">{d['k']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Update ✅", key=f"btn_{p}"):
            pop_update(p)

with tab_pns:
    render_ui(URL_PNS, list(DATABASE_INFO.keys())[:17])
with tab_pppk:
    render_ui(URL_PPPK, list(DATABASE_INFO.keys())[17:])
