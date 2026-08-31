import time
import random
import re
import json
import hashlib
from urllib.parse import quote_plus
import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timezone, timedelta

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="Uganda Heavy-Duty Business Scraper", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 100%);
        color: #f3f4f6;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #090d16 100%);
        border-right: 1px solid #1f2937;
    }
    h1, h2, h3 { color: #ffffff !important; }
    .stButton > button {
        background: linear-gradient(180deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.title("Uganda Heavy-Duty Multi-Sector Business Harvester")
st.caption("Zero-API-Cost • High-Density Matrix Scanning • OpenStreetMap + Directory + Frontend Maps Grid")

# ====================== SECTOR MATRIX EXPANSION ======================
# Automatically expands a broad sector keyword into granular sub-categories
SECTOR_EXPANSIONS = {
    "hardware": ["hardware", "cement shop", "building materials", "plumbing supplies", "electrical shop", "steel fabrication", "tools supplier", "timber yard", "paints distributor"],
    "pharmacy": ["pharmacy", "drug shop", "medical clinic", "medical laboratory", "hospital", "dental clinic", "veterinary drug shop", "healthcare center"],
    "supermarket": ["supermarket", "grocery store", "mini market", "wholesale shop", "provision store", "general merchandise", "hypermarket"],
    "school": ["primary school", "secondary school", "nursery school", "kindergarten", "vocational institution", "training center", "coaching college"],
    "restaurant": ["restaurant", "cafe", "hotel", "fast food", "bar and grill", "local food joint", "caterers", "bakery"],
    "automotive": ["spare parts", "auto garage", "car dealer", "mechanic", "tyre center", "car wash", "fuel station", "motorcycle spare parts"]
}

# Detailed regional bounding boxes for deep OpenStreetMap grid queries
REGION_BOXES = {
    "Kampala": [
        {"name": "Central Kampala", "box": "(0.30, 32.55, 0.33, 32.59)"},
        {"name": "Nakawa & Ntinda", "box": "(0.33, 32.58, 0.38, 32.65)"},
        {"name": "Kawempe & Bwaise", "box": "(0.35, 32.53, 0.42, 32.58)"},
        {"name": "Rubaga & Nateete", "box": "(0.28, 32.50, 0.32, 32.55)"},
        {"name": "Makindye & Ggaba", "box": "(0.25, 32.55, 0.30, 32.62)"}
    ],
    "Wakiso": [
        {"name": "Kira & Namugongo", "box": "(0.35, 32.60, 0.42, 32.70)"},
        {"name": "Nansana & Nabweru", "box": "(0.35, 32.50, 0.40, 32.55)"},
        {"name": "Entebbe Corridor", "box": "(0.05, 32.45, 0.25, 32.55)"},
        {"name": "Kajjansi & Katabi", "box": "(0.15, 32.50, 0.22, 32.58)"}
    ],
    "Mukono": [
        {"name": "Mukono Central & Seeta", "box": "(0.30, 32.70, 0.40, 32.80)"}
    ],
    "Jinja": [
        {"name": "Jinja Municipality", "box": "(0.40, 33.18, 0.47, 33.25)"}
    ],
    "Mbarara": [
        {"name": "Mbarara City", "box": "(-0.62, 30.63, -0.58, 30.68)"}
    ]
}

# ====================== SIDEBAR CONFIG ======================
st.sidebar.markdown("### ⚙️ Production Scraper Controls")

region = st.sidebar.selectbox("Select Region / Hub", list(REGION_BOXES.keys()))
selected_sector = st.sidebar.selectbox("Select Business Sector", list(SECTOR_EXPANSIONS.keys()))

custom_keyword_override = st.sidebar.text_input("Or Custom Search Query", value="", help="Overrides sector matrix if filled.")

st.sidebar.markdown("---")
deep_scan_maps = st.sidebar.checkbox("Enable Deep Google Maps Scroll (Playwright)", value=False, help="Runs headless browser automation to scroll and pull maximum listings. Requires playwright installed.")
max_scrolls = st.sidebar.slider("Maps Scroll Depth (Pages)", 1, 10, 3, help="Higher value = more businesses harvested from Google Maps frontend.")

# ====================== CORE UTILS ======================
def clean_text(val):
    if not val:
        return "N/A"
    return re.sub(r"\s+", " ", str(val)).strip()

def make_id(source, name, address=""):
    raw = f"{source}|{clean_text(name).lower()}|{clean_text(address).lower()}"
    return "prod_" + hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()[:24]

# ====================== ENGINE 1: OVERPASS GRID HARVESTER ======================
def harvest_openstreetmap_grid(region_name, keywords):
    sub_grids = REGION_BOXES.get(region_name, [{"name": region_name, "box": "(0.25, 32.50, 0.45, 32.70)"}])
    overpass_url = "https://overpass-api.de/api/interpreter"
    all_records = []
    
    session = requests.Session()
    session.headers.update({"User-Agent": "UgandaProductionScraper/2.0"})

    for grid in sub_grids:
        bbox = grid["box"]
        for kw in keywords:
            query = f"""
            [out:json][timeout:30];
            (
              node["name"~"{kw}", i]{bbox};
              way["name"~"{kw}", i]{bbox};
            );
            out body;
            >;
            out skel qt;
            """
            try:
                response = session.post(overpass_url, data={"data": query}, timeout=35)
                if response.status_code == 200:
                    data = response.json()
                    for el in data.get("elements", []):
                        tags = el.get("tags", {})
                        name = tags.get("name")
                        if not name:
                            continue
                        
                        address = ", ".join(filter(None, [tags.get("addr:street"), grid["name"], region_name]))
                        phone = tags.get("phone", tags.get("contact:phone", "N/A"))
                        website = tags.get("website", tags.get("contact:website", "N/A"))
                        category = tags.get("shop", tags.get("amenity", tags.get("office", kw)))

                        all_records.append({
                            "Company Name": clean_text(name),
                            "Region": region_name,
                            "Sub-Zone": grid["name"],
                            "Sector Category": clean_text(category).capitalize(),
                            "Matched Keyword": kw,
                            "Phone Contact": clean_text(phone),
                            "Website": clean_text(website),
                            "Physical Address": clean_text(address),
                            "Place ID": make_id("OSM-Grid", name, address),
                            "Lat": str(el.get("lat", "N/A")),
                            "Lng": str(el.get("lon", "N/A")),
                            "Data Source": "OpenStreetMap High-Density Grid"
                        })
                time.sleep(1.0) # Polite pacing to prevent server block
            except Exception:
                continue
    return all_records

# ====================== ENGINE 2: DIRECTORY MATRIX SCRAPER ======================
def harvest_directories(region_name, keywords):
    records = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    # Target high-yield public directory search routes
    for kw in keywords:
        search_urls = [
            f"https://www.yellowpages-uganda.com/search?q={quote_plus(kw)}",
            f"https://www.businesslist.co.ug/search?q={quote_plus(kw)}",
            f"https://finderafrica.com/?s={quote_plus(kw)}"
        ]
        
        for url in search_urls:
            try:
                res = session.get(url, timeout=12)
                if res.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(res.text, "html.parser")
                    for heading in soup.find_all(["h2", "h3", "h4", "a"]):
                        name = clean_text(heading.get_text("D", strip=True))
                        if len(name) < 3 or len(name) > 120 or name.lower() in {"home", "login", "search"}:
                            continue
                        parent = heading.parent
                        block = clean_text(parent.get_text(" ", strip=True)) if parent else name
                        
                        phones = re.findall(r"(?:\+?256|0)[\d\s().\-/]{7,}", block)
                        phone = phones[0] if phones else "N/A"
                        
                        records.append({
                            "Company Name": name,
                            "Region": region_name,
                            "Sub-Zone": region_name,
                            "Sector Category": kw.capitalize(),
                            "Matched Keyword": kw,
                            "Phone Contact": clean_text(phone),
                            "Website": "N/A",
                            "Physical Address": region_name,
                            "Place ID": make_id("Directory-Matrix", name),
                            "Lat": "N/A",
                            "Lng": "N/A",
                            "Data Source": "Public Directory Matrix"
                        })
                time.sleep(0.8)
            except Exception:
                continue
    return records

# ====================== ENGINE 3: PLAYWRIGHT INFINITE-SCROLL MAPS ======================
def harvest_frontend_maps_infinite(region_name, keywords, scroll_depth):
    records = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            
            for kw in keywords:
                query_str = f"{kw} in {region_name}, Uganda"
                search_url = f"https://www.google.com/maps/search/{quote_plus(query_str)}"
                try:
                    page.goto(search_url, timeout=35000)
                    page.wait_for_timeout(3000)
                    
                    # Target the scrollable container sidebar for infinite scrolling
                    sidebar_selector = 'div[role="feed"]'
                    try:
                        page.wait_for_selector(sidebar_selector, timeout=8000)
                        for _ in range(scroll_depth):
                            page.evaluate(f"""
                                const elem = document.querySelector('{sidebar_selector}');
                                if(elem) {{ elem.scrollTop = elem.scrollHeight; }}
                            """)
                            page.wait_for_timeout(2500)
                    except Exception:
                        pass # Fallback if specific feed structure varies
                    
                    # Extract listing elements
                    listings = page.locator('div.Nv2PK').all()
                    for item in listings:
                        try:
                            text_block = item.inner_text().split("\n")
                            name = text_block[0] if len(text_block) > 0 else "N/A"
                            full_text = " ".join(text_block)
                            
                            phones = re.findall(r"(?:\+?256|0)[\d\s().\-/]{7,}", full_text)
                            phone = phones[0] if phones else "N/A"
                            
                            records.append({
                                "Company Name": clean_text(name),
                                "Region": region_name,
                                "Sub-Zone": region_name,
                                "Sector Category": kw.capitalize(),
                                "Matched Keyword": kw,
                                "Phone Contact": clean_text(phone),
                                "Website": "N/A",
                                "Physical Address": region_name,
                                "Place ID": make_id("Maps-Infinite", name),
                                "Lat": "N/A",
                                "Lng": "N/A",
                                "Data Source": "Google Maps Frontend Infinite Scroll"
                            })
                        except Exception:
                            continue
                except Exception:
                    continue
            browser.close()
    except Exception:
        pass
    return records

# ====================== STATE & EXECUTION CONTROLLER ======================
if "production_leads" not in st.session_state:
    st.session_state.production_leads = []
if "exec_fingerprint" not in st.session_state:
    st.session_state.exec_fingerprint = ""

active_keywords = [custom_keyword_override.strip()] if custom_keyword_override.strip() else SECTOR_EXPANSIONS.get(selected_sector, [selected_sector])
current_fingerprint = hashlib.sha256(f"{region}|{selected_sector}|{custom_keyword_override}|{deep_scan_maps}".encode()).hexdigest()

if st.session_state.exec_fingerprint != current_fingerprint:
    st.session_state.production_leads = []
    st.session_state.exec_fingerprint = current_fingerprint

st.subheader(f"Target Matrix: {selected_sector.upper()} across {region}")
st.write(f"**Expanded Sub-Queries Matrix:** `{', '.join(active_keywords)}`")

if st.button("🚀 Launch Heavy-Duty Harvester Job", use_container_width=True):
    with st.spinner("Executing multi-threaded sector sweep across micro-grids and directories..."):
        master_list = []
        
        # 1. OpenStreetMap Grid Harvester
        osm_data = harvest_openstreetmap_grid(region, active_keywords)
        master_list.extend(osm_data)
        
        # 2. Directory Matrix Harvester
        dir_data = harvest_directories(region, active_keywords)
        master_list.extend(dir_data)
        
        # 3. Google Maps Infinite Scroll (Optional)
        if deep_scan_maps:
            maps_data = harvest_frontend_maps_infinite(region, active_keywords, max_scrolls)
            master_list.extend(maps_data)
            
        # Deduplication and processing
        if master_list:
            df_res = pd.DataFrame(master_list)
            df_res = df_res.drop_duplicates(subset=["Place ID"])
            st.session_state.production_leads = df_res.to_dict("records")
        else:
            st.session_state.production_leads = []

if st.session_state.production_leads:
    df_final = pd.DataFrame(st.session_state.production_leads)
    df_final.insert(0, "No.", range(1, len(df_final) + 1))
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Unique Records", len(df_final))
    c2.metric("Target Region", region)
    c3.metric("Sector Matrix", selected_sector.capitalize())
    c4.metric("Sub-Queries Used", len(active_keywords))

    st.markdown("---")
    st.dataframe(
        df_final[["No.", "Company Name", "Sector Category", "Matched Keyword", "Phone Contact", "Physical Address", "Sub-Zone", "Data Source"]],
        use_container_width=True,
        height=500
    )

    st.markdown("---")
    csv_data = df_final.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Sector Production Database (CSV)",
        data=csv_data,
        file_name=f"Uganda_{region}_{selected_sector}_production_leads.csv",
        mime="text/css" if False else "text/csv",
        use_container_width=True
    )
else:
    st.info("Click the button above to start the heavy-duty sector sweep. This will loop through multiple sub-categories and sub-zones automatically.")
