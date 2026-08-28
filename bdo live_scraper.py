import time
import random
import pandas as pd
import requests
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Full Region Lead Generator", page_icon="📍", layout="wide")

# Simple modern style
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0;}
section[data-testid="stSidebar"] {background: #1e293b; border-right: 1px solid #334155;}
h1, h2, h3 {color: #f8fafc !important;}
div[data-testid="stMetric"] {background: rgba(30,41,59,0.7); border: 1px solid #334155; border-radius: 12px; padding: 16px;}
.stButton > button {background: linear-gradient(90deg, #3b82f6, #06b6d4); color: white; border-radius: 10px; font-weight: 600;}
.stDownloadButton > button {background: linear-gradient(90deg, #10b981, #059669); color: white; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# API Key from secrets
try:
    api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
except:
    st.error("API key not configured. Contact the administrator.")
    st.stop()

# Welcome + Quote
QUOTES = [
    "Success is the sum of small efforts repeated day in and day out.",
    "The only way to do great work is to love what you do.",
    "Don't watch the clock; do what it does. Keep going.",
    "Opportunities don't happen. You create them.",
    "Dream big. Start small. Act now.",
    "Consistency is what transforms average into excellence.",
    "Your future is created by what you do today, not tomorrow.",
    "Push yourself, because no one else is going to do it for you."
]

hour = datetime.now().hour
if 5 <= hour < 12:
    greeting = "Good morning"
elif 12 <= hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

st.markdown(f"### {greeting} 👋 Ready to generate leads?")
st.caption(f"“{random.choice(QUOTES)}”")
st.title("📍 Full Region Business Lead Generator")

# Sidebar
st.sidebar.header("Search Settings")
region = st.sidebar.selectbox("Select Region", ["Kampala", "Wakiso", "Mukono"])
search_query = st.sidebar.text_input("Business Type / Keyword", value="Hardware")
radius = st.sidebar.slider("Search Radius (meters)", 2000, 8000, 5000, 500)

# Grids
REGION_GRIDS = {
    "Kampala": [
        (-0.3476, 32.5825), (-0.3120, 32.5800), (-0.2800, 32.5600),
        (-0.3300, 32.6200), (-0.3000, 32.6500), (-0.3600, 32.6200),
        (-0.3200, 32.5400), (-0.2900, 32.5200), (-0.3500, 32.5400),
        (-0.3800, 32.5800), (-0.4000, 32.5500), (-0.3700, 32.6100),
        (-0.3400, 32.5600), (-0.3100, 32.6000), (-0.3600, 32.5900)
    ],
    "Wakiso": [
        (0.0640, 32.4600), (0.1000, 32.5000), (0.0400, 32.5200),
        (0.0000, 32.4800), (0.0800, 32.4200), (0.1200, 32.4800),
        (0.0500, 32.4000), (0.0200, 32.5500), (-0.0200, 32.5200),
        (0.0900, 32.5500), (0.0300, 32.4500), (0.0700, 32.3800)
    ],
    "Mukono": [
        (0.3530, 32.7550), (0.3200, 32.7200), (0.3800, 32.7800),
        (0.3000, 32.7800), (0.4000, 32.7300), (0.3500, 32.7000),
        (0.2800, 32.7400), (0.3700, 32.8200), (0.3300, 32.8000),
        (0.4100, 32.7600)
    ]
}

# Session state
if "stored_places" not in st.session_state:
    st.session_state.stored_places = []
if "used_points" not in st.session_state:
    st.session_state.used_points = set()
if "last_params" not in st.session_state:
    st.session_state.last_params = ""
if "point_index" not in st.session_state:
    st.session_state.point_index = 0

def fetch_place_details(place_id, key):
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={"place_id": place_id, "fields": "formatted_phone_number,international_phone_number,website", "key": key},
            timeout=8
        )
        data = r.json()
        if data.get("status") == "OK":
            res = data.get("result", {})
            phone = res.get("formatted_phone_number") or res.get("international_phone_number") or "N/A"
            return phone, res.get("website", "N/A")
    except:
        pass
    return "N/A", "N/A"

def nearby_search(lat, lng, keyword, key, radius_m):
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={"location": f"{lat},{lng}", "radius": radius_m, "keyword": keyword, "key": key},
            timeout=12
        )
        data = r.json()
        if data.get("status") == "OK":
            return data.get("results", [])
    except:
        pass
    return []

def process_places(places, region_name, keyword, key):
    results = []
    for p in places:
        pid = p.get("place_id")
        if not pid:
            continue
        phone, website = fetch_place_details(pid, key)
        results.append({
            "Company Name": p.get("name", "N/A"),
            "Region": region_name,
            "Category": keyword.capitalize(),
            "Phone Contact": phone,
            "Website": website,
            "Physical Address": p.get("vicinity", "N/A"),
            "Rating": p.get("rating", "N/A"),
            "Place ID": pid
        })
    return results

# Logic
current_params = f"{region}_{search_query}_{radius}"
if st.session_state.last_params != current_params:
    st.session_state.stored_places = []
    st.session_state.used_points = set()
    st.session_state.point_index = 0
    st.session_state.last_params = current_params

grid = REGION_GRIDS[region]
total_points = len(grid)

# First load (6 points)
if not st.session_state.stored_places and st.session_state.point_index == 0:
    with st.spinner(f"Scanning {region}..."):
        batch = []
        for i in range(min(6, total_points)):
            places = nearby_search(grid[i][0], grid[i][1], search_query, api_key, radius)
            batch.extend(process_places(places, region, search_query, api_key))
            st.session_state.used_points.add(i)
            st.session_state.point_index = i + 1
            time.sleep(1.1)
        if batch:
            df = pd.DataFrame(batch).drop_duplicates(subset=["Place ID"])
            st.session_state.stored_places = df.to_dict("records")

# Show results
if st.session_state.stored_places:
    df = pd.DataFrame(st.session_state.stored_places).drop_duplicates(subset=["Place ID"]).reset_index(drop=True)
    df.insert(0, "No.", range(1, len(df)+1))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Places", len(df))
    c2.metric("Region", region)
    c3.metric("Keyword", search_query.capitalize())
    c4.metric("Points", f"{len(st.session_state.used_points)}/{total_points}")

    st.dataframe(df[["No.", "Company Name", "Phone Contact", "Physical Address", "Rating", "Website"]], use_container_width=True, height=450)

    remaining = total_points - len(st.session_state.used_points)
    if remaining > 0:
        if st.button(f"Load Next Batch ({remaining} left)", type="primary"):
            with st.spinner("Loading more..."):
                new_batch = []
                for i in range(st.session_state.point_index, min(st.session_state.point_index + 3, total_points)):
                    places = nearby_search(grid[i][0], grid[i][1], search_query, api_key, radius)
                    new_batch.extend(process_places(places, region, search_query, api_key))
                    st.session_state.used_points.add(i)
                    time.sleep(1.1)
                st.session_state.point_index += 3
                combined = st.session_state.stored_places + new_batch
                st.session_state.stored_places = pd.DataFrame(combined).drop_duplicates(subset=["Place ID"]).to_dict("records")
                st.rerun()
    else:
        st.success("All points scanned.")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Export to CSV", csv, f"{region}_{search_query}_leads.csv", "text/csv")
else:
    st.warning("No places found yet. Try another keyword or increase radius.")
