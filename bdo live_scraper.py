import time
import re
import hashlib
from urllib.parse import quote_plus
import pandas as pd
import requests
import streamlit as st

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="Uganda Tri-Engine Business Harvester", layout="wide")

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

st.title("Uganda Tri-Engine National Harvester")
st.caption("Maximum Volume • OpenStreetMap + Directory Matrix + Headless Maps Infinite Scroll")

# ====================== MATRIX CONFIG ======================
SECTOR_MATRIX = {
    "hardware": {
        "osm": ["shop=hardware", "shop=doityourself", "shop=building_supplies"],
        "keywords": ["hardware store", "cement distributor", "building materials shop", "tools supplier"]
    },
    "pharmacy": {
        "osm": ["amenity=pharmacy", "shop=medical_supply", "amenity=clinic"],
        "keywords": ["pharmacy", "drug shop", "medical clinic", "medical laboratory"]
    },
    "supermarket": {
        "osm": ["shop=supermarket", "shop=convenience", "shop=wholesale"],
        "keywords": ["supermarket", "grocery store", "mini market", "wholesale shop"]
    },
    "school": {
        "osm": ["amenity=school", "amenity=kindergarten", "amenity=college"],
        "keywords": ["primary school", "secondary school", "nursery school", "training center"]
    },
    "restaurant": {
        "osm": ["amenity=restaurant", "amenity=cafe", "amenity=fast_food"],
        "keywords": ["restaurant", "cafe", "hotel", "fast food", "bar and grill"]
    },
    "automotive": {
        "osm": ["shop=car_repair", "shop=tyres", "shop=car_parts"],
        "keywords": ["spare parts", "auto garage", "car dealer", "mechanic", "tyre center"]
    }
}

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
        {"name": "Entebbe Corridor", "box": "(0.05, 32.45, 0.25, 32.55)"}
    ],
    "Jinja": [{"name": "Jinja Municipality", "box": "(0.40, 33.18, 0.47, 33.25)"}],
    "Mbarara": [{"name": "Mbarara City", "box": "(-0.62, 30.63, -0.58, 30.68)"}],
    "Gulu": [{"name": "Gulu City Center", "box": "(2.75, 32.28, 2.80, 32.33)"}],
    "Mbale": [{"name": "Mbale Municipality", "box": "(1.05, 34.15, 1.12, 34.22)"}]
}

# ====================== SIDEBAR CONTROLS ======================
st.sidebar.markdown("### ⚙️ Harvester Configuration")
region = st.sidebar.selectbox("Select Region / Hub", list(REGION_BOXES.keys()))
selected_sector = st.sidebar.selectbox("Select Business Sector", list(SECTOR_MATRIX.keys()))
max_scrolls = st.sidebar.slider("Maps Scroll Depth", 1, 8, 3)

# ====================== CLEANING & FILTERING ======================
GARBAGE_TERMS = {
    "add listing", "sign in", "log in", "login", "explore categories", 
    "download our app", "explore website", "contact", "privacy policy", 
    "blog", "about us", "events", "explore locations", "home", "register",
    "terms of use", "faq", "sitemap", "all categories", "unnamed"
}

def clean_text(val):
    if not val:
        return "N/A"
    return re.sub(r"\s+", " ", str(val)).strip()

def is_valid_name(name):
    cleaned = clean_text(name).lower()
    if not cleaned or len(cleaned) < 2 or len(cleaned) > 120:
        return False
    if cleaned in GARBAGE_TERMS:
        return False
    if any(p in cleaned for p in ["download", "sign up", "click here", "read more", "all rights"]):
        return False
    return True

def make_id(source, name, address=""):
    raw = f"{source}|{clean_text(name).lower()}|{clean_text(address).lower()}"
    return "tri_" + hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()[:24]

