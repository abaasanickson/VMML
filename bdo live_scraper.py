import time
import pandas as pd
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Live Maps BDO Lead Generator", page_icon="📍", layout="wide"
)

# Custom Modern CSS Styling (Dark Theme & Glassmorphism UI)
st.markdown(
    """
    <style>
        .main {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stTextInput input, .stSelectbox select {
            background-color: #161b22;
            color: white;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        .metric-card {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            border: 1px solid #374151;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #38bdf8;
        }
        .metric-label {
            font-size: 14px;
            color: #9ca3af;
            margin-top: 5px;
        }
        .lead-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            padding: 16px;
            border-radius: 10px;
            margin-bottom: 12px;
            transition: transform 0.2s ease;
        }
        .lead-card:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }
        .company-title {
            font-size: 18px;
            font-weight: 600;
            color: #f3f4f6;
        }
        .badge {
            background-color: #0369a1;
            color: #e0f2fe;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
    </style>
""",
    unsafe_allow_html=True,
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

# Expanded micro-zones to pull more comprehensive coverage across Kampala & surroundings
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


def fetch_google_places(target_region, query_term, key):
  if not key:
    return None

  url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
  full_query = f"{query_term} in {target_region}, Uganda"

  params = {"query": full_query, "key": key}
  extracted = []
  max_pages = 3  # Fetches up to 3 pages (~60 results total per sub-zone)

  try:
    for page in range(max_pages):
      response = requests.get(url, params=params, timeout=10)
      data = response.json()

      status = data.get("status")
      if status == "OK":
        places = data.get("results", [])

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

        next_page_token = data.get("next_page_token")
        if next_page_token and page < max_pages - 1:
          time.sleep(3)
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
  with st.spinner(
      f"Fetching live results for '{search_query}' in {region}..."
  ):
    df_results = fetch_google_places(region, search_query, api_key)

  if df_results is not None and not df_results.empty:
    # Modern Metric Layout using columns
    c1, c2, c3 = st.columns(3)
    with c1:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div class="metric-value">{len(df_results)}</div>
                    <div class="metric-label">Live Places Found</div>
                </div>
            """,
          unsafe_allow_html=True,
      )
    with c2:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div class="metric-value">{region}</div>
                    <div class="metric-label">Target Zone</div>
                </div>
            """,
          unsafe_allow_html=True,
      )
    with c3:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div class="metric-value">{search_query.capitalize()}</div>
                    <div class="metric-label">Search Keyword</div>
                </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")
    st.subheader(
        f"📋 Live Map Results for: '{search_query.capitalize()}' in {region}"
    )

    # Render results in clean UI cards alongside the dataframe
    for _, row in df_results.iterrows():
      website_display = (
          f"<a href='{row['Website']}' target='_blank'>Visit Website</a>"
          if row["Website"] != "N/A"
          else "No Website"
      )
      st.markdown(
          f"""
            <div class="lead-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="company-title">{row['No.']}. {row['Company Name']}</span>
                    <span class="badge">⭐ {row['Rating']}</span>
                </div>
                <p style="color: #9ca3af; margin: 8px 0 4px 0; font-size: 14px;">📍 {row['Physical Address']}</p>
                <p style="margin: 0; font-size: 14px;">📞 <b>Phone:</b> {row['Phone Contact']} &nbsp;|&nbsp; 🌐 <b>Web:</b> {website_display}</p>
            </div>
        """,
          unsafe_allow_html=True,
      )

    st.markdown("---")
    # Export button
    csv_data = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Cleaned Lead List to CSV",
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
