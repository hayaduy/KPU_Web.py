import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
from io import BytesIO
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. KONFIGURASI URL ---
URL_API_PNS = "https://script.google.com/macros/s/AKfycbyWJbg_KceQroTV51pFuM30Ij-K4VwynhjK9NI2R-VBYrLJEA1rh7prec4MvNiKBUJV/exec"
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbwWKNLcFa06rxdCSbr1Ex-6dTUzjxJndEfF_bnBZx0oPOevtXqB6H3nUttupzE2D9yn/exec"
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbxhhNvz5thj5PjA5W19Te02c2E3zueN-QEfNf9nF5El0rfToXK9A8qjNZVpiqnqLyLD/exec"

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# --- 2. FUNGSI AMBIL DATA LAPKIN ---
def get_lapkin_data(nama_user, bulan_nama, tahun):
    try:
        response = requests.get(f"{URL_API_LAPKIN}?v={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            data_json = response.json()
            bulan_angka = LIST_BULAN.index(bulan_nama) + 1
            filtered_data = []
            target_clean = str(nama_user).strip().lower().replace(",", "").replace(".", "")

            for item in data_json:
                val_nama = str(item.get('nama', '')).strip().lower().replace(",", "").replace(".", "")
                if val_nama == target_clean:
                    val_tgl = str(item.get('tanggal', ''))
                    dt_obj = None
                    for fmt in ["%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d"]:
                        try:
                            clean_tgl = val_tgl.split(' ')[0] if ' ' in val_tgl else val_tgl
                            dt_obj = datetime.strptime(clean_tgl, fmt)
                            break
                        except: continue
                    
                    if dt_obj and dt_obj.month == bulan_angka and dt_obj.year == tahun:
                        # Mengambil data 'uraian' dari JSON (Hasil Kerja)
                        hasil_kerja = item.get('uraian', '-')
                        filtered_data.append({
                            "tgl": dt_obj.day,
                            "hari_tgl": dt_obj.strftime("%d/%m/%Y"),
                            "hasil": hasil_kerja
                        })
            return sorted(filtered_data, key=lambda x: x['tgl'])
    except: return []
    return []

# --- 3. GENERATOR EXCEL (SESUAI GAMBAR) ---
def create_excel_file(user_nama, bulan_nama, tahun, ttd_nama):
    output = BytesIO()
    info_user = DATABASE_INFO[user_nama]
    info_ttd = DATABASE_INFO[ttd_nama]
    data_lapkin = get_lapkin_data(user_nama, bulan_nama, tahun)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Laporan')
        
        # Formats
        f_h = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 12})
        f_b = workbook.add_format({'bold': True})
        f_border = workbook.add_format({'border': 1, 'text_wrap': True, 'valign': 'top'})
        f_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'top'})
        f_table_h = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9D9D9'})
        
        # Header Laporan
        worksheet.merge_range('A1:E1', 'LAPORAN BULANAN', f_h)
        worksheet.merge_range('A2:E2', 'SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN', f_h)
        
        worksheet.write('A4', 'Bulan', f_b); worksheet.write('B4', f': {bulan_nama}')
        worksheet.write('A5', 'Nama', f_b); worksheet.write('B5', f': {user_nama}')
        worksheet.write('A6', 'Jabatan', f_b); worksheet.write('B6', f': {info_user[1]}')
        worksheet.write('A7', 'Unit Kerja', f_b); worksheet.write('B7', f': {info_user[2]}')
        worksheet.write('A8', 'Sub Bagian', f_b); worksheet.write('B8', f': {info_user[3]}')
        
        worksheet.write('A10', 'Hasil Kinerja', f_b); worksheet.write('B10', ':')
        
        # Table Headers (Baris 11)
        headers = ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja / Output", "Keterangan"]
        for i, h in enumerate(headers):
            worksheet.write(10, i, h, f_table_h)
        
        # Isi Data
        row = 11
        if not data_lapkin:
            worksheet.merge_range(row, 0, row, 4, "Data Tidak Ditemukan", f_center)
            row += 1
        else:
            for i, d in enumerate(data_lapkin):
                worksheet.write(row, 0, i + 1, f_center)
                worksheet.write(row, 1, d['hari_tgl'], f_center)
                worksheet.write(row, 2, "", f_border)           # Kolom Uraian KOSONG
                worksheet.write(row, 3, d['hasil'], f_border)   # Kolom Hasil Kerja ISI
                worksheet.write(row, 4, "Hadir", f_center)
                row += 1
        
        # Footer / Tanda Tangan
        row_ttd = row + 2
        last_day = calendar.monthrange(tahun, LIST_BULAN.index(bulan_nama)+1)[1]
        
        worksheet.write(row_ttd, 3, f"Kandangan, {last_day} {bulan_nama} {tahun}")
        worksheet.write(row_ttd+1, 3, "Atasan Langsung,")
        worksheet.write(row_ttd+5, 3, ttd_nama, f_b)
        worksheet.write(row_ttd+6, 3, f"NIP. {info_ttd[0]}")
        
        # Lebar Kolom
        worksheet.set_column('A:A', 4)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('C:D', 35)
        
    return output.getvalue()

