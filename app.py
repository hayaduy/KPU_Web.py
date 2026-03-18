# app.py
import streamlit as st
from datetime import datetime
import pytz
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK
from dashboards import pop_update

st.set_page_config(page_title="KPU HSS Presence Hub", layout="wide")
wita_tz = pytz.timezone('Asia/Makassar')

# --- CSS NYA DI SINI ---
st.markdown("<style>/* Paste CSS dari kode Abang di sini */</style>", unsafe_allow_html=True)

st.title("🏛️ MONITORING KPU HSS")
pilih_tgl = st.date_input("Pilih Tanggal", value=datetime.now(wita_tz).date())

# TAB SYSTEM
t1, t2, t3 = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])

def render_list(masters, urls, tab_name):
    data_log = process_attendance(urls, masters, pilih_tgl)
    for i, p in enumerate(masters, 1):
        d = data_log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        # Render Card HTML di sini...
        col_main, col_btn = st.columns([8, 2])
        col_main.write(f"{i}. {p} | M: {d['m']} | P: {d['p']} | {d['k']}")
        if col_btn.button("Update", key=f"{tab_name}_{p}"):
            pop_update(p)

with t1: render_list(list(DATABASE_INFO.keys()), [URL_PNS, URL_PPPK], "all")
with t2: render_list(MASTER_PNS, [URL_PNS], "pns")
with t3: render_list(MASTER_PPPK, [URL_PPPK], "pppk")
