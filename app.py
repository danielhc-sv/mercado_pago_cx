import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import calendar
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Mercado Pago CX - Leal Assessoria",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

conn = st.connection("gsheets", type=GSheetsConnection)

def inject_premium_dark_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                font-family: 'Inter', sans-serif;
                background-color: #1e1f22 !important;
                color: #dbdee1 !important;
            }
            [data-testid="stSidebar"] {
                background-color: #111214 !important;
                border-right: none !important;
                padding-top: 10px;
            }
            h1, h2, h3, h4 { 
                color: #f2f3f5 !important; 
                font-weight: 700 !important;
                letter-spacing: -0.3px;
            }
            div[data-testid="stRadio"] [data-testid="stWidgetLabel"] { display: none !important; }
            div[data-testid="stRadio"] > div { flex-direction: column !important; gap: 4px; }
            div[data-testid="stRadio"] label {
                background-color: transparent !important;
                border-radius: 5px !important;
                padding: 10px 14px !important;
                color: #949ba4 !important;
                transition: all 0.15s ease-in-out;
                width: 100%;
                cursor: pointer;
                border: none !important;
            }
            div[data-testid="stRadio"] label:hover { background-color: #35373c !important; color: #dbdee1 !important; }
            div[data-testid="stRadio"] label[data-checked="true"] {
                background-color: #404249 !important;
                color: #ffffff !important;
                font-weight: 600 !important;
            }
            div[data-testid="stRadio"] label [data-testid="stMarker"] { display: none !important; }

            .discord-profile {
                background-color: #111214; border-radius: 12px; overflow: hidden;
                margin-bottom: 25px;
            }
            .discord-banner {
                background: linear-gradient(90deg, #009ee3 0%, #002f6c 100%); height: 100px; width: 100%;
            }
            .discord-avatar-area {
                padding: 0 20px; margin-top: -45px; display: flex; align-items: flex-end;
                justify-content: space-between; margin-bottom: 15px;
            }
            .discord-avatar {
                width: 85px; height: 85px; border-radius: 50%; background-color: #5865f2;
                border: 6px solid #111214; display: flex; align-items: center; justify-content: center;
                font-size: 28px; color: white; font-weight: bold; position: relative;
            }
            .discord-status-online {
                position: absolute; width: 20px; height: 20px; background-color: #23a55a;
                border-radius: 50%; bottom: -2px; right: -2px; border: 4px solid #111214;
            }
            .discord-badge-container { display: flex; gap: 6px; margin-bottom: 5px; }
            .discord-badge {
                background-color: #23a55a; color: white; font-size: 10px; font-weight: bold;
                padding: 3px 8px; border-radius: 4px; text-transform: uppercase;
            }
            .discord-badge-blue { background-color: #009ee3; }
            .discord-badge-purple { background-color: #5865f2; }
            .discord-badge-gold { background-color: #f0b232; color: #111214; }
            .discord-body { padding: 0 20px 20px 20px; }
            
            .cx-metric-card {
                background-color: #2b2d31; border: none !important; border-radius: 8px; padding: 16px; margin-bottom: 15px;
            }
            .cx-label { font-size: 11px; color: #949ba4; font-weight: 600; text-transform: uppercase; }
            .cx-value { font-size: 24px; color: #f2f3f5; font-weight: 700; margin-top: 4px; }
            
            .stTextArea textarea, .stTextInput input, .stSelectbox div, .stNumberInput input, .stDateInput input { 
                background-color: #111214 !important; border: 1px solid #383a40 !important; color: #dbdee1 !important;
            }
            .stButton>button { 
                background-color: #5865f2 !important; color: white !important; border-radius: 4px !important; font-weight: 600 !important; width: 100%;
            }
            .stButton>button:hover { background-color: #4752c4 !important; }
            
            .stTabs [data-baseweb="tab-list"] { background-color: #111214; padding: 4px; border-radius: 6px; border-bottom: none !important; }
            .stTabs [data-baseweb="tab"] { color: #949ba4 !important; }
            .
