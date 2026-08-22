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

# Optional input for your Google Places API Key
api_key = st.sidebar.text_input(
    "Google Maps API Key",
    type="password",
    help="Enter your Google Cloud Places API key here.",
)

region = st.sidebar.selectbox(
    "Select Location Zone", ["Kampala", "Wakiso", "Mukono"]
)

search_query = st.sidebar.text_input(
    "Enter Business Type / Keyword",
    value="School",
    help="Type any category (e.g., School, Hardware, Pharmacy, Supermarket)",
)


def fetch_google_places(target_region, query_term, key):
  if not key:
    return None  # Prompt user for key if missing

  url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
  full_query = f"{query_term} in {target_region}, Uganda"

  params = {"query": full_query, "key": key}

  try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if data.get("status") == "OK":
      places = data.get("results", [])
      extracted = []

      for idx, place in enumerate(places, start=1):
        extracted.append({
            "No.": idx,
            "Company Name": place.get("name", "N/A"),
            "Region": target_region,
            "Category": query_term.capitalize(),
            "Phone Contact": "Available via Place Details",
            "Physical Address": place.get("formatted_address", target_region),
            "Rating": place.get("rating", "N/A"),
        })
      return pd.DataFrame(extracted)
    else:
      st.warning(
          f"API Response Status: {data.get('status')} - Check your API key or"
          " query quota."
      )
      return pd.DataFrame()
  except Exception as e:
    st.error(f"Connection error: {e}")
    return pd.DataFrame()


# Check if API Key is provided
if api_key:
  with st.spinner(f"Fetching live results for '{search_query}' in {region}..."):
    df_results = fetch_google_places(region, search_query, api_key)

  if df_results is not None and not df_results.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Places Found", len(df_results))
    col2.metric("Target Zone", region)
    col3.metric("Keyword", search_query.capitalize())

    st.markdown("---")
    st.subheader(
        f"📋 Live Map Results for: '{search_query.capitalize()}' in {region}"
    )
    st.dataframe(df_results, use_container_width=True)

    # Export button
    csv_data = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Live Map Leads to CSV",
        data=csv_data,
        file_name=f"google_places_{region}_{search_query}.csv",
        mime="text/csv",
    )
  else:
    st.info("No records returned or waiting for valid search query parameters.")
else:
  st.info(
      "👈 Please enter your **Google Maps API Key** in the sidebar to begin"
      " fetching live data."
  )