# ====================== ENGINE 1: OSM STRUCTURAL GRID ======================
def run_engine_osm(region_name, sector_key):
    sub_grids = REGION_BOXES.get(region_name, [])
    tags = SECTOR_MATRIX[sector_key]["osm"]
    overpass_url = "https://overpass-api.de/api/interpreter"
    records = []
    session = requests.Session()
    session.headers.update({"User-Agent": "UgandaTriEngine/3.0"})

    for grid in sub_grids:
        bbox = grid["box"]
        for tag_pair in tags:
            key, val = tag_pair.split("=")
            query = f"""
            [out:json][timeout:30];
            (
              node["{key}"="{val}"]{bbox};
              way["{key}"="{val}"]{bbox};
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
                        td = el.get("tags", {})
                        name = td.get("name")
                        if not is_valid_name(name):
                            continue
                        address = ", ".join(filter(None, [td.get("addr:street"), grid["name"], region_name]))
                        phone = td.get("phone", td.get("contact:phone", "N/A"))
                        website = td.get("website", td.get("contact:website", "N/A"))
                        cat = td.get("shop", td.get("amenity", sector_key))

                        records.append({
                            "Company Name": clean_text(name),
                            "Region": region_name,
                            "Sub-Zone": grid["name"],
                            "Sector Category": clean_text(cat).replace("_", " ").title(),
                            "Phone Contact": clean_text(phone),
                            "Website": clean_text(website),
                            "Physical Address": clean_text(address),
                            "Place ID": make_id("OSM", name, address),
                            "Data Source": "OpenStreetMap Structural DB"
                        })
                time.sleep(0.5)
            except Exception:
                continue
    return records

# ====================== ENGINE 2: DIRECTORY MATRIX ======================
def run_engine_directories(region_name, sector_key):
    keywords = SECTOR_MATRIX[sector_key]["keywords"]
    records = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    for kw in keywords:
        urls = [
            f"https://www.yellowpages-uganda.com/search?q={quote_plus(kw)}",
            f"https://www.businesslist.co.ug/search?q={quote_plus(kw)}"
        ]
        for url in urls:
            try:
                res = session.get(url, timeout=10)
                if res.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(res.text, "html.parser")
                    for heading in soup.find_all(["h2", "h3", "h4"]):
                        name = clean_text(heading.get_text(" ", strip=True))
                        if not is_valid_name(name):
                            continue
                        parent = heading.parent
                        block = clean_text(parent.get_text(" ", strip=True)) if parent else name
                        phones = re.findall(r"(?:\+?256|0)[\d\s().\-/]{7,}", block)
                        phone = phones[0] if phones else "N/A"

                        records.append({
                            "Company Name": name,
                            "Region": region_name,
                            "Sub-Zone": region_name,
                            "Sector Category": kw.title(),
                            "Phone Contact": clean_text(phone),
                            "Website": "N/A",
                            "Physical Address": region_name,
                            "Place ID": make_id("Directory", name),
                            "Data Source": "Public Directory Matrix"
                        })
                time.sleep(0.5)
            except Exception:
                continue
    return records

# ====================== ENGINE 3: PLAYWRIGHT INFINITE SCROLL ======================
def run_engine_maps(region_name, sector_key, depth):
    keywords = SECTOR_MATRIX[sector_key]["keywords"]
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
                    page.goto(search_url, timeout=30000)
                    page.wait_for_timeout(2000)
                    
                    sidebar_selector = 'div[role="feed"]'
                    try:
                        page.wait_for_selector(sidebar_selector, timeout=6000)
                        for _ in range(depth):
                            page.evaluate(f"const el = document.querySelector('{sidebar_selector}'); if(el) el.scrollTop = el.scrollHeight;")
                            page.wait_for_timeout(2000)
                    except Exception:
                        pass
                    
                    listings = page.locator('div.Nv2PK').all()
                    for item in listings:
                        try:
                            lines = item.inner_text().split("\n")
                            name = lines[0] if len(lines) > 0 else ""
                            if not is_valid_name(name):
                                continue
                            full_text = " ".join(lines)
                            phones = re.findall(r"(?:\+?256|0)[\d\s().\-/]{7,}", full_text)
                            phone = phones[0] if phones else "N/A"

                            records.append({
                                "Company Name": clean_text(name),
                                "Region": region_name,
                                "Sub-Zone": region_name,
                                "Sector Category": kw.title(),
                                "Phone Contact": clean_text(phone),
                                "Website": "N/A",
                                "Physical Address": region_name,
                                "Place ID": make_id("Maps", name),
                                "Data Source": "Google Maps Infinite Scroll"
                            })
                        except Exception:
                            continue
                except Exception:
                    continue
            browser.close()
    except Exception:
        pass
    return records

# ====================== STATE CONTROLLER ======================
if "tri_leads" not in st.session_state:
    st.session_state.tri_leads = []
if "tri_config" not in st.session_state:
    st.session_state.tri_config = ""

current_config = f"{region}|{selected_sector}"
if st.session_state.tri_config != current_config:
    st.session_state.tri_leads = []
    st.session_state.tri_config = current_config

st.subheader(f"Active Multi-Engine Target: {selected_sector.upper()} in {region}")

if st.button("🚀 Launch Tri-Engine National Harvest", use_container_width=True):
    with st.spinner("Executing simultaneous multi-source data sweep across OSM, Directories, and Maps..."):
        master_collection = []
        
        # Engine 1: OSM
        master_collection.extend(run_engine_osm(region, selected_sector))
        # Engine 2: Directories
        master_collection.extend(run_engine_directories(region, selected_sector))
        # Engine 3: Maps Infinite Scroll
        master_collection.extend(run_engine_maps(region, selected_sector, max_scrolls))
        
        if master_collection:
            df_m = pd.DataFrame(master_collection)
            df_m = df_m.drop_duplicates(subset=["Place ID"])
            st.session_state.tri_leads = df_m.to_dict("records")
        else:
            st.session_state.tri_leads = []

if st.session_state.tri_leads:
    df_final = pd.DataFrame(st.session_state.tri_leads)
    df_final.insert(0, "No.", range(1, len(df_final) + 1))
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Unique Businesses", len(df_final))
    c2.metric("Region", region)
    c3.metric("Sector", selected_sector.capitalize())
    c4.metric("Engines Active", "3 Combined")

    st.markdown("---")
    st.dataframe(
        df_final[["No.", "Company Name", "Sector Category", "Phone Contact", "Physical Address", "Data Source"]],
        use_container_width=True,
        height=500
    )

    st.markdown("---")
    csv_data = df_final.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Combined Tri-Engine Database (CSV)",
        data=csv_data,
        file_name=f"Uganda_{region}_{selected_sector}_tri_engine_leads.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("Click the button above to run all three scraping engines simultaneously to pull maximum volume.")
