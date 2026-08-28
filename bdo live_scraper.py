import time
import random
import pandas as pd
import requests
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Full Region Lead Generator",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS
st.markdown(
    """
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
        color:
