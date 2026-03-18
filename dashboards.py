import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import calendar
from io import BytesIO
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK 

# --- 1. KONFIGURASI URL ---
# PASTIKAN URL_API_LAPKIN DI BAWAH INI ADALAH URL "EXEC" HASIL DEPLOY TERBARU
URL_API_PNS = "https://script.google.com/macros/s/AKfycbyWJbg_KceQroTV51pFuM30Ij-K4VwynhjK9NI2R-VBYrLJEA1rh7prec4MvNiKBUJV/exec"
URL_API_PPPK = "https://script.google.com/macros/s/AKfycbwWKNLcFa06rxdCSbr1Ex-6dTUzjxJndEfF_bnBZx0oPOevtXqB6H3nUttupzE2D9yn/exec"
URL_API_LAPKIN = "https://script.google.com/macros/s/AKfycbyXtsnv9OQ1qDkF41iCsqWzcQbqy0YKmrdrzzR4bAno19g3RRWjhpxxeKTDW1c05Irz/exec"

# --- 2. FUNGSI AMBIL DATA LAPKIN ---
def get_lapkin_data(nama_user, bulan_nama, tahun):
    try:
        response = requests.get(URL_API_LAPKIN, timeout=15)
        
        # Cek apakah responnya valid JSON
        if response.status_code == 200:
            try:
                data_json = response.json()
            except:
                st.error("API Lapkin memberikan respon bukan JSON. Pastikan Script sudah di-Deploy sebagai 'Anyone'.")
                return []
            
            list_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            bulan_angka = list_bulan.index(bulan_nama) + 1
            
            filtered_data = []
            for item in data_json:
                # Cari kolom nama secara fleksibel
                val_nama = next((str(v).strip().lower() for k, v in item.items() if 'nama' in k.lower()), "")
                
                if val_nama == str(nama_user).strip().lower():
                    # Cari kolom tanggal/timestamp
                    val_tgl = next((str(v) for k, v in item.items() if 'tanggal' in k.lower() or 'timestamp' in k.lower()), "")
                    
                    dt_obj = None
                    # Parsing tanggal (Coba berbagai format)
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            clean_tgl = val_tgl.split(' ')[0] if ' ' in val_tgl else val_tgl
                            dt_obj = datetime.strptime(clean_tgl, fmt)
                            break
                        except: continue
                    
                    if dt_obj and dt_obj.month == bulan_angka and dt_obj.year == tahun:
                        # Cari kolom Hasil Kerja / Output
                        hasil_kerja = "-"
                        for k, v in item.items():
                            kl = k.lower()
                            if ('hasil' in kl or 'output' in kl or 'kerja' in kl) and str(v).strip().lower() != val_nama:
                                hasil_kerja = str(v)
                                break
                        
                        filtered_data.append({
                            "tgl": dt_obj.day,
                            "hari_tgl": dt_obj.strftime("%d/%m/%Y"),
                            "uraian": f"Melaksanakan tugas: {hasil_kerja}",
                            "output": hasil_kerja
                        })
            
            return sorted(filtered_data, key=lambda x: x['tgl'])
    except Exception as e:
        st.error(f"Gagal koneksi ke server: {e}")
        return []
    return []

# --- 3. FUNGSI GENERATOR EXCEL ---
def create_excel_file(user_nama, bulan_nama, tahun, ttd_nama):
    output = BytesIO()
    info_user = DATABASE_INFO[user_nama]
    info_ttd = DATABASE_INFO[ttd_nama]
    
    data_lapkin = get_lapkin_data(user_nama, bulan_nama, tahun)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Laporan')
        
        f_header = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 12})
        f_bold = workbook.add_format({'bold': True})
        f_border = workbook.add_format({'border': 1, 'text_wrap': True, 'valign': 'top'})
        f_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'top'})
        f_table_h = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9D9D9'})
        
        worksheet.merge_range('A1:E1', 'LAPORAN KINERJA BULANAN', f_header)
        worksheet.merge_range('A2:E2', 'SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN', f_header)
        
        worksheet.write('A4', 'Bulan', f_bold); worksheet.write('B4', f': {bulan_nama} {tahun}')
        worksheet.write('A5', 'Nama', f_bold); worksheet.write('B5', f': {user_nama}')
        worksheet.write('A6', 'Jabatan', f_bold); worksheet.write('B6', f': {info_user[1]}')
        
        headers = ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja / Output", "Keterangan"]
        for i, h in enumerate(headers):
            worksheet.write(9, i, h, f_table_h)
        
        row = 10
        if not data_lapkin:
            worksheet.merge_range(row, 0, row, 4, f"Data {user_nama} tidak ditemukan. Pastikan sudah isi Lapkin di GSheet.", f_center)
            row += 1
        else:
            for i, d in enumerate(data_lapkin):
                worksheet.write(row, 0, i + 1, f_center)
                worksheet.write(row, 1, d['hari_tgl'], f_center)
                worksheet.write(row, 2, d['uraian'], f_border)
                worksheet.write(row, 3, d['output'], f_border)
                worksheet.write(row, 4, "Hadir", f_center)
                row += 1
        
        row_ttd = row + 3
        list_bln = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        bln_idx = list_bln.index(bulan_nama) + 1
        last_day = calendar.monthrange(tahun, bln_idx)[1]
        
        worksheet.write(row_ttd, 3, f"Kandangan, {last_day} {bulan_nama} {tahun}")
        worksheet.write(row_ttd+1, 3, "Atasan Langsung,")
        worksheet.write(row_ttd+5, 3, ttd_nama, f_bold)
        worksheet.write(row_ttd+6, 3, f"NIP. {info_ttd[0]}")
        
        worksheet.set_column('A:A', 4)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:D', 45)
        
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
    if "Sekretaris" in jabatan or "Kepala Sub" in jabatan: idx = 0
    return atasan_list, idx

