import time
import pandas as pd
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Live Maps BDO Lead Generator", page_icon="📍", layout="wide"
)

st.title("📍 Live Google Maps Business Lead Generator")
st.markdown(
    "Query real-time business and institutional listings dynamically using the"
    " Places API."
)

# Sidebar parameters
st.sidebar.header("API & Search Parameters")

api_key = st.sidebar.text_input(
    "Google Maps API Key",
    type="password",
    help="Enter your Google Cloud Places API key here.",
)

region = st.sidebar.selectbox(
    "Select Location Zone / Sub-Division",
    [
        "Kampala Central",
        "Nakawa Division",
        "Kawempe Division",
        "Rubaga Division",
        "Makindye Division",
        "Wakiso",
        "Mukono",
    ],
)

search_query = st.sidebar.text_input(
    "Enter Business Type / Keyword",
    value="Hardware",
    help="Type any category (e.g., School, Hardware, Pharmacy, Supermarket)",
)

# Initialize Session State to manage manual page fetching without wiping data
if "stored_places" not in st.session_state:
  st.session_state.stored_places = []
if "next_token" not in st.session_state:
  st.session_state.next_token = None
if "last_query_params" not in st.session_state:
  st.session_state.last_query_params = ""


def fetch_place_details(place_id, key):
  details_url = "https://maps.googleapis.com/maps/api/place/details/json"
  params = {
      "place_id": place_id,
      "fields": "formatted_phone_number,website,international_phone_number",
      "key": key,
  }
  try:
    response = requests.get(details_url, params=params, timeout=5)
    data = response.json()
    if data.get("status") == "OK":
      result = data.get("result", {})
      return result.get(
          "formatted_phone_number",
          result.get("international_phone_number", "N/A"),
      ), result.get("website", "N/A")
  except Exception:
    pass
  return "N/A", "N/A"


def fetch_batch(target_region, query_term, key, page_token=None):
  url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

  if page_token:
    params = {"pagetoken": page_token, "key": key}
    time.sleep(3)  # Google token activation delay
  else:
    full_query = f"{query_term} in {target_region}, Uganda"
    params = {"query": full_query, "key": key}

  try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    status = data.get("status")
    if status == "OK":
      places = data.get("results", [])
      new_token = data.get("next_page_token", None)
      extracted = []

      for place in places:
        place_id = place.get("place_id")
        phone, website = "N/A", "N/A"
        if place_id:
          phone, website = fetch_place_details(place_id, key)

        extracted.append({
            "Company Name": place.get("name", "N/A"),
            "Region": target_region,
            "Category": query_term.capitalize(),
            "Phone Contact": phone,
            "Website": website,
            "Physical Address": place.get("formatted_address", target_region),
            "Rating": place.get("rating", "N/A"),
        })
      return extracted, new_token
    else:
      return [], None
  except Exception as e:
    st.error(f"Connection error: {e}")
    return [], None


# Check if API Key is provided
if api_key:
  current_params_key = f"{region}_{search_query}"

  # Reset state if user changes location or keyword
  if st.session_state.last_query_params != current_params_key:
    st.session_state.stored_places = []
    st.session_state.next_token = None
    st.session_state.last_query_params = current_params_key

    # Fetch initial first batch (Page 1)
    with st.spinner(f"Fetching initial results for '{search_query}'..."):
      batch, token = fetch_batch(region, search_query, api_key)
      st.session_state.stored_places.extend(batch)
      st.session_state.next_token = token

  # Display current dataset in table
  if st.session_state.stored_places:
    df_results = pd.DataFrame(st.session_state.stored_places)
    # Drop potential duplicates just in case
    df_results = df_results.drop_duplicates(subset=["Company Name"]).reset_index(
        drop=True
    )
    df_results.insert(0, "No.", range(1, len(df_results) + 1))

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Places Loaded", len(df_results))
    col2.metric("Target Zone", region)
    col3.metric("Keyword", search_query.capitalize())

    st.markdown("---")
    st.subheader(
        f"📋 Live Map Results for: '{search_query.capitalize()}' in {region}"
    )

    st.dataframe(df_results, use_container_width=True)

    # Manual Pagination / Refresh Button
    if st.session_state.next_token:
      if st.button("🔄 Load Next 20 Places"):
        with st.spinner("Fetching next batch from Google Maps..."):
          batch, token = fetch_batch(
              region, search_query, api_key, st.session_state.next_token
          )
          if batch:
            st.session_state.stored_places.extend(batch)
            st.session_state.next_token = token
            st.rerun()
          else:
            st.warning("No more extra listings available for this query.")
    else:
      st.info(
          "✨ You've reached Google's maximum page limit for this search term."
          " Try changing your keyword or sub-division slightly to fetch more!"
      )

    st.markdown("---")
    csv_data = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Cumulative Leads to CSV",
        data=csv_data,
        file_name=f"google_places_{region}_{search_query}.csv",
        mime="text/csv",
    )
  else:
    st.warning("No records returned for these search parameters.")
else:
  st.info(
      "👈 Please enter your **Google Maps API Key** in the sidebar to begin"
      " fetching live data."
  )
