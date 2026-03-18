# database.py

# Struktur Data: 
# "Nama": ["NIP", "Jabatan", "Unit Kerja", "Sub Bagian", "Status", "Atasan", "NIP Atasan", "ROLE"]

DATABASE_INFO = {
    # --- ADMIN (3 Orang) ---
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. HSS", "-", "PNS", "Ketua KPU Kab. HSS", "-", "Admin"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum & SDM", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Admin"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Admin"],

    # --- BENDAHARA (5 Orang) ---
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Bendahara"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Bendahara"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Bendahara"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Bendahara"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Bendahara"],

    # --- PEGAWAI PNS ---
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Pegawai"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan & Logistik", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Pegawai"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan & Data", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001", "Pegawai"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],

    # --- PEGAWAI PPPK ---
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Teknis", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004", "Pegawai"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI", "Sekretariat KPU Kab. HSS", "Sub Bagian Keuangan", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001", "Pegawai"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Hukum", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003", "Pegawai"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU", "Sekretariat KPU Kab. HSS", "Sub Bagian Perencanaan", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013", "Pegawai"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]
