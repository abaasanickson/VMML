import time
import math
import pandas as pd
import requests
import streamlit as st

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Full Region Lead Generator",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Full Region Business Lead Generator")
st.markdown("Scrape **all** businesses across Kampala, Wakiso & Mukono using grid-based Nearby Search.")

# ====================== SIDEBAR ======================
st.sidebar.header("Search Settings")

api_key = st.sidebar.text_input(
    "Google Maps API Key",
    type="password",
    help="Enable Places API (New or legacy) in Google Cloud"
)

region = st.sidebar.selectbox(
    "Select Region",
    ["Kampala", "Wakiso", "Mukono"]
)

search_query = st.sidebar.text_input(
    "Business Type / Keyword",
    value="Hardware",
    help="e.g. School, Hardware, Pharmacy, Supermarket, Clinic"
)

radius = st.sidebar.slider("Search Radius per point (meters)", 2000, 8000, 4500, 500)

# ====================== REGION GRIDS ======================
# These points cover the whole region (not just near Masooli)
REGION_GRIDS = {
    "Kampala": [
        (-0.3476, 32.5825),   # Central
        (-0.3120, 32.5800),   # Kawempe
        (-0.2800, 32.5600),   # Kawempe North
        (-0.3300, 32.6200),   # Nakawa
        (-0.3000, 32.6500),   # Nakawa East
        (-0.3600, 32.6200),   # Nakawa South
        (-0.3200, 32.5400),   # Lubaga
        (-0.2900, 32.5200),   # Lubaga West
        (-0.3500, 32.5400),   # Lubaga South
        (-0.3800, 32.5800),   # Makindye
        (-0.4000, 32.5500),   # Makindye South
        (-0.3700, 32.6100),   # Makindye East
        (-0.3400, 32.5600),   # Mengo / Old Kampala
        (-0.3100, 32.6000),   # Ntinda / Naguru
        (-0.3600, 32.5900),   # Nsambya
    ],
    "Wakiso": [
        (0.0640, 32.4600),    # Wakiso Town
        (0.1000, 32.5000),    # Kasangati / Masooli area
        (0.0400, 32.5200),    # Nansana
        (0.0000, 32.4800),    # Matugga
        (0.0800, 32.4200),    # Kakiri
        (0.1200, 32.4800),    # Gayaza
        (0.0500, 32.4000),    # Busukuma
        (0.0200, 32.5500),    # Kira / Namugongo
        (-0.0200, 32.5200),   # Bweyogerere
        (0.0900, 32.5500),    # Kasangati East
        (0.0300, 32.4500),    # Gombe
        (0.0700, 32.3800),    # Kakiri West
    ],
    "Mukono": [
        (0.3530, 32.7550),    # Mukono Town
        (0.3200, 32.7200),    # Seeta
        (0.3800, 32.7800),    # Nakifuma
        (0.3000, 32.7800),    # Nama
        (0.4000, 32.7300),    # Ntunda
        (0.3500, 32.7000),    # Kyampisi
        (0.2800, 32.7400),    # Goma
        (0.3700, 32.8200),    # Ntenjeru
        (0.3300, 32.8000),    # Nakisunga
        (0.4100, 32.7600),    # Kasawo direction
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
        "fields": "formatted_phone_number,international_phone_number,website",
        "key": key
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        if data.get("status") == "OK":
            result = data.get("result", {})
            phone = result.get("formatted_phone_number") or result.get("international_phone_number") or "N/A"
            website = result.get("website") or "N/A"
            return phone, website
    except:
        pass
    return "N/A", "N/A"


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
        status = data.get("status")

        if status == "OK":
            return data.get("results", []), data.get("next_page_token")
        elif status == "ZERO_RESULTS":
            return [], None
        else:
            st.warning(f"API status: {status}")
            return [], None
    except Exception as e:
        st.error(f"Request error: {e}")
        return [], None


def process_places(places, region_name, keyword, key):
    extracted = []
    for place in places:
        place_id = place.get("place_id")
        if not place_id:
            continue

        phone, website = fetch_place_details(place_id, key)

        extracted.append({
            "Company Name": place.get("name", "N/A"),
            "Region": region_name,
            "Category": keyword.capitalize(),
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
if not api_key:
    st.info("👈 Enter your Google Maps API Key in the sidebar to start.")
    st.stop()

current_params = f"{region}_{search_query}_{radius}"

# Reset when user changes region / keyword / radius
if st.session_state.last_params != current_params:
    st.session_state.stored_places = []
    st.session_state.used_points = set()
    st.session_state.point_index = 0
    st.session_state.last_params = current_params

grid = REGION_GRIDS[region]
total_points = len(grid)

# ===== FIRST LOAD =====
if len(st.session_state.stored_places) == 0 and st.session_state.point_index == 0:
    with st.spinner(f"Scanning first points in {region}..."):
        batch = []
        # Load first 3 points automatically
        for i in range(min(3, total_points)):
            lat, lng = grid[i]
            places, _ = nearby_search(lat, lng, search_query, api_key, radius)
            batch.extend(process_places(places, region, search_query, api_key))
            st.session_state.used_points.add(i)
            st.session_state.point_index = i + 1
            time.sleep(1.2)  # be gentle with the API

        # Remove duplicates
        df_temp = pd.DataFrame(batch)
        if not df_temp.empty:
            df_temp = df_temp.drop_duplicates(subset=["Place ID"])
            st.session_state.stored_places = df_temp.to_dict("records")

# ===== DISPLAY RESULTS =====
if st.session_state.stored_places:
    df = pd.DataFrame(st.session_state.stored_places)
    df = df.drop_duplicates(subset=["Place ID"]).reset_index(drop=True)
    df.insert(0, "No.", range(1, len(df) + 1))

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Unique Places", len(df))
    col2.metric("Region", region)
    col3.metric("Keyword", search_query.capitalize())
    col4.metric("Points Used", f"{len(st.session_state.used_points)} / {total_points}")

    st.markdown("---")
    st.subheader(f"Results for “{search_query}” in {region}")

    st.dataframe(
        df[["No.", "Company Name", "Phone Contact", "Physical Address", "Rating", "Website"]],
        use_container_width=True,
        height=450
    )

    # ===== LOAD NEXT BATCH BUTTON =====
    remaining = total_points - len(st.session_state.used_points)

    if remaining > 0:
        if st.button(f"🔄 Load Next Batch ({remaining} points left)", type="primary"):
            with st.spinner("Fetching next batch of places..."):
                new_batch = []
                points_to_load = min(3, remaining)  # load 3 points per click

                for i in range(st.session_state.point_index, st.session_state.point_index + points_to_load):
                    if i >= total_points:
                        break
                    lat, lng = grid[i]
                    places, _ = nearby_search(lat, lng, search_query, api_key, radius)
                    new_batch.extend(process_places(places, region, search_query, api_key))
                    st.session_state.used_points.add(i)
                    time.sleep(1.2)

                st.session_state.point_index += points_to_load

                # Merge & deduplicate
                combined = st.session_state.stored_places + new_batch
                df_combined = pd.DataFrame(combined).drop_duplicates(subset=["Place ID"])
                st.session_state.stored_places = df_combined.to_dict("records")

                st.rerun()
    else:
        st.success("✅ All grid points in this region have been scanned.")

    # ===== EXPORT =====
    st.markdown("---")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export All Leads to CSV",
        data=csv,
        file_name=f"{region}_{search_query}_leads.csv",
        mime="text/csv"
    )

else:
    st.warning("No places found yet. Try a different keyword or increase the radius.")
