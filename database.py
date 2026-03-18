# --- DATABASE PEGAWAI KPU HSS ---
# Password Default: kpuhss2026

DATABASE_INFO = {
    # --- PIMPINAN ---
    "Suwanto, SH., MH.": ["197205212009121001", "Sekretaris", "kpuhss2026", "admin", "PNS"],
    
    # --- SUB BAGIAN PERENCANAAN DATA DAN INFORMASI (RENDATIN) ---
    "Rusma Ariati, SE": ["198406212011012013", "Kepala Sub. Bagian Perencanaan Data dan Informasi", "kpuhss2026", "admin", "PNS"],
    "Zainal Hilmi Yustan": ["198106152009101001", "Pranata Komputer Ahli Pertama", "kpuhss2026", "pegawai", "PNS"],
    "Muhammad Hafiz Rijani, S.KOM": ["199201132020121004", "Pengolah Data Intelijen", "kpuhss2026", "pegawai", "PPPK"],
    "Apriadi Rakhman": ["198904222024211013", "Ahli Pertama-Pranata Komputer", "kpuhss2026", "pegawai", "PPPK"],
    "Alfian Ridhani, S.Kom": ["199511102024061001", "Pengelola Layanan Operasional", "kpuhss2026", "pegawai", "PNS"],

    # --- SUB BAGIAN KEUANGAN, UMUM DAN LOGISTIK (KUL) ---
    "Ineke Setiyaningsih, S.Sos": ["198310032009122001", "Kepala Sub Bagian Keuangan, Umum dan Logistik", "kpuhss2026", "admin", "PNS"],
    "Helmalina": ["196803181990032003", "Penelaah Teknis Kebijakan", "kpuhss2026", "pegawai", "PNS"],
    "Ahmad Erwan Rifani, S.HI": ["198308292008111001", "Penelaah Teknis Kebijakan", "kpuhss2026", "bendahara", "PNS"],
    "Najmi Hidayati": ["198506082007012003", "Penata Kelola Sistem dan Teknologi Informasi", "kpuhss2026", "bendahara", "PNS"],
    "Muhammad Aldi Hudaifi, S.Kom": ["200101212025061007", "Penata Kelola Sistem dan Teknologi Informasi", "kpuhss2026", "pegawai", "PNS"],
    "Firda Aulia, S.Kom.": ["200204152025062007", "Penata Kelola Sistem dan Teknologi Informasi", "kpuhss2026", "pegawai", "PNS"],
    "Sya'bani Rona Baika": ["199202072024212044", "Ahli Pertama-Pranata Komputer", "kpuhss2026", "bendahara", "PPPK"],
    "Basuki Rahmat": ["197705022024211007", "Penata Kelola Pemilihan Umum Ahli Pertama", "kpuhss2026", "bendahara", "PPPK"],
    "Saldoz Yedi": ["198008112025211019", "Operator Layanan Operasional", "kpuhss2026", "pegawai", "PPPK"],
    "Mastoni Ridani": ["199106012025211018", "Operator Layanan Operasional", "kpuhss2026", "pegawai", "PPPK"],
    "Suriadi": ["199803022025211005", "Pengelola Umum Operasional", "kpuhss2026", "pegawai", "PPPK"],
    "Ami Aspihani": ["198204042025211031", "Operator Layanan Operasional", "kpuhss2026", "pegawai", "PPPK"],
    "Emaliani": ["198906222025212027", "Pengadministrasi Perkantoran", "kpuhss2026", "pegawai", "PPPK"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN", "kpuhss2026", "pegawai", "PPPK"],

    # --- SUB BAGIAN TEKNIS PEMILU, PARTISIPASI DAN HUBUNGAN MASYARAKAT ---
    "Wawan Setiawan, SH": ["198606012010121004", "Kepala Sub. Bagian Teknis Pemilu, Partisipasi dan Hubungan Masyarakat", "kpuhss2026", "admin", "PNS"],
    "Suci Lestari, S.Ikom": ["198501082010122006", "Penelaah Teknis Kebijakan", "kpuhss2026", "pegawai", "PNS"],
    "Athaya Insyira Khairani, S.H": ["200107122025062017", "Penyusun Materi Hukum dan Perundang-Undangan", "kpuhss2026", "pegawai", "PNS"],
    "Muhammad Ibnu Fahmi, S.H.": ["200106082025061007", "Penyusun Materi Hukum dan Perundang-Undangan", "kpuhss2026", "pegawai", "PNS"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA", "kpuhss2026", "pegawai", "PPPK"],
    "Sulaiman": ["198411222024211010", "Penata Kelola Pemilihan Umum Ahli Pertama", "kpuhss2026", "pegawai", "PPPK"],

    # --- SUB BAGIAN HUKUM DAN SUMBER DAYA MANUSIA ---
    "Farah Agustina Setiawati, SH": ["198408282010122003", "Kepala Sub. Bagian Hukum dan Sumber Daya Manusia", "kpuhss2026", "admin", "PNS"],
    "Jainal Abidin": ["198207122009101001", "Pengelola layanan operasional", "kpuhss2026", "pegawai", "PNS"],
    "Syaiful Anwar": ["197411272007101001", "Penata Kelola Sistem dan Teknologi Informasi", "kpuhss2026", "bendahara", "PNS"],
    "M Satria Maipadly": ["198905262024211016", "Ahli Pertama-Penata Kelola Pemilu", "kpuhss2026", "pegawai", "PPPK"],
    "Abdurrahman": ["198810122025211031", "Operator Layanan Operasional", "kpuhss2026", "admin", "PPPK"],
}

# --- MASTER LIST ---
MASTER_PNS = [name for name, info in DATABASE_INFO.items() if info[4] == "PNS"]
MASTER_PPPK = [name for name, info in DATABASE_INFO.items() if info[4] == "PPPK"]
