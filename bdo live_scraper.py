import time
import random
import pandas as pd
import requests
import streamlit as st
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Full Region Lead Generator",
    page_icon="📍",
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
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    .stDownloadButton > button {
        background: linear-gradient(90deg, #10b981, #059669);
        color: white;
        border-radius: 10px;
        font-weight: 600;
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
        color: #38bdf8;
        margin-bottom: 6px;
    }
    .welcome-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .quote {
        font-style: italic;
        color: #cbd5e1;
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
QUOTES = [
    "Success is the sum of small efforts repeated day in and day out.",
    "The only way to do great work is to love what you do.",
    "Don't watch the clock; do what it does. Keep going.",
    "Opportunities don't happen. You create them.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Dream big. Start small. Act now.",
    "Consistency is what transforms average into excellence.",
    "Your future is created by what you do today, not tomorrow.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones."
]


def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Hello"


quote = random.choice(QUOTES)
greeting = get_greeting()

st.markdown(f"""
<div class="welcome-card">
    <div class="welcome-title">{greeting} 👋 Ready to generate leads?</div>
    <div class="welcome-subtitle">Full coverage across Kampala, Wakiso & Mukono</div>
    <div class="quote">“{quote}”</div>
</div>
""", unsafe_allow_html=True)

st.title("📍 Full Region Business Lead Generator")
st.caption("Grid-based Nearby Search • Complete regional coverage • Deduplicated results")

# ====================== SIDEBAR ======================
st.sidebar.markdown("### ⚙️ Search Settings")

region = st.sidebar.selectbox(
    "Select Region",
    ["Kampala", "Wakiso", "Mukono"]
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

st.sidebar.markdown("---")
st.sidebar.info("Larger radius = better coverage but more duplicates (auto-removed)")

# ====================== REGION GRIDS ======================
REGION_GRIDS = {
    "Kampala": [
        (0.3136, 32.5811),   # Central
        (0.3300, 32.5800),   # Kawempe
        (0.3500, 32.5700),   # Kawempe North
        (0.3200, 32.6200),   # Nakawa
        (0.3400, 32.6400),   # Nakawa / Ntinda
        (0.3000, 32.6100),   # Nakawa South
        (0.3100, 32.5400),   # Lubaga
        (0.3300, 32.5200),   # Lubaga West
        (0.2900, 32.5500),   # Lubaga South
        (0.2800, 32.5800),   # Makindye
        (0.2600, 32.5600),   # Makindye South
        (0.2900, 32.6000),   # Makindye East
        (0.3200, 32.5600),   # Mengo
        (0.3400, 32.6000),   # Kololo / Naguru
        (0.3000, 32.5900),   # Nsambya
    ],
    "Wakiso": [
        (0.0640, 32.4600),   # Wakiso Town / Central
        (0.1000, 32.5000),   # Matugga
        (0.0400, 32.5200),   # Kawempe-Matugga corridor
        (0.0000, 32.4800),   # Nansana
        (0.0800, 32.4200),   # Kakiri
        (0.1200, 32.4800),   # Gombe
        (0.0500, 32.4000),   # Mende
        (0.0200, 32.5500),   # Kira / Namugongo
        (-0.0200, 32.5200),  # Makindye-Ssabagabo / Entebbe Road
        (0.0900, 32.5500),   # Kasangati / Nangabo
        (0.0300, 32.4500),   # Buloba
        (0.0700, 32.3800),   # Ssisa
    ],
    "Mukono": [
        (0.3530, 32.7550),   # Mukono Municipality (Central)
        (0.3200, 32.7200),   # Seeta / Bweyogerere border
        (0.3800, 32.7800),   # Nama
        (0.3000, 32.7800),   # Mukono South / Katosi road
        (0.4000, 32.7300),   # Kyampisi
        (0.3500, 32.7000),   # Goma
        (0.2800, 32.7400),   # Mpatta
        (0.3700, 32.8200),   # Nakisunga
        (0.3300, 32.8000),   # Ntenjeru-Kisoga
        (0.4100, 32.7600),   # Nakifuma
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


# ====================== HELPER FUNCTIONS ======================
def fetch_place_details(place_id, key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,international_phone_number,website,types",  # <--- Add "types" here
        "key": key
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        if data.get("status") == "OK":
            result = data.get("result", {})
            phone = result.get("formatted_phone_number") or result.get("international_phone_number") or "N/A"
            website = result.get("website") or "N/A"

            # <--- Add this block to parse the types into a readable string --->
            raw_types = result.get("types", [])
            filtered_types = [t.replace("_", " ").title() for t in raw_types if
                              t not in ["point_of_interest", "establishment"]]
            business_deals_in = ", ".join(filtered_types) if filtered_types else "N/A"

            return phone, website, business_deals_in  # <--- Return the new variable
    except:
        pass
    return "N/A", "N/A", "N/A"


def nearby_search(lat, lng, keyword, key, radius_m):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "keyword": keyword,
        "key": key
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        data = r.json()
        if data.get("status") == "OK":
            return data.get("results", []), data.get("next_page_token")
        return [], None
    except:
        return [], None


def process_places(places, region_name, keyword, key):
    extracted = []
    for place in places:
        place_id = place.get("place_id")
        if not place_id:
            continue

        # Unpack the 3 values now returned
        phone, website, business_deals_in = fetch_place_details(place_id, key)

        extracted.append({
            "Company Name": place.get("name", "N/A"),
            "Region": region_name,
            "Category": keyword.capitalize(),
            "Business Deals In": business_deals_in,  # <--- Add the new column here
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
            places, _ = nearby_search(lat, lng, search_query, api_key, radius)
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
        df[["No.", "Company Name", "Phone Contact", "Physical Address", "Rating", "Website"]],
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
                    places, _ = nearby_search(lat, lng, search_query, api_key, radius)
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
