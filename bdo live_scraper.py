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
        background: linear-gradient(
