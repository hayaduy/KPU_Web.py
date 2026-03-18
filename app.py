import streamlit as st
from database import DATABASE_INFO, MASTER_PNS, MASTER_PPPK
from core_logic import process_attendance, URL_PNS, URL_PPPK
from dashboards import pop_update

st.set_page_config(page_title="KPU HSS Presence Hub", layout="wide", page_icon="🏛️")
# Tetap WITA
import pytz
from datetime import datetime
wita_tz = pytz.timezone('Asia/Makassar')

# --- STYLE CSS BARU: LEBIH GANTENG & MODERN ---
st.markdown("""
    <style>
    /* 1. Background Total: Gelap Super Elegan */
    .stApp {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
    }
    
    /* 2. Header Box: Gradasi Solid Modern */
    .header-box {
        text-align: center;
        background: linear-gradient(90deg, #1e3a8a 0%, #000000 50%, #7c2d12 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .header-box h1 {
        color: #F59E0B !important; /* Emas KPU */
        font-size: 32px !important;
        font-weight: bold !important;
        margin: 0 !important;
    }
    .clock-box {
        text-align: center;
        color: #cbd5e1;
        font-size: 18px;
        font-family: 'Courier New', monospace;
        margin-top: 5px;
    }

    /* 3. Employee Card: Desain Minimalis & Glassmorphism */
    .employee-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        padding: 15px 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.2s, background 0.2s;
    }
    .employee-card:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateY(-2px);
    }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #94a3b8; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; text-transform: uppercase; }
    
    /* Warna Status */
    .status-hadir { color: #10B981; } /* Hijau Emerald */
    .status-alpa { color: #EF4444; } /* Merah */
    .status-terlambat { color: #F59E0B; } /* Oranye KPU */

    /* 4. Tombol: Premium & Borderless */
    .stButton>button {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        transition: all 0.2s;
        padding: 5px 15px !important;
    }
    .stButton>button:hover {
        background-color: #F59E0B !important;
        border: 1px solid #F59E0B !important;
        color: black !important;
        transform: scale(1.05);
    }
    
    /* 5. Tab System: Modern & Clean */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #F59E0B !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER LAYOUT ---
st.markdown("""
    <div class="header-box">
        <h1>🏛️ MONITORING KPU HSS</h1>
        <div class="clock-box">""" + datetime.now(wita_tz).strftime("%H:%M:%S WITA") + """</div>
    </div>
""", unsafe_allow_html=True)

# (Sisa kode app.py Abang tetap sama, panggil render_list, tabs, dll)
