import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import calendar
import re

# --- KONFIGURASI URL ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

def clean_name_for_match(name):
    """Menghapus gelar dan karakter khusus agar pencarian akurat"""
    if not name: return ""
    n = str(name).lower()
    # 1. Hapus gelar setelah koma (contoh: , SH., MH.)
    n = re.sub(r'\,.*', '', n) 
    # 2. Hapus gelar depan dan belakang yang umum
    # PERBAIKAN: Kata 'dalam' diganti menjadi 'in'
    for g in ['h.', 'hj.', 'sh', 'mh', 'se', 's.sos', 'st', 'mm', 'spd', 's.kom', 's.ap']:
        n = n.replace(g, "")
    # 3. Hapus spasi dan titik sisa
    return "".join(n.split()).replace(".", "")

# --- 1. LOGIKA ABSENSI ---
def process_attendance(urls, daftar_nama, tgl_pilihan):
    attendance_results = {nama: {"m": "--:--", "p": "--:--", "k": "ALPA"} for nama in daftar_nama}
    str_tgl_target = tgl_pilihan.strftime("%d/%m/%Y")
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                if not df.empty:
                    for _, row in df.iterrows():
                        ts = str(row.iloc[0])
                        if str_tgl_target in ts:
                            nama_sheet = row.iloc[1]
                            for nama_db in daftar_nama:
                                if clean_name_for_match(nama_sheet) == clean_name_for_match(nama_db):
                                    try: jam = ts.split(" ")[1][:5]
                                    except: jam = "--:--"
                                    if attendance_results[nama_db]["m"] == "--:--":
                                        attendance_results[nama_db]["m"] = jam
                                        attendance_results[nama_db]["k"] = "HADIR"
                                    attendance_results[nama_db]["p"] = jam
        except: continue
    return attendance_results

# --- 2. LOGIKA AMBIL DATA LAPKIN ---
def get_lapkin_data(URL_API_LAPKIN, LIST_BULAN, nama_user, bulan_nama, tahun):
    try:
        response = requests.get(f"{URL_API_LAPKIN}?v={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            data_json = response.json()
            bulan_angka = LIST_BULAN.index(bulan_nama) + 1
            filtered_data = []
            target_clean = clean_name_for_match(nama_user)

            for item in data_json:
                val_nama = clean_name_for_match(item.get('nama', ''))
                if val_nama == target_clean:
                    val_tgl = str(item.get('tanggal', ''))
                    dt_obj = None
                    for fmt in ["%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d"]:
                        try:
                            clean_tgl = val_tgl.split(' ')[0]
                            dt_obj = datetime.strptime(clean_tgl, fmt)
                            break
                        except: continue
                    
                    if dt_obj and dt_obj.month == bulan_angka and dt_obj.year == tahun:
                        filtered_data.append({
                            "tgl": dt_obj.day,
                            "hari_tgl": dt_obj.strftime("%d/%m/%Y"),
                            "hasil": item.get('uraian', '-')
                        })
            return sorted(filtered_data, key=lambda x: x['tgl'])
    except: return []
    return []

# --- 3. LOGIKA GENERATOR EXCEL ---
def create_excel_file(DATABASE_INFO, LIST_BULAN, user_nama, bulan_nama, tahun, ttd_pilih, data_lapkin):
    output = BytesIO()
    if user_nama not in DATABASE_INFO: return None
        
    info = DATABASE_INFO[user_nama]
    
    atasan_nama = ttd_pilih
    if atasan_nama == "Suwanto, SH., MH.": 
        j_atasan = "Sekretaris KPU Kab. Hulu Sungai Selatan"
    else:
        info_atasan = DATABASE_INFO.get(atasan_nama, ["-", "Kepala Sub Bagian"])
        j_raw = info_atasan[1]
        j_atasan = j_raw
        if any(x in j_raw for x in ["Kasubbag", "TP-Hupmas", "Teknis"]):
            if "TP-Hupmas" in j_raw or "Teknis" in j_raw: j_atasan = "Kepala Sub Bagian Teknis Penyelenggaraan Pemilu,\nPartisipasi dan Hubungan Masyarakat"
            elif "Keuangan" in j_raw: j_atasan = "Kepala Sub Bagian Keuangan,\nUmum dan Logistik"
            elif "Hukum" in j_raw: j_atasan = "Kepala Sub Bagian Hukum dan\nSumber Daya Manusia"
            elif "Perencanaan" in j_raw: j_atasan = "Kepala Sub Bagian Perencanaan,\nData dan Informasi"

    hr_t = calendar.monthrange(tahun, LIST_BULAN.index(bulan_nama)+1)[1]
    tgl_ttd = f"{hr_t} {bulan_nama} {tahun}"

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Laporan')
        
        f_h = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 12})
        f_b = workbook.add_format({'bold': True})
        f_border = workbook.add_format({'border': 1, 'text_wrap': True, 'valign': 'top'})
        f_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'top'})
        f_table_h = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'bg_color': '#D9D9D9'})
        
        worksheet.merge_range('A1:E1', 'LAPORAN BULANAN', f_h)
        worksheet.merge_range('A2:E2', 'SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN', f_h)
        
        worksheet.write('A4', 'Bulan', f_b); worksheet.write('B4', f': {bulan_nama}')
        worksheet.write('A5', 'Nama', f_b); worksheet.write('B5', f': {user_nama}')
        
        # Penulisan profil dengan indeks info yang benar
        worksheet.write('A6', 'Jabatan', f_b);    worksheet.write('B6', f': {info[1]}')
        worksheet.write('A7', 'Unit Kerja', f_b); worksheet.write('B7', f': {info[2]}')
        worksheet.write('A8', 'Sub Bagian', f_b); worksheet.write('B8', f': {info[3]}')
        
        headers = ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja / Output", "Keterangan"]
        for i, h in enumerate(headers): 
            worksheet.write(10, i, h, f_table_h)
        
        row = 11
        if not data_lapkin:
            worksheet.merge_range(row, 0, row, 4, "Data Tidak Ditemukan", f_center)
            row += 1
        else:
            for i, d in enumerate(data_lapkin):
                worksheet.write(row, 0, i + 1, f_center)
                worksheet.write(row, 1, d['hari_tgl'], f_center)
                worksheet.write(row, 2, "", f_border)
                worksheet.write(row, 3, d['hasil'], f_border)
                worksheet.write(row, 4, "Hadir", f_center)
                row += 1
            
        row_f = row + 2
        worksheet.write(row_f, 3, f"Kandangan, {tgl_ttd}")
        worksheet.write(row_f+1, 3, "Atasan Langsung,")
        worksheet.write(row_f+4, 3, j_atasan, workbook.add_format({'text_wrap': True}))
        worksheet.write(row_f+8, 3, atasan_nama, f_b)
        
        # Ambil NIP atasan
        info_atasan_final = DATABASE_INFO.get(atasan_nama, ["-"])
        worksheet.write(row_f+9, 3, f"NIP. {info_atasan_final[0]}")
        
        worksheet.set_column('A:A', 4)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('C:D', 40)
        worksheet.set_column('E:E', 12)

    return output.getvalue()