# --- 4. LOGIKA PENANDATANGAN ---
def get_approver_options(user_nama):
    info = DATABASE_INFO[user_nama]
    jabatan = info[1]
    atasan_list = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE"]
    idx = 0
    if any(x in jabatan for x in ["Teknis", "Pemilu"]): idx = 1
    elif any(x in jabatan for x in ["Keuangan", "Umum", "Logistik"]): idx = 2
    elif any(x in jabatan for x in ["Hukum", "SDM"]): idx = 3
    elif any(x in jabatan for x in ["Perencanaan", "Data"]): idx = 4
    return atasan_list, idx

# --- 5. UI COMPONENTS ---
def inject_custom_css():
    st.markdown("""<style>[data-testid="stMetricValue"] { font-size: 24px; } .stButton button { border-radius: 8px; }</style>""", unsafe_allow_html=True)

@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    tab_abs, tab_lap, tab_dl = st.tabs(["🚀 ABSEN", "📝 LAPKIN", "📥 DOWNLOAD"])
    
    with tab_abs:
        if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
            target_url = URL_API_PNS if info[4] == "PNS" else URL_API_PPPK
            payload = {"nama": user['nama'], "nip": info[0], "jabatan": info[1], "status": info[4]}
            try:
                res = requests.post(target_url, json=payload, timeout=10)
                st.success("Presensi Berhasil!") if "Success" in res.text else st.error(res.text)
            except: st.error("Gagal terhubung")

    with tab_lap:
        stat = st.selectbox("Status Kehadiran:", ["HADIR", "IZIN", "TL", "CUTI"])
        hasil = st.text_input("Hasil Kerja / Output Hari Ini:") 
        if st.button("KIRIM DATA LAPKIN", use_container_width=True):
            if hasil:
                payload = {"nama": user['nama'], "nip": info[0], "jabatan": info[1], "status": stat, "uraian": hasil}
                try:
                    requests.post(URL_API_LAPKIN, json=payload, timeout=10)
                    st.success("Lapkin Terkirim!")
                except: st.error("Gagal mengirim")
            else: st.warning("Mohon isi hasil kerja!")

    with tab_dl:
        bln = st.selectbox("Pilih Bulan:", LIST_BULAN, index=datetime.now().month-1)
        thn = st.selectbox("Tahun:", [2025, 2026], index=1)
        list_atasan, def_idx = get_approver_options(user['nama'])
        ttd_pilih = st.selectbox("Penandatangan:", list_atasan, index=def_idx)
        
        if st.button("🔍 PROSES EXCEL", use_container_width=True):
            with st.spinner("Mengambil data..."):
                excel_data = create_excel_file(user['nama'], bln, thn, ttd_pilih)
                st.download_button("📥 DOWNLOAD FILE SEKARANG", excel_data, f"LAPKIN_{user['nama']}_{bln}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# --- 6. DASHBOARD VIEWS ---
def show_pegawai(user):
    inject_custom_css()
    st.subheader(f"Halo, {user['nama']} 👋")
    c1, c2 = st.columns(2)
    if c1.button("🚀 ABSEN / HADIR", use_container_width=True, type="primary"): pop_menu_mandiri(user)
    if c2.button("📝 ISI LAPKIN", use_container_width=True): pop_menu_mandiri(user)
    st.divider()
    data_log = process_attendance([URL_PNS, URL_PPPK], [user['nama']], datetime.now())
    render_monitoring_list([user['nama']], data_log)

def show_admin(user, database):
    inject_custom_css()
    st.subheader("🏛️ Administrator Panel")
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True): pop_menu_mandiri(user)
    tab1, tab2 = st.tabs(["🔍 MONITORING", "👥 KELOLA USER"])
    with tab1:
        tgl = st.date_input("Pilih Tanggal Monitoring:", datetime.now())
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list(list(database.keys()), data_log)
    with tab2:
        st.dataframe(pd.DataFrame([{"Nama": k, "NIP": v[0], "Jabatan": v[1], "Role": v[3]} for k, v in database.items()]), use_container_width=True)

def show_bendahara(user):
    inject_custom_css()
    st.subheader("💰 Menu Bendahara")
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True): pop_menu_mandiri(user)
    tgl = st.date_input("Rekap Kehadiran Tanggal:", datetime.now())
    data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl)
    render_monitoring_list(list(DATABASE_INFO.keys()), data_log)

def render_monitoring_list(list_nama, data_log):
    for p in sorted(list_nama):
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid {color};">
            <small style="color:#888;">{p}</small><br>
            <div style="display:flex; justify-content:space-between;">
                <span><b>{d['m']} - {d['p']}</b></span>
                <span style="color:{color}; font-weight:bold;">{d['k']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
