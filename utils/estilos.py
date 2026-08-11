import streamlit as st

def cargar_css():
    st.markdown("""
    <style>
        :root {
            --primary: #1a3a5c;
            --primary-light: #2c5a8a;
            --accent: #e8a317;
            --bg-card: #ffffff;
            --bg-soft: #f4f7fb;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
        }

        .stApp { background-color: #f8fafc; }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a3a5c 0%, #0f2744 100%);
        }
        [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
        [data-testid="stSidebar"] .stRadio label { font-size: 0.93rem; padding: 4px 0; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.2);
            color: #e2e8f0 !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.35);
        }
        [data-testid="stSidebar"] .stNumberInput input {
            background: rgba(255,255,255,0.08) !important;
            color: #f1f5f9 !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
        }

        h1, h2, h3, h4 {
            color: var(--primary) !important;
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
            letter-spacing: -0.02em;
        }

        [data-testid="stMetric"] {
            background: white; border: 1px solid var(--border);
            border-radius: 12px; padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        [data-testid="stMetricLabel"] {
            color: var(--text-muted) !important; font-size: 0.75rem !important;
            text-transform: uppercase; letter-spacing: 0.04em; font-weight: 500 !important;
        }
        [data-testid="stMetricValue"] {
            color: var(--primary) !important; font-weight: 700 !important; font-size: 1.4rem !important;
        }
        [data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

        .stButton > button { border-radius: 8px; font-weight: 600; transition: all 0.15s ease; }
        .stButton > button[kind="primary"] { background: var(--primary); border: none; }
        .stButton > button[kind="primary"]:hover {
            background: var(--primary-light); box-shadow: 0 4px 12px rgba(26,58,92,0.25);
        }

        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
            border-radius: 8px !important; border: 1px solid var(--border) !important;
        }

        hr {
            border: none; height: 1px;
            background: linear-gradient(to right, transparent, #cbd5e1, transparent); margin: 1.4rem 0;
        }

        .stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }

        .module-header {
            background: linear-gradient(135deg, #1a3a5c 0%, #2c5a8a 100%); color: white;
            padding: 14px 24px; border-radius: 10px; font-weight: 600; font-size: 1.12rem;
            letter-spacing: 0.02em; margin-bottom: 1.4rem; box-shadow: 0 4px 12px rgba(26,58,92,0.18);
        }

        .kpi-section-label {
            font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.05em; color: #64748b; margin: 0.8rem 0 0.5rem 0;
        }

        .footer-custom {
            margin-top: 2.5rem; padding: 1.2rem 0.5rem; border-top: 1px solid var(--border);
            font-size: 0.82rem; color: var(--text-muted); font-family: 'Segoe UI', system-ui, sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)