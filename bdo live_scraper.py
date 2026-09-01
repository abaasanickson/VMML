import time
import random
import re
import json
import hashlib
import urllib.parse
from datetime import datetime, timezone, timedelta

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ====================== PAGE CONFIG ======================
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
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 6px;
    }
    .welcome-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .quote {
        font-style: italic;
        color: #38bdf8;
        border-left: 4px solid #3b82f6;
        padding-left: 16px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== QUOTES & WELCOME ======================
@st.cache_data(ttl=60)
def get_live_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and data[0].get("q"):
                return f'"{data[0]["q"]}" — {data[0].get("a", "Unknown")}'
    except Exception:
        pass
    return '"Dream big. Start small. Act now."'

def get_greeting():
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
    <div class="welcome-title">{greeting}. Ready to generate leads?</div>
    <div class="welcome-subtitle">Full coverage across Kampala, Wakiso, Mukono & Regional Directories</div>
    <div class="quote">{quote}</div>
</div>
""", unsafe_allow_html=True)

st.title("Full Region Business Lead Generator")
st.caption("Direct Uganda Directory, Registry & OpenStreetMap Search • Multi-Source Expansion • Deduplicated results")

# ====================== SIDEBAR ======================
st.sidebar.markdown("### ⚙️ Search Settings")

region = st.sidebar.selectbox(
    "Select Region",
    ["Kampala", "Wakiso", "Mukono", "Western Uganda", "Masaka", "Jinja"]
)

search_query = st.sidebar.text_input(
    "Business Type / Keyword",
    value="Hardware",
    help="e.g. School, Hardware, Pharmacy, Bank, Supermarket, Clinic..."
)

st.sidebar.markdown("---")
st.sidebar.info("Hybrid active: OpenStreetMap spatial data + Playwright headless browser scraping across public Ugandan directories and registries.")

# ====================== UGANDA SOURCE CATALOG & SCRAPERS ======================
DIRECTORY_SOURCES = [
    {"name": "Yellow Pages Uganda", "url": "https://www.yellowpages-uganda.com/"},
    {"name": "Yellow Uganda", "url": "https://www.yellow.ug/"},
    {"name": "Hotfrog Uganda", "url": "https://www.hotfrog.ug/"},
    {"name": "FinderAfrica Uganda", "url": "https://finderafrica.com/location/business-directory-uganda/"},
    {"name": "KCCA Business Register", "url": "https://www.kcca.go.ug/businesses"},
]

def clean_text(value):
    if value is None:
        return "N/A"
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value if value else "N/A"

def fetch_osm_grid_data(region_name, keyword):
    """Queries free OpenStreetMap Overpass API for geographic nodes and ways."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Region bounding box mapping
    bbox = "0.25,32.45,0.42,32.70" # Kampala default
    if region_name.lower() == 'wakiso':
        bbox = "0.05,32.30,0.60,32.65"
    elif region_name.lower() == 'mukono':
        bbox = "0.20,32.60,0.55,32.90"

    query = f"""
    [out:json][timeout:25];
    (
      node["shop"="{keyword.lower()}"]({bbox});
      way["shop"="{keyword.lower()}"]({bbox});
      node["amenity"="{keyword.lower()}"]({bbox});
      way["amenity"="{keyword.lower()}"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data=query, timeout=30)
        if response.status_code == 200:
            elements = response.json().get('elements', [])
            records = []
            for el in elements:
                if 'tags' in el:
                    name = el['tags'].get('name', 'Unnamed Entity')
                    records.append({
                        "Company Name": name,
                        "Region": region_name,
                        "Category": keyword.capitalize(),
                        "Business Deals In": keyword.capitalize(),
                        "Phone Contact": el['tags'].get('phone', el['tags'].get('contact:phone', 'N/A')),
                        "Website": el['tags'].get('website', 'N/A'),
                        "Physical Address": el['tags'].get('addr:street', region_name),
                        "Rating": "N/A",
                        "Lat": str(el.get('lat', 'N/A')),
                        "Lng": str(el.get('lon', 'N/A')),
                        "Data Source": "OpenStreetMap",
                        "Source URL": "OpenStreetMap Overpass API"
                    })
            return records
    except Exception as e:
        print(f"OSM Error: {e}")
    return []

def scrape_ugandan_directories(region_name, keyword):
    """Scrapes public directories and registries using Playwright headless browser."""
    aggregated_records = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            for source in DIRECTORY_SOURCES:
                target_url = f"{source['url']}?q={urllib.parse.quote(keyword)}&l={urllib.parse.quote(region_name)}"
                try:
                    page.goto(target_url, timeout=25000)
                    time.sleep(random.uniform(1.0, 2.0))
                    
                    for _ in range(2):
                        page.mouse.wheel(0, 1000)
                        time.sleep(0.8)

                    soup = BeautifulSoup(page.content(), 'html.parser')
                    listings = soup.select('.listing-card, .business-card, .search-item, article, .result-item')
                    
                    for item in listings:
                        name_elem = item.select_one('h2, h3, .title, .business-name')
                        phone_elem = item.select_one('.phone, .tel, a[href^="tel:"]')
                        address_elem = item.select_one('.address, .location')
                        
                        name = clean_text(name_elem.get_text(strip=True) if name_elem else None)
                        if name != "N/A":
                            aggregated_records.append({
                                "Company Name": name,
                                "Region": region_name,
                                "Category": keyword.capitalize(),
                                "Business Deals In": keyword.capitalize(),
                                "Phone Contact": clean_text(phone_elem.get_text(strip=True) if phone_elem else "N/A"),
                                "Website": source["url"],
                                "Physical Address": clean_text(address_elem.get_text(strip=True) if address_elem else region_name),
                                "Rating": "N/A",
                                "Lat": "N/A",
                                "Lng": "N/A",
                                "Data Source": source["name"],
                                "Source URL": target_url
                            })
                except Exception:
                    continue
            browser.close()
    except Exception as e:
        print(f"Playwright error: {e}")
    return aggregated_records

# ====================== SESSION STATE & MAIN LOGIC ======================
if "stored_places" not in st.session_state:
    st.session_state.stored_places = []
if "last_search" not in st.session_state:
    st.session_state.last_search = ""

current_search_key = f"{region}|{search_query}"

if st.session_state.last_search != current_search_key:
    st.session_state.stored_places = []
    st.session_state.last_search = current_search_key

if not search_query.strip():
    st.warning("Enter a business keyword to start the directory search.")
else:
    if not st.session_state.stored_places:
        with st.spinner(f"Scraping OpenStreetMap & Ugandan Directories for '{search_query}' in {region}..."):
            osm_data = fetch_osm_grid_data(region, search_query)
            dir_data = scrape_ugandan_directories(region, search_query)
            
            combined = osm_data + dir_data
            if combined:
                df_temp = pd.DataFrame(combined)
                df_temp = df_temp.drop_duplicates(subset=["Company Name", "Physical Address"])
                st.session_state.stored_places = df_temp.to_dict("records")

    if st.session_state.stored_places:
        df = pd.DataFrame(st.session_state.stored_places)
        df.insert(0, "No.", range(1, len(df) + 1))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Unique Places", len(df))
        m2.metric("Region", region)
        m3.metric("Keyword", search_query.capitalize())
        m4.metric("Sources Scanned", "OSM + Directories")

        st.markdown("---")
        st.subheader(f"Results for “{search_query}” in {region}")

        display_columns = [
            "No.", "Company Name", "Business Deals In", "Phone Contact",
            "Physical Address", "Rating", "Website", "Data Source", "Source URL"
        ]
        display_columns = [c for c in display_columns if c in df.columns]

        st.dataframe(
            df[display_columns],
            use_container_width=True,
            height=460
        )

        st.markdown("---")
        csv = df.drop(columns=["No."], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export All Leads to CSV",
            data=csv,
            file_name=f"{region}_{search_query}_leads.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("No public records found for this keyword/region combination. Try another search term.")
