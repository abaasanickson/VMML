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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Matte Obsidian Luxury Dark Theme */
    .stApp {
        background: #09090b;
        color: #f4f4f5;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #0d0d11;
        border-right: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    /* Typography & Spacing */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.035em;
        font-weight: 700;
    }

    /* Luxury Cards / Metrics */
    div[data-testid="stMetric"] {
        background: rgba(24, 24, 27, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }
    div[data-testid="stMetric"] label {
        color: #71717a !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1.7rem !important;
    }

    /* Minimalist Obsidian Action Buttons - Matching the clean typographic aesthetic */
    .stButton > button {
        background: #18181b;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #27272a;
        border-color: rgba(255, 255, 255, 0.25);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }

    /* Download Button - Styled to match the same clean minimalist button structure */
    .stDownloadButton > button {
        background: #18181b;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover {
        background: #27272a;
        border-color: rgba(255, 255, 255, 0.25);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }

    /* Welcome Banner */
    .welcome-card {
        background: rgba(18, 18, 23, 0.7);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6);
    }
    .welcome-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.025em;
        margin-bottom: 6px;
    }
    .welcome-subtitle {
        color: #a1a1aa;
        font-size: 0.95rem;
        margin-bottom: 14px;
        font-weight: 400;
    }
    .quote {
        font-style: italic;
        color: #d4d4d8;
        border-left: 2px solid #52525b;
        padding-left: 14px;
        margin-top: 14px;
        font-size: 0.9rem;
        background: transparent;
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


from datetime import datetime, timezone, timedelta

def get_greeting():
    # Define EAT (East Africa Time) which is UTC+3
    eat_timezone = timezone(timedelta(hours=3))
    hour = datetime.now(eat_timezone).hour
    
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
    ["Kampala", "Wakiso", "Mukono", "Western Uganda","Masaka","Jinja"]
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
    ],
    "Western Uganda": [
        (-0.6053, 30.6552),  # Mbarara City (Central)
        (-0.6200, 30.6400),  # Mbarara - Kakoba / Nyamitanga
        (0.6725, 30.2917),   # Fort Portal City (Kabarole)
        (-1.2486, 29.9888),  # Kabale Town
        (-0.2756, 30.2744),  # Bushenyi / Ishaka
        (0.4423, 30.3547),   # Kasese Town
        (-0.9942, 30.2281),  # Ntungamo
        (-0.8353, 30.4078),  # Rukungiri
        (0.1287, 31.0531),   # Hoima City (Bunyoro)
        (1.0264, 30.5516),   # Masindi
    ],
    "Masaka": [
        (-0.3476, 31.7356),  # Masaka City (Central)
        (-0.3300, 31.7200),  # Nyendo
        (-0.3600, 31.7500),  # Kimanya / Kitubulu
        (-0.3150, 31.7000),  # Buwunga
        (-0.3800, 31.7800),  # Mukungwe
        (-0.3000, 31.7600),  # Kyanamukaka
        (-0.3500, 31.6800),  # Villa Maria / Bukoto
        (-0.2800, 31.8100),  # Masaka Rural / Kalungu border
    ],
    "Jinja": [
        (0.4479, 33.2026),   # Jinja City (Central / CBD)
        (0.4300, 33.1800),   # Walukuba / Masese
        (0.4650, 33.2200),   # Bugembe / Kimaka
        (0.4200, 33.2200),   # Danida / Nile Crescent
        (0.4800, 33.2500),   # Kakira
        (0.4100, 33.1500),   # Buwenge Road corridor
        (0.4500, 33.2800),   # Busedde
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
        df[["No.", "Company Name","Business Deals In", "Phone Contact", "Physical Address", "Rating", "Website"]],
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
