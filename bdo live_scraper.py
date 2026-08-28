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


def fetch_place_details(place_id, key):
  """Fetches extra details like phone number and website using Place Details API."""
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


def fetch_google_places(target_region, query_term, key):
  if not key:
    return None  # Prompt user for key if missing

  url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
  full_query = f"{query_term} in {target_region}, Uganda"

  params = {"query": full_query, "key": key}
  extracted = []
  max_pages = 3  # Fetches up to 3 pages (~60 results total)

  try:
    for page in range(max_pages):
      response = requests.get(url, params=params, timeout=10)
      data = response.json()

      status = data.get("status")
      if status == "OK":
        places = data.get("results", [])

        for place in places:
          place_id = place.get("place_id")
          # Fetch phone number & website dynamically for each place
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

        # Check for next page token
        next_page_token = data.get("next_page_token")
        if next_page_token and page < max_pages - 1:
          # Google requires a short delay before the next_page_token becomes active
          time.sleep(2)
          params = {"pagetoken": next_page_token, "key": key}
        else:
          break
      else:
        if not extracted:
          st.warning(
              f"API Response Status: {status} - Check your API key or query"
              " quota."
          )
        break

    if extracted:
      df = pd.DataFrame(extracted)
      df.insert(0, "No.", range(1, len(df) + 1))
      return df
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
