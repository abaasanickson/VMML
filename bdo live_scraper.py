import time
import random
import pandas as pd
import requests
import streamlit as st
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="VMML BDO BUSINESS GENERATOR",
    # page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    div[data-testid="stMetric"] div {
        color: #38bdf8 !important;
        font-weight: 600;
    }
    .stButton > button {
        background: linear-gradient(180deg, #808080, #4c5055);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    .stDownloadButton > button {
        background: linear-gradient(180deg, #021024, #052659);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .welcome-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .welcome-title {
        font-size: 1.6rem;38bdf8
        font-weight: 700;
        color: #291C0E;
        margin-bottom: 6px;
    }
    .welcome-subtitle {
        color: #6E473B;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .quote {
        font-style: italic;
        color: #A78D78;
        border-left: 4px solid #3b82f6;
        padding-left: 16px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== LOAD API KEY FROM SECRETS ======================
try:
    api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
except:
    st.error("API key not configured. Please contact the administrator.")
    st.stop()

# ====================== QUOTES & WELCOME ======================
import streamlit as st


@st.cache_data(ttl=60)
def get_live_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=3)
        if response.status_code == 200:
            data = response.json()
            quote_text = data[0]['q']
            author = data[0]['a']
            return f'"{quote_text}" — {author}'
    except Exception as e:
        pass

    return '"Dream big. Start small. Act now."'


quote = get_live_quote()

from datetime import datetime, timezone, timedelta


def get_greeting():
    # Define EAT (East Africa Time) which is UTC+3
    eat_timezone = timezone(timedelta(hours=3))
    hour = datetime.now(eat_timezone).hour

    if 5 <= hour < 12:
        return "Good morning Alison"
    elif 12 <= hour < 17:
        return "Good afternoon Alison"
    elif 17 <= hour < 22:
        return "Good evening Alison"
    else:
        return "Hello Alison"


quote = get_live_quote()
greeting = get_greeting()

st.markdown(f"""
<div class="welcome-card">
    <div class="welcome-title">{greeting}  Ready to generate leads?</div>
    <div class="welcome-subtitle">Full coverage across Kampala, Wakiso & Mukono</div>
    <div class="quote">“{quote}”</div>
</div>
""", unsafe_allow_html=True)

st.title("Full Region Business Lead Generator")
st.caption("Grid-based Nearby Search • Complete regional coverage • Deduplicated results")

# ====================== SIDEBAR ======================
st.sidebar.markdown("### ⚙️ Search Settings")

region = st.sidebar.selectbox(
    "Select Region",
    ["Kampala", "Wakiso", "Mukono", "Western Uganda", "Masaka", "Jinja"]
)

search_query = st.sidebar.text_input(
    "Business Type / Keyword",
    value="Hardware",
    help="e.g. School, Hardware, Pharmacy, Supermarket, Clinic"
)

radius = st.sidebar.slider(
    "Search Radius per point (meters)",
    min_value=2000,
    max_value=8000,
    value=5000,
    step=500
)
#place_type = st.sidebar.selectbox(
    #"Google Place Type (optional)",
    #options=["", "bank", "finance", "school", "hospital", "pharmacy", "supermarket", "store", "restaurant"],
   # help="Leave empty for general keyword search. Use specific type for better results on banks, schools, etc."
#)

st.sidebar.markdown("---")
st.sidebar.info("Larger radius = better coverage but more duplicates (auto-removed)")

# ====================== REGION GRIDS ======================
REGION_GRIDS = {
    "Kampala": [
        # ========== CENTRAL DIVISION (CBD + Kololo + Nakasero + Old Kampala) ==========
        (0.30, 32.56), (0.30, 32.57), (0.30, 32.58), (0.30, 32.59), (0.30, 32.60),
        (0.31, 32.56), (0.31, 32.57), (0.31, 32.58), (0.31, 32.59), (0.31, 32.60),
        (0.32, 32.56), (0.32, 32.57), (0.32, 32.58), (0.32, 32.59), (0.32, 32.60),
        (0.33, 32.56), (0.33, 32.57), (0.33, 32.58), (0.33, 32.59), (0.33, 32.60),
        (0.34, 32.56), (0.34, 32.57), (0.34, 32.58), (0.34, 32.59), (0.34, 32.60),

        # ========== KAWEMPE DIVISION (North) ==========
        (0.34, 32.54), (0.34, 32.55),
        (0.35, 32.54), (0.35, 32.55), (0.35, 32.56), (0.35, 32.57),
        (0.36, 32.54), (0.36, 32.55), (0.36, 32.56), (0.36, 32.57),
        (0.37, 32.54), (0.37, 32.55), (0.37, 32.56), (0.37, 32.57),
        (0.38, 32.54), (0.38, 32.55), (0.38, 32.56), (0.38, 32.57),
        (0.39, 32.54), (0.39, 32.55), (0.39, 32.56),
        (0.40, 32.54), (0.40, 32.55),

        # ========== NAKAWA DIVISION (East) ==========
        (0.31, 32.61), (0.31, 32.62), (0.31, 32.63), (0.31, 32.64),
        (0.32, 32.61), (0.32, 32.62), (0.32, 32.63), (0.32, 32.64),
        (0.33, 32.61), (0.33, 32.62), (0.33, 32.63), (0.33, 32.64),
        (0.34, 32.61), (0.34, 32.62), (0.34, 32.63), (0.34, 32.64),
        (0.35, 32.61), (0.35, 32.62), (0.35, 32.63), (0.35, 32.64),
        (0.36, 32.61), (0.36, 32.62), (0.36, 32.63),
        (0.30, 32.61), (0.30, 32.62), (0.30, 32.63),

        # ========== LUBAGA / RUBAGA DIVISION (West) ==========
        (0.29, 32.52), (0.29, 32.53), (0.29, 32.54), (0.29, 32.55),
        (0.30, 32.52), (0.30, 32.53), (0.30, 32.54), (0.30, 32.55),
        (0.31, 32.52), (0.31, 32.53), (0.31, 32.54), (0.31, 32.55),
        (0.32, 32.52), (0.32, 32.53), (0.32, 32.54), (0.32, 32.55),
        (0.33, 32.52), (0.33, 32.53), (0.33, 32.54),
        (0.28, 32.53), (0.28, 32.54), (0.28, 32.55),

        # ========== MAKINDYE DIVISION (South) ==========
        (0.26, 32.55), (0.26, 32.56), (0.26, 32.57), (0.26, 32.58), (0.26, 32.59),
        (0.27, 32.55), (0.27, 32.56), (0.27, 32.57), (0.27, 32.58), (0.27, 32.59),
        (0.28, 32.56), (0.28, 32.57), (0.28, 32.58), (0.28, 32.59),
        (0.29, 32.56), (0.29, 32.57), (0.29, 32.58), (0.29, 32.59),
        (0.25, 32.56), (0.25, 32.57), (0.25, 32.58),
        (0.24, 32.57), (0.24, 32.58),

        # ========== EXTRA IMPORTANT AREAS ==========
        # Ntinda / Naguru / Bukoto
        (0.34, 32.60), (0.35, 32.60), (0.36, 32.60),
        # Wandegeya / Makerere
        (0.33, 32.55), (0.34, 32.55),
        # Nsambya / Kibuli
        (0.30, 32.59), (0.29, 32.59),
        # Bwaise / Kawaala side
        (0.35, 32.53), (0.36, 32.53),
        # Industrial Area / Luzira direction
        (0.31, 32.65), (0.32, 32.65),
        # Najjanankumbi / Ndeeba
        (0.28, 32.55), (0.29, 32.54),
    ],
    "Wakiso": [
        # Generated systematic grid covering Wakiso District
        # Latitude from -0.05 to 0.55, Longitude from 32.25 to 32.75, step 0.03

        (-0.05, 32.25), (-0.05, 32.28), (-0.05, 32.31), (-0.05, 32.34), (-0.05, 32.37),
        (-0.05, 32.40), (-0.05, 32.43), (-0.05, 32.46), (-0.05, 32.49), (-0.05, 32.52),
        (-0.05, 32.55), (-0.05, 32.58), (-0.05, 32.61), (-0.05, 32.64), (-0.05, 32.67),
        (-0.05, 32.70), (-0.05, 32.73),

        (-0.02, 32.25), (-0.02, 32.28), (-0.02, 32.31), (-0.02, 32.34), (-0.02, 32.37),
        (-0.02, 32.40), (-0.02, 32.43), (-0.02, 32.46), (-0.02, 32.49), (-0.02, 32.52),
        (-0.02, 32.55), (-0.02, 32.58), (-0.02, 32.61), (-0.02, 32.64), (-0.02, 32.67),
        (-0.02, 32.70), (-0.02, 32.73),

        (0.01, 32.25), (0.01, 32.28), (0.01, 32.31), (0.01, 32.34), (0.01, 32.37),
        (0.01, 32.40), (0.01, 32.43), (0.01, 32.46), (0.01, 32.49), (0.01, 32.52),
        (0.01, 32.55), (0.01, 32.58), (0.01, 32.61), (0.01, 32.64), (0.01, 32.67),
        (0.01, 32.70), (0.01, 32.73),

        (0.04, 32.25), (0.04, 32.28), (0.04, 32.31), (0.04, 32.34), (0.04, 32.37),
        (0.04, 32.40), (0.04, 32.43), (0.04, 32.46), (0.04, 32.49), (0.04, 32.52),
        (0.04, 32.55), (0.04, 32.58), (0.04, 32.61), (0.04, 32.64), (0.04, 32.67),
        (0.04, 32.70), (0.04, 32.73),

        (0.07, 32.25), (0.07, 32.28), (0.07, 32.31), (0.07, 32.34), (0.07, 32.37),
        (0.07, 32.40), (0.07, 32.43), (0.07, 32.46), (0.07, 32.49), (0.07, 32.52),
        (0.07, 32.55), (0.07, 32.58), (0.07, 32.61), (0.07, 32.64), (0.07, 32.67),
        (0.07, 32.70), (0.07, 32.73),

        (0.10, 32.25), (0.10, 32.28), (0.10, 32.31), (0.10, 32.34), (0.10, 32.37),
        (0.10, 32.40), (0.10, 32.43), (0.10, 32.46), (0.10, 32.49), (0.10, 32.52),
        (0.10, 32.55), (0.10, 32.58), (0.10, 32.61), (0.10, 32.64), (0.10, 32.67),
        (0.10, 32.70), (0.10, 32.73),

        (0.13, 32.25), (0.13, 32.28), (0.13, 32.31), (0.13, 32.34), (0.13, 32.37),
        (0.13, 32.40), (0.13, 32.43), (0.13, 32.46), (0.13, 32.49), (0.13, 32.52),
        (0.13, 32.55), (0.13, 32.58), (0.13, 32.61), (0.13, 32.64), (0.13, 32.67),
        (0.13, 32.70), (0.13, 32.73),

        (0.16, 32.25), (0.16, 32.28), (0.16, 32.31), (0.16, 32.34), (0.16, 32.37),
        (0.16, 32.40), (0.16, 32.43), (0.16, 32.46), (0.16, 32.49), (0.16, 32.52),
        (0.16, 32.55), (0.16, 32.58), (0.16, 32.61), (0.16, 32.64), (0.16, 32.67),
        (0.16, 32.70), (0.16, 32.73),

        (0.19, 32.25), (0.19, 32.28), (0.19, 32.31), (0.19, 32.34), (0.19, 32.37),
        (0.19, 32.40), (0.19, 32.43), (0.19, 32.46), (0.19, 32.49), (0.19, 32.52),
        (0.19, 32.55), (0.19, 32.58), (0.19, 32.61), (0.19, 32.64), (0.19, 32.67),
        (0.19, 32.70), (0.19, 32.73),

        (0.22, 32.25), (0.22, 32.28), (0.22, 32.31), (0.22, 32.34), (0.22, 32.37),
        (0.22, 32.40), (0.22, 32.43), (0.22, 32.46), (0.22, 32.49), (0.22, 32.52),
        (0.22, 32.55), (0.22, 32.58), (0.22, 32.61), (0.22, 32.64), (0.22, 32.67),
        (0.22, 32.70), (0.22, 32.73),

        (0.25, 32.25), (0.25, 32.28), (0.25, 32.31), (0.25, 32.34), (0.25, 32.37),
        (0.25, 32.40), (0.25, 32.43), (0.25, 32.46), (0.25, 32.49), (0.25, 32.52),
        (0.25, 32.55), (0.25, 32.58), (0.25, 32.61), (0.25, 32.64), (0.25, 32.67),
        (0.25, 32.70), (0.25, 32.73),

        (0.28, 32.25), (0.28, 32.28), (0.28, 32.31), (0.28, 32.34), (0.28, 32.37),
        (0.28, 32.40), (0.28, 32.43), (0.28, 32.46), (0.28, 32.49), (0.28, 32.52),
        (0.28, 32.55), (0.28, 32.58), (0.28, 32.61), (0.28, 32.64), (0.28, 32.67),
        (0.28, 32.70), (0.28, 32.73),

        (0.31, 32.25), (0.31, 32.28), (0.31, 32.31), (0.31, 32.34), (0.31, 32.37),
        (0.31, 32.40), (0.31, 32.43), (0.31, 32.46), (0.31, 32.49), (0.31, 32.52),
        (0.31, 32.55), (0.31, 32.58), (0.31, 32.61), (0.31, 32.64), (0.31, 32.67),
        (0.31, 32.70), (0.31, 32.73),

        (0.34, 32.25), (0.34, 32.28), (0.34, 32.31), (0.34, 32.34), (0.34, 32.37),
        (0.34, 32.40), (0.34, 32.43), (0.34, 32.46), (0.34, 32.49), (0.34, 32.52),
        (0.34, 32.55), (0.34, 32.58), (0.34, 32.61), (0.34, 32.64), (0.34, 32.67),
        (0.34, 32.70), (0.34, 32.73),

        (0.37, 32.25), (0.37, 32.28), (0.37, 32.31), (0.37, 32.34), (0.37, 32.37),
        (0.37, 32.40), (0.37, 32.43), (0.37, 32.46), (0.37, 32.49), (0.37, 32.52),
        (0.37, 32.55), (0.37, 32.58), (0.37, 32.61), (0.37, 32.64), (0.37, 32.67),
        (0.37, 32.70), (0.37, 32.73),

        (0.40, 32.25), (0.40, 32.28), (0.40, 32.31), (0.40, 32.34), (0.40, 32.37),
        (0.40, 32.40), (0.40, 32.43), (0.40, 32.46), (0.40, 32.49), (0.40, 32.52),
        (0.40, 32.55), (0.40, 32.58), (0.40, 32.61), (0.40, 32.64), (0.40, 32.67),
        (0.40, 32.70), (0.40, 32.73),

        (0.43, 32.25), (0.43, 32.28), (0.43, 32.31), (0.43, 32.34), (0.43, 32.37),
        (0.43, 32.40), (0.43, 32.43), (0.43, 32.46), (0.43, 32.49), (0.43, 32.52),
        (0.43, 32.55), (0.43, 32.58), (0.43, 32.61), (0.43, 32.64), (0.43, 32.67),
        (0.43, 32.70), (0.43, 32.73),

        (0.46, 32.25), (0.46, 32.28), (0.46, 32.31), (0.46, 32.34), (0.46, 32.37),
        (0.46, 32.40), (0.46, 32.43), (0.46, 32.46), (0.46, 32.49), (0.46, 32.52),
        (0.46, 32.55), (0.46, 32.58), (0.46, 32.61), (0.46, 32.64), (0.46, 32.67),
        (0.46, 32.70), (0.46, 32.73),

        (0.49, 32.25), (0.49, 32.28), (0.49, 32.31), (0.49, 32.34), (0.49, 32.37),
        (0.49, 32.40), (0.49, 32.43), (0.49, 32.46), (0.49, 32.49), (0.49, 32.52),
        (0.49, 32.55), (0.49, 32.58), (0.49, 32.61), (0.49, 32.64), (0.49, 32.67),
        (0.49, 32.70), (0.49, 32.73),

        (0.52, 32.25), (0.52, 32.28), (0.52, 32.31), (0.52, 32.34), (0.52, 32.37),
        (0.52, 32.40), (0.52, 32.43), (0.52, 32.46), (0.52, 32.49), (0.52, 32.52),
        (0.52, 32.55), (0.52, 32.58), (0.52, 32.61), (0.52, 32.64), (0.52, 32.67),
        (0.52, 32.70), (0.52, 32.73),

        (0.55, 32.25), (0.55, 32.28), (0.55, 32.31), (0.55, 32.34), (0.55, 32.37),
        (0.55, 32.40), (0.55, 32.43), (0.55, 32.46), (0.55, 32.49), (0.55, 32.52),
        (0.55, 32.55), (0.55, 32.58), (0.55, 32.61), (0.55, 32.64), (0.55, 32.67),
        (0.55, 32.70), (0.55, 32.73),
    ],
    "Mukono": [
        # ========== MUKONO TOWN / MUNICIPALITY CORE (very dense) ==========
        (0.32, 32.72), (0.32, 32.73), (0.32, 32.74), (0.32, 32.75), (0.32, 32.76), (0.32, 32.77),
        (0.33, 32.72), (0.33, 32.73), (0.33, 32.74), (0.33, 32.75), (0.33, 32.76), (0.33, 32.77),
        (0.34, 32.72), (0.34, 32.73), (0.34, 32.74), (0.34, 32.75), (0.34, 32.76), (0.34, 32.77),
        (0.35, 32.72), (0.35, 32.73), (0.35, 32.74), (0.35, 32.75), (0.35, 32.76), (0.35, 32.77),
        (0.36, 32.72), (0.36, 32.73), (0.36, 32.74), (0.36, 32.75), (0.36, 32.76), (0.36, 32.77),
        (0.37, 32.72), (0.37, 32.73), (0.37, 32.74), (0.37, 32.75), (0.37, 32.76), (0.37, 32.77),

        # ========== SEETA / BWEYOGERERE BORDER AREA ==========
        (0.30, 32.68), (0.30, 32.69), (0.30, 32.70), (0.30, 32.71), (0.30, 32.72),
        (0.31, 32.68), (0.31, 32.69), (0.31, 32.70), (0.31, 32.71), (0.31, 32.72),
        (0.32, 32.68), (0.32, 32.69), (0.32, 32.70), (0.32, 32.71),
        (0.33, 32.68), (0.33, 32.69), (0.33, 32.70), (0.33, 32.71),
        (0.34, 32.68), (0.34, 32.69), (0.34, 32.70), (0.34, 32.71),

        # ========== NAMA / NORTHERN SIDE ==========
        (0.37, 32.75), (0.37, 32.76), (0.37, 32.77), (0.37, 32.78), (0.37, 32.79),
        (0.38, 32.75), (0.38, 32.76), (0.38, 32.77), (0.38, 32.78), (0.38, 32.79),
        (0.39, 32.75), (0.39, 32.76), (0.39, 32.77), (0.39, 32.78), (0.39, 32.79),
        (0.40, 32.75), (0.40, 32.76), (0.40, 32.77), (0.40, 32.78), (0.40, 32.79),
        (0.41, 32.75), (0.41, 32.76), (0.41, 32.77), (0.41, 32.78), (0.41, 32.79),

        # ========== KYAMPISI / GOMA AREA ==========
        (0.38, 32.70), (0.38, 32.71), (0.38, 32.72),
        (0.39, 32.70), (0.39, 32.71), (0.39, 32.72),
        (0.40, 32.70), (0.40, 32.71), (0.40, 32.72),
        (0.41, 32.70), (0.41, 32.71), (0.41, 32.72),
        (0.42, 32.70), (0.42, 32.71), (0.42, 32.72),

        # ========== LUGAZI DIRECTION (EAST) ==========
        (0.34, 32.80), (0.34, 32.81), (0.34, 32.82), (0.34, 32.83),
        (0.35, 32.80), (0.35, 32.81), (0.35, 32.82), (0.35, 32.83),
        (0.36, 32.80), (0.36, 32.81), (0.36, 32.82), (0.36, 32.83),
        (0.37, 32.80), (0.37, 32.81), (0.37, 32.82), (0.37, 32.83),
        (0.38, 32.80), (0.38, 32.81), (0.38, 32.82), (0.38, 32.83),

        # ========== SOUTHERN SIDE (KATOSI / MPATTA DIRECTION) ==========
        (0.28, 32.72), (0.28, 32.73), (0.28, 32.74), (0.28, 32.75), (0.28, 32.76),
        (0.29, 32.72), (0.29, 32.73), (0.29, 32.74), (0.29, 32.75), (0.29, 32.76),
        (0.30, 32.73), (0.30, 32.74), (0.30, 32.75), (0.30, 32.76),
        (0.27, 32.74), (0.27, 32.75),

        # ========== NAKISUNGA / NTENJERU SIDE ==========
        (0.32, 32.78), (0.32, 32.79), (0.32, 32.80),
        (0.33, 32.78), (0.33, 32.79), (0.33, 32.80),
        (0.34, 32.78), (0.34, 32.79),
        (0.35, 32.78), (0.35, 32.79),

        # ========== EXTRA COVERAGE ==========
        (0.42, 32.74), (0.42, 32.75), (0.42, 32.76),
        (0.43, 32.74), (0.43, 32.75), (0.43, 32.76),
        (0.31, 32.76), (0.31, 32.77), (0.31, 32.78),
        (0.36, 32.68), (0.36, 32.69),
        (0.39, 32.73), (0.39, 32.74),
    ],
    "Western Uganda": [
        # ========== MBARARA CLUSTER (very dense) ==========
        (-0.70, 30.55), (-0.70, 30.58), (-0.70, 30.61), (-0.70, 30.64), (-0.70, 30.67), (-0.70, 30.70),
        (-0.67, 30.55), (-0.67, 30.58), (-0.67, 30.61), (-0.67, 30.64), (-0.67, 30.67), (-0.67, 30.70),
        (-0.64, 30.55), (-0.64, 30.58), (-0.64, 30.61), (-0.64, 30.64), (-0.64, 30.67), (-0.64, 30.70),
        (-0.61, 30.55), (-0.61, 30.58), (-0.61, 30.61), (-0.61, 30.64), (-0.61, 30.67), (-0.61, 30.70),
        (-0.58, 30.55), (-0.58, 30.58), (-0.58, 30.61), (-0.58, 30.64), (-0.58, 30.67), (-0.58, 30.70),
        (-0.55, 30.55), (-0.55, 30.58), (-0.55, 30.61), (-0.55, 30.64), (-0.55, 30.67), (-0.55, 30.70),

        # ========== FORT PORTAL / KABAROLE CLUSTER ==========
        (0.55, 30.20), (0.55, 30.23), (0.55, 30.26), (0.55, 30.29), (0.55, 30.32), (0.55, 30.35),
        (0.58, 30.20), (0.58, 30.23), (0.58, 30.26), (0.58, 30.29), (0.58, 30.32), (0.58, 30.35),
        (0.61, 30.20), (0.61, 30.23), (0.61, 30.26), (0.61, 30.29), (0.61, 30.32), (0.61, 30.35),
        (0.64, 30.20), (0.64, 30.23), (0.64, 30.26), (0.64, 30.29), (0.64, 30.32), (0.64, 30.35),
        (0.67, 30.20), (0.67, 30.23), (0.67, 30.26), (0.67, 30.29), (0.67, 30.32), (0.67, 30.35),
        (0.70, 30.20), (0.70, 30.23), (0.70, 30.26), (0.70, 30.29), (0.70, 30.32), (0.70, 30.35),

        # ========== KASESE CLUSTER ==========
        (0.10, 30.00), (0.10, 30.03), (0.10, 30.06), (0.10, 30.09), (0.10, 30.12), (0.10, 30.15),
        (0.13, 30.00), (0.13, 30.03), (0.13, 30.06), (0.13, 30.09), (0.13, 30.12), (0.13, 30.15),
        (0.16, 30.00), (0.16, 30.03), (0.16, 30.06), (0.16, 30.09), (0.16, 30.12), (0.16, 30.15),
        (0.19, 30.00), (0.19, 30.03), (0.19, 30.06), (0.19, 30.09), (0.19, 30.12), (0.19, 30.15),
        (0.22, 30.00), (0.22, 30.03), (0.22, 30.06), (0.22, 30.09), (0.22, 30.12), (0.22, 30.15),
        (0.25, 30.00), (0.25, 30.03), (0.25, 30.06), (0.25, 30.09), (0.25, 30.12), (0.25, 30.15),

        # ========== KABALE CLUSTER ==========
        (-1.30, 29.90), (-1.30, 29.93), (-1.30, 29.96), (-1.30, 29.99), (-1.30, 30.02), (-1.30, 30.05),
        (-1.27, 29.90), (-1.27, 29.93), (-1.27, 29.96), (-1.27, 29.99), (-1.27, 30.02), (-1.27, 30.05),
        (-1.24, 29.90), (-1.24, 29.93), (-1.24, 29.96), (-1.24, 29.99), (-1.24, 30.02), (-1.24, 30.05),
        (-1.21, 29.90), (-1.21, 29.93), (-1.21, 29.96), (-1.21, 29.99), (-1.21, 30.02), (-1.21, 30.05),
        (-1.18, 29.90), (-1.18, 29.93), (-1.18, 29.96), (-1.18, 29.99), (-1.18, 30.02), (-1.18, 30.05),

        # ========== BUSHENYI / ISHAKA CLUSTER ==========
        (-0.35, 30.20), (-0.35, 30.23), (-0.35, 30.26), (-0.35, 30.29), (-0.35, 30.32),
        (-0.32, 30.20), (-0.32, 30.23), (-0.32, 30.26), (-0.32, 30.29), (-0.32, 30.32),
        (-0.29, 30.20), (-0.29, 30.23), (-0.29, 30.26), (-0.29, 30.29), (-0.29, 30.32),
        (-0.26, 30.20), (-0.26, 30.23), (-0.26, 30.26), (-0.26, 30.29), (-0.26, 30.32),
        (-0.23, 30.20), (-0.23, 30.23), (-0.23, 30.26), (-0.23, 30.29), (-0.23, 30.32),

        # ========== NTUNGAMO CLUSTER ==========
        (-1.05, 30.15), (-1.05, 30.18), (-1.05, 30.21), (-1.05, 30.24), (-1.05, 30.27),
        (-1.02, 30.15), (-1.02, 30.18), (-1.02, 30.21), (-1.02, 30.24), (-1.02, 30.27),
        (-0.99, 30.15), (-0.99, 30.18), (-0.99, 30.21), (-0.99, 30.24), (-0.99, 30.27),
        (-0.96, 30.15), (-0.96, 30.18), (-0.96, 30.21), (-0.96, 30.24), (-0.96, 30.27),

        # ========== RUKUNGIRI CLUSTER ==========
        (-0.90, 30.35), (-0.90, 30.38), (-0.90, 30.41), (-0.90, 30.44), (-0.90, 30.47),
        (-0.87, 30.35), (-0.87, 30.38), (-0.87, 30.41), (-0.87, 30.44), (-0.87, 30.47),
        (-0.84, 30.35), (-0.84, 30.38), (-0.84, 30.41), (-0.84, 30.44), (-0.84, 30.47),
        (-0.81, 30.35), (-0.81, 30.38), (-0.81, 30.41), (-0.81, 30.44), (-0.81, 30.47),

        # ========== HOIMA CLUSTER ==========
        (1.35, 31.25), (1.35, 31.28), (1.35, 31.31), (1.35, 31.34), (1.35, 31.37), (1.35, 31.40),
        (1.38, 31.25), (1.38, 31.28), (1.38, 31.31), (1.38, 31.34), (1.38, 31.37), (1.38, 31.40),
        (1.41, 31.25), (1.41, 31.28), (1.41, 31.31), (1.41, 31.34), (1.41, 31.37), (1.41, 31.40),
        (1.44, 31.25), (1.44, 31.28), (1.44, 31.31), (1.44, 31.34), (1.44, 31.37), (1.44, 31.40),
        (1.47, 31.25), (1.47, 31.28), (1.47, 31.31), (1.47, 31.34), (1.47, 31.37), (1.47, 31.40),

        # ========== MASINDI CLUSTER ==========
        (1.60, 31.65), (1.60, 31.68), (1.60, 31.71), (1.60, 31.74), (1.60, 31.77),
        (1.63, 31.65), (1.63, 31.68), (1.63, 31.71), (1.63, 31.74), (1.63, 31.77),
        (1.66, 31.65), (1.66, 31.68), (1.66, 31.71), (1.66, 31.74), (1.66, 31.77),
        (1.69, 31.65), (1.69, 31.68), (1.69, 31.71), (1.69, 31.74), (1.69, 31.77),
        (1.72, 31.65), (1.72, 31.68), (1.72, 31.71), (1.72, 31.74), (1.72, 31.77),

        # ========== EXTRA IMPORTANT TOWNS ==========
        (0.45, 30.25),  # around Kamwenge / Kyenjojo corridor
        (0.50, 30.40),
        (-0.40, 30.40),  # Sheema / Buhweju area
        (-0.50, 30.50),
        (-0.80, 29.90),  # Kisoro direction
        (-1.10, 29.80),
        (0.80, 30.10),  # Bundibugyo direction
        (1.20, 31.00),  # between Hoima and Fort Portal
        (0.90, 30.80),
        (-0.15, 30.50),  # between Mbarara and Bushenyi
    ],
    "Masaka": [
        # ========== MASAKA CITY CORE (very dense) ==========
        (-0.36, 31.70), (-0.36, 31.71), (-0.36, 31.72), (-0.36, 31.73), (-0.36, 31.74), (-0.36, 31.75),
        (-0.35, 31.70), (-0.35, 31.71), (-0.35, 31.72), (-0.35, 31.73), (-0.35, 31.74), (-0.35, 31.75),
        (-0.34, 31.70), (-0.34, 31.71), (-0.34, 31.72), (-0.34, 31.73), (-0.34, 31.74), (-0.34, 31.75),
        (-0.33, 31.70), (-0.33, 31.71), (-0.33, 31.72), (-0.33, 31.73), (-0.33, 31.74), (-0.33, 31.75),
        (-0.32, 31.70), (-0.32, 31.71), (-0.32, 31.72), (-0.32, 31.73), (-0.32, 31.74), (-0.32, 31.75),

        # ========== NYENDO AREA ==========
        (-0.31, 31.70), (-0.31, 31.71), (-0.31, 31.72), (-0.31, 31.73), (-0.31, 31.74),
        (-0.30, 31.70), (-0.30, 31.71), (-0.30, 31.72), (-0.30, 31.73), (-0.30, 31.74),
        (-0.29, 31.71), (-0.29, 31.72), (-0.29, 31.73),

        # ========== KIMANYA / KYABAKUZA ==========
        (-0.35, 31.76), (-0.35, 31.77), (-0.35, 31.78),
        (-0.34, 31.76), (-0.34, 31.77), (-0.34, 31.78),
        (-0.33, 31.76), (-0.33, 31.77), (-0.33, 31.78),
        (-0.32, 31.76), (-0.32, 31.77),

        # ========== VILLA MARIA / BUKOTO DIRECTION ==========
        (-0.35, 31.66), (-0.35, 31.67), (-0.35, 31.68), (-0.35, 31.69),
        (-0.34, 31.66), (-0.34, 31.67), (-0.34, 31.68), (-0.34, 31.69),
        (-0.33, 31.66), (-0.33, 31.67), (-0.33, 31.68), (-0.33, 31.69),
        (-0.36, 31.67), (-0.36, 31.68),

        # ========== MUKUNGWE / SOUTHERN SIDE ==========
        (-0.38, 31.72), (-0.38, 31.73), (-0.38, 31.74), (-0.38, 31.75),
        (-0.39, 31.72), (-0.39, 31.73), (-0.39, 31.74), (-0.39, 31.75),
        (-0.40, 31.72), (-0.40, 31.73), (-0.40, 31.74),
        (-0.37, 31.72), (-0.37, 31.73), (-0.37, 31.74),

        # ========== KYANAMUKAKA / RURAL EDGE ==========
        (-0.30, 31.75), (-0.30, 31.76), (-0.30, 31.77),
        (-0.29, 31.75), (-0.29, 31.76),
        (-0.28, 31.74), (-0.28, 31.75),

        # ========== EXTRA COVERAGE ==========
        (-0.37, 31.70), (-0.37, 31.71),
        (-0.36, 31.76), (-0.36, 31.77),
        (-0.31, 31.68), (-0.31, 31.69),
        (-0.33, 31.79), (-0.34, 31.79),
        (-0.41, 31.73), (-0.41, 31.74),
    ],
    "Jinja": [
        # ========== JINJA CITY CORE (very dense) ==========
        (0.42, 33.18), (0.42, 33.19), (0.42, 33.20), (0.42, 33.21), (0.42, 33.22), (0.42, 33.23),
        (0.43, 33.18), (0.43, 33.19), (0.43, 33.20), (0.43, 33.21), (0.43, 33.22), (0.43, 33.23),
        (0.44, 33.18), (0.44, 33.19), (0.44, 33.20), (0.44, 33.21), (0.44, 33.22), (0.44, 33.23),
        (0.45, 33.18), (0.45, 33.19), (0.45, 33.20), (0.45, 33.21), (0.45, 33.22), (0.45, 33.23),
        (0.46, 33.18), (0.46, 33.19), (0.46, 33.20), (0.46, 33.21), (0.46, 33.22), (0.46, 33.23),
        (0.47, 33.18), (0.47, 33.19), (0.47, 33.20), (0.47, 33.21), (0.47, 33.22), (0.47, 33.23),

        # ========== WALUKUBA / MASESE / SOUTHERN SIDE ==========
        (0.40, 33.17), (0.40, 33.18), (0.40, 33.19), (0.40, 33.20), (0.40, 33.21),
        (0.41, 33.17), (0.41, 33.18), (0.41, 33.19), (0.41, 33.20), (0.41, 33.21),
        (0.42, 33.17),
        (0.39, 33.18), (0.39, 33.19), (0.39, 33.20),

        # ========== BUGEMBE / KIMAKA / NORTHERN SIDE ==========
        (0.46, 33.24), (0.46, 33.25), (0.46, 33.26),
        (0.47, 33.24), (0.47, 33.25), (0.47, 33.26),
        (0.48, 33.24), (0.48, 33.25), (0.48, 33.26),
        (0.49, 33.24), (0.49, 33.25), (0.49, 33.26),
        (0.50, 33.24), (0.50, 33.25), (0.50, 33.26),

        # ========== KAKIRA AREA ==========
        (0.48, 33.27), (0.48, 33.28), (0.48, 33.29),
        (0.49, 33.27), (0.49, 33.28), (0.49, 33.29),
        (0.50, 33.27), (0.50, 33.28), (0.50, 33.29),
        (0.51, 33.27), (0.51, 33.28), (0.51, 33.29),

        # ========== BUWENGE ROAD / WESTERN CORRIDOR ==========
        (0.41, 33.14), (0.41, 33.15), (0.41, 33.16),
        (0.42, 33.14), (0.42, 33.15), (0.42, 33.16),
        (0.43, 33.14), (0.43, 33.15), (0.43, 33.16),
        (0.44, 33.14), (0.44, 33.15), (0.44, 33.16),

        # ========== BUSEDDE / EASTERN SIDE ==========
        (0.44, 33.27), (0.44, 33.28), (0.44, 33.29),
        (0.45, 33.27), (0.45, 33.28), (0.45, 33.29),
        (0.46, 33.27), (0.46, 33.28), (0.46, 33.29),

        # ========== NJERU SIDE (across the Nile - still useful) ==========
        (0.43, 33.24), (0.43, 33.25),
        (0.44, 33.24), (0.44, 33.25),
        (0.45, 33.24), (0.45, 33.25),

        # ========== EXTRA COVERAGE POINTS ==========
        (0.40, 33.22), (0.40, 33.23),
        (0.48, 33.20), (0.48, 33.21), (0.48, 33.22),
        (0.50, 33.22), (0.50, 33.23),
        (0.38, 33.19), (0.38, 33.20),
        (0.52, 33.25), (0.52, 33.26),
    ]
}

# ====================== SESSION STATE ======================
if "stored_places" not in st.session_state:
    st.session_state.stored_places = []
if "used_points" not in st.session_state:
    st.session_state.used_points = set()
if "last_params" not in st.session_state:
    st.session_state.last_params = ""
if "point_index" not in st.session_state:
    st.session_state.point_index = 0


# ====================== IMPROVED HELPER FUNCTIONS ======================

def fetch_place_details(place_id, key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,international_phone_number,website,types",
        "key": key
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        if data.get("status") == "OK":
            result = data.get("result", {})
            phone = result.get("formatted_phone_number") or result.get("international_phone_number") or "N/A"
            website = result.get("website") or "N/A"

            raw_types = result.get("types", [])
            filtered_types = [t.replace("_", " ").title() for t in raw_types
                              if t not in ["point_of_interest", "establishment"]]
            business_deals_in = ", ".join(filtered_types) if filtered_types else "N/A"

            return phone, website, business_deals_in
    except:
        pass
    return "N/A", "N/A", "N/A"


def nearby_search_full(lat, lng, keyword, key, radius_m, place_type=None, max_pages=3):
    """
    Improved Nearby Search with full pagination (up to 60 results).
    Works for any keyword (Hardware, School, Pharmacy, SACCO, Bank, etc.)
    """
    all_results = []
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "key": key
    }

    # Add keyword if provided
    if keyword and keyword.strip():
        params["keyword"] = keyword.strip()

    # Optional type (useful for bank, school, hospital, etc.)
    if place_type and place_type.strip():
        params["type"] = place_type.strip().lower()

    for page in range(max_pages):
        try:
            r = requests.get(url, params=params, timeout=15)
            data = r.json()

            status = data.get("status")

            if status == "OK":
                results = data.get("results", [])
                all_results.extend(results)
            elif status == "ZERO_RESULTS":
                break
            else:
                # OVER_QUERY_LIMIT, REQUEST_DENIED, etc.
                break

            next_token = data.get("next_page_token")
            if not next_token:
                break

            # Google requires ~2 seconds delay before using next_page_token
            time.sleep(2.2)

            # Next page only needs the token
            params = {
                "pagetoken": next_token,
                "key": key
            }

        except Exception as e:
            break

    return all_results


def process_places(places, region_name, keyword, key):
    extracted = []
    for place in places:
        place_id = place.get("place_id")
        if not place_id:
            continue

        phone, website, business_deals_in = fetch_place_details(place_id, key)

        extracted.append({
            "Company Name": place.get("name", "N/A"),
            "Region": region_name,
            "Category": keyword.capitalize() if keyword else "General",
            "Business Deals In": business_deals_in,
            "Phone Contact": phone,
            "Website": website,
            "Physical Address": place.get("vicinity") or place.get("formatted_address", "N/A"),
            "Rating": place.get("rating", "N/A"),
            "Place ID": place_id,
            "Lat": place["geometry"]["location"]["lat"],
            "Lng": place["geometry"]["location"]["lng"],
        })
    return extracted


# ====================== MAIN LOGIC ======================
current_params = f"{region}_{search_query}_{radius}"

if st.session_state.last_params != current_params:
    st.session_state.stored_places = []
    st.session_state.used_points = set()
    st.session_state.point_index = 0
    st.session_state.last_params = current_params

grid = REGION_GRIDS[region]
total_points = len(grid)

# First load
if len(st.session_state.stored_places) == 0 and st.session_state.point_index == 0:
    with st.spinner(f"Scanning first points in {region}..."):
        batch = []
        for i in range(min(3, total_points)):
            lat, lng = grid[i]
            places = nearby_search_full(
                lat=lat,
                lng=lng,
                keyword=search_query,
                key=api_key,
                radius_m=radius,
                place_type=None,
                max_pages=3
            )
            batch.extend(process_places(places, region, search_query, api_key))
            st.session_state.used_points.add(i)
            st.session_state.point_index = i + 1
            time.sleep(1.1)

        df_temp = pd.DataFrame(batch)
        if not df_temp.empty:
            df_temp = df_temp.drop_duplicates(subset=["Place ID"])
            st.session_state.stored_places = df_temp.to_dict("records")

# Display
if st.session_state.stored_places:
    df = pd.DataFrame(st.session_state.stored_places)
    df = df.drop_duplicates(subset=["Place ID"]).reset_index(drop=True)
    df.insert(0, "No.", range(1, len(df) + 1))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Unique Places", len(df))
    m2.metric("Region", region)
    m3.metric("Keyword", search_query.capitalize())
    m4.metric("Points Scanned", f"{len(st.session_state.used_points)} / {total_points}")

    st.markdown("---")
    st.subheader(f"Results for “{search_query}” in {region}")

    st.dataframe(
        df[["No.", "Company Name", "Business Deals In", "Phone Contact", "Physical Address", "Rating", "Website"]],
        use_container_width=True,
        height=460
    )

    remaining = total_points - len(st.session_state.used_points)

    if remaining > 0:
        if st.button(f"🔄 Load Next Batch  ({remaining} points left)", type="primary", use_container_width=True):
            with st.spinner("Fetching next batch..."):
                new_batch = []
                points_to_load = min(3, remaining)
                for i in range(st.session_state.point_index, st.session_state.point_index + points_to_load):
                    if i >= total_points:
                        break
                    lat, lng = grid[i]
                    places = nearby_search_full(
                        lat=lat,
                        lng=lng,
                        keyword=search_query,
                        key=api_key,
                        radius_m=radius,
                        place_type=None,
                        max_pages=3
                    )
                    new_batch.extend(process_places(places, region, search_query, api_key))
                    st.session_state.used_points.add(i)
                    time.sleep(1.1)

                st.session_state.point_index += points_to_load
                combined = st.session_state.stored_places + new_batch
                df_combined = pd.DataFrame(combined).drop_duplicates(subset=["Place ID"])
                st.session_state.stored_places = df_combined.to_dict("records")
                st.rerun()
    else:
        st.success("✅ All grid points in this region have been scanned.")

    st.markdown("---")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export All Leads to CSV",
        data=csv,
        file_name=f"{region}_{search_query}_leads.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.warning("No places found yet. Try a different keyword or increase the radius.")