# --- 5. CSS ---
def inject_custom_css():
    st.markdown("""<style>[data-testid="stMetricValue"] { font-size: 24px; } .stButton button { border-radius: 8px; }</style>""", unsafe_allow_html=True)

# --- 6. POP-UP MENU MANDIRI ---
@st.dialog("📋 AKSES MANDIRI & LAPKIN")
def pop_menu_mandiri(user):
    info = DATABASE_INFO[user['nama']]
    nip, jabatan, status_peg = info[0], info[1], info[4]
    
    tab_abs, tab_lap, tab_dl = st.tabs(["🚀 ABSEN", "📝 LAPKIN", "📥 DOWNLOAD"])
    
    with tab_abs:
        if st.button("KLIK UNTUK ABSEN (HADIR)", use_container_width=True, type="primary"):
            target_url = URL_API_PNS if status_peg == "PNS" else URL_API_PPPK
            payload = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": status_peg}
            with st.spinner("Mengirim..."):
                try:
                    res = requests.post(target_url, json=payload, timeout=10)
                    st.success("Presensi Berhasil!") if "Success" in res.text else st.error(res.text)
                except: st.error("Koneksi Gagal")

    with tab_lap:
        stat = st.selectbox("Status:", ["HADIR", "IZIN", "TL", "CUTI"])
        hasil = st.text_input("Hasil Kerja / Output:") 
        if st.button("KIRIM LAPKIN", use_container_width=True):
            if hasil:
                payload = {"nama": user['nama'], "nip": nip, "jabatan": jabatan, "status": stat, "output": hasil}
                with st.spinner("Mengirim..."):
                    try:
                        requests.post(URL_API_LAPKIN, json=payload, timeout=10)
                        st.success("Berhasil dikirim!")
                    except: st.error("Gagal terhubung.")
            else: st.warning("Isi hasil kerja!")

    with tab_dl:
        bln = st.selectbox("Pilih Bulan Laporan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        thn = st.selectbox("Tahun:", [2025, 2026], index=1)
        list_atasan, def_idx = get_approver_options(user['nama'])
        ttd_pilih = st.selectbox("Pilih Penandatangan:", list_atasan, index=def_idx)
        
        if st.button("🔍 PROSES LAPORAN", use_container_width=True):
            with st.spinner("Menghubungi GSheet Lapkin..."):
                excel_data = create_excel_file(user['nama'], bln, thn, ttd_pilih)
                st.download_button(
                    label="📥 DOWNLOAD FILE EXCEL",
                    data=excel_data,
                    file_name=f"LAPORAN_{user['nama']}_{bln}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )

# --- 7. DASHBOARD LOGIC ---
def show_pegawai(user):
    inject_custom_css()
    st.subheader(f"Halo, {user['nama']} 👋")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 ABSEN / HADIR", use_container_width=True, type="primary"):
            pop_menu_mandiri(user)
    with col2:
        if st.button("📝 ISI LAPKIN", use_container_width=True):
            pop_menu_mandiri(user)
    st.divider()
    tgl_now = datetime.now()
    data_log = process_attendance([URL_PNS, URL_PPPK], [user['nama']], tgl_now)
    render_monitoring_list([user['nama']], data_log)

def show_admin(user, database):
    inject_custom_css()
    st.subheader("🏛️ Administrator Panel")
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True):
        pop_menu_mandiri(user)
    tab_mon, tab_user = st.tabs(["🔍 MONITORING", "👥 KELOLA USER"])
    with tab_mon:
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Pilih Tanggal:", datetime.now())
        search = c2.text_input("Cari Nama:")
        data_log = process_attendance([URL_PNS, URL_PPPK], list(database.keys()), tgl)
        render_monitoring_list([n for n in list(database.keys()) if search.lower() in n.lower()], data_log)
    with tab_user:
        user_list = [{"Nama": k, "NIP": v[0], "Role": v[3].upper(), "Password": v[2]} for k, v in database.items()]
        st.dataframe(pd.DataFrame(user_list), use_container_width=True)

def show_bendahara(user):
    inject_custom_css()
    st.subheader("💰 Menu Bendahara")
    if st.button("📂 MENU MANDIRI SAYA", use_container_width=True):
        pop_menu_mandiri(user)
    st.divider()
    tgl_rekap = st.date_input("Pilih Hari Rekap:", datetime.now())
    data_log = process_attendance([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), tgl_rekap)
    render_monitoring_list(list(DATABASE_INFO.keys()), data_log)

def render_monitoring_list(list_nama, data_log):
    for p in list_nama:
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        color = "#10B981" if d['k'] == "HADIR" else "#EF4444"
        st.markdown(f"""<div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid {color};"><small>{p}</small> <br> <b>{d['m']} - {d['p']}</b> | <span style="color:{color}">{d['k']}</span></div>""", unsafe_allow_html=True)
