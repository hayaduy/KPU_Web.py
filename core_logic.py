import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# URL yang Abang berikan (Format CSV Publik)
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

def process_attendance(urls, daftar_nama, tgl_pilihan):
    """
    Memproses data kehadiran dari Google Sheets (CSV) berdasarkan tanggal pilihan.
    """
    # Inisialisasi hasil: Default ALPA untuk semua pegawai di database
    attendance_results = {nama: {"m": "--:--", "p": "--:--", "k": "ALPA"} for nama in daftar_nama}
    
    # Format tanggal pilihan (dari st.date_input) menjadi string "DD/MM/YYYY"
    str_tgl_target = tgl_pilihan.strftime("%d/%m/%Y")
    
    for url in urls:
        try:
            # Mengambil data CSV
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Membaca string CSV ke DataFrame
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)

                if not df.empty:
                    for _, row in df.iterrows():
                        # Kolom 0: Timestamp (format: 17/03/2026 16:51:54)
                        timestamp_full = str(row.iloc[0])
                        
                        # Cek apakah baris ini sesuai dengan tanggal yang dipilih Admin
                        if str_tgl_target in timestamp_full:
                            nama = row.iloc[1] # Kolom 1: Nama
                            
                            # Ekstraksi jam dan menit (HH:mm)
                            # Mengambil bagian setelah spasi dan memotong detik
                            try:
                                jam_menit = timestamp_full.split(" ")[1][:5]
                            except:
                                jam_menit = "--:--"

                            if nama in attendance_results:
                                # Data pertama yang ditemukan pada hari itu = Jam Masuk
                                if attendance_results[nama]["m"] == "--:--":
                                    attendance_results[nama]["m"] = jam_menit
                                    attendance_results[nama]["k"] = "HADIR"
                                
                                # Data terakhir yang ditemukan pada hari itu = Jam Pulang
                                attendance_results[nama]["p"] = jam_menit
                                
        except Exception as e:
            print(f"Gagal memproses URL {url}: {e}")
            
    return attendance_results
