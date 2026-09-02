import streamlit as st

def cargar_css():
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════
       VARIABLES GLOBALES (Paleta Corporativa con #fa7d2a)
    ═══════════════════════════════════════════════════════ */
    :root {
        --primary:        #1a3a5c;
        --primary-light:  #2c5a8a;
        --accent:         #fa7d2a;
        --accent-hover:   #e66b1a;
        --accent-dim:     rgba(250, 125, 42, 0.15);
        --bg-main:        #f0f4f8;
        --bg-card:        #ffffff;
        --bg-soft:        #f8fafc;
        --text-main:      #1e293b;
        --text-muted:     #64748b;
        --border:         #e2e8f0;
        --success:        #16a34a;
        --warning:        #fa7d2a;
        --danger:         #dc2626;
        --nav-dark:       #0f2744;
        --nav-darker:     #0a1f38;
    }

    /* ═══════════════════════════════════════════════════════
       OCULTAR CHROME NATIVO DE STREAMLIT
    ═══════════════════════════════════════════════════════ */
    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }
    /* Ocultar sidebar por completo (modo pantalla completa) */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ═══════════════════════════════════════════════════════
       LAYOUT BASE
    ═══════════════════════════════════════════════════════ */
    .stApp { background-color: var(--bg-main); }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 2rem !important;
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        max-width: 100% !important;
    }

    /* ═══════════════════════════════════════════════════════
       ERP TOPBAR (BANNER INSTITUCIONAL)
    ═══════════════════════════════════════════════════════ */
    .erp-topbar {
        background: linear-gradient(135deg, var(--primary) 0%, var(--nav-darker) 100%);
        padding: 0 1.8rem;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0 -1.8rem 1rem -1.8rem;
        border-bottom: 3px solid var(--accent);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
    }
    .erp-topbar-left {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }
    .erp-logo        { height: 38px; }
    .erp-logo-text   { font-weight: 800; font-size: 1.45rem; color: var(--accent); letter-spacing: 0.06em; }
    .erp-topbar-info { display: flex; flex-direction: column; line-height: 1.2; }
    .erp-topbar-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.01em;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .erp-topbar-sub {
        color: #94a3b8;
        font-size: 0.65rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .erp-topbar-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .erp-user-badge {
        background: var(--accent-dim);
        border: 1px solid rgba(250, 125, 42, 0.45);
        color: var(--accent) !important;
        padding: 0.35rem 0.95rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .erp-version {
        color: #64748b;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        font-weight: 600;
    }

    /* ═══════════════════════════════════════════════════════
       BOTONES DE NAVEGACIÓN ERP (ÁREAS PRINCIPALES)
    ═══════════════════════════════════════════════════════ */
    /* Botón Activo (Seleccionado) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #fa7d2a 0%, #e66b1a 100%) !important;
        border: 1px solid #fa7d2a !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
        box-shadow: 0 3px 12px rgba(250, 125, 42, 0.38) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #e66b1a 0%, #d45f12 100%) !important;
        border-color: #d45f12 !important;
        box-shadow: 0 4px 16px rgba(250, 125, 42, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Botón Inactivo */
    .stButton > button[kind="secondary"] {
        background: #1a3a5c !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(250, 125, 42, 0.15) !important;
        border-color: #fa7d2a !important;
        color: #fa7d2a !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12) !important;
        transform: translateY(-1px);
    }

    /* Botón Logout específico */
    .erp-logout-btn .stButton > button {
        background: rgba(220, 38, 38, 0.08) !important;
        border: 1px solid rgba(220, 38, 38, 0.25) !important;
        color: #dc2626 !important;
        font-size: 0.82rem !important;
        padding: 0.6rem 0.8rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    .erp-logout-btn .stButton > button:hover {
        background: #dc2626 !important;
        border-color: #dc2626 !important;
        color: #ffffff !important;
        box-shadow: 0 3px 10px rgba(220, 38, 38, 0.3) !important;
    }

    /* ═══════════════════════════════════════════════════════
       PESTAÑAS DE SUBMÓDULOS (NIVEL 2)
    ═══════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-bottom: 2px solid var(--border) !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 0 0.5rem !important;
        gap: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 6px 6px 0 0 !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 0.75rem 1.25rem !important;
        transition: all 0.15s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary) !important;
        background: rgba(250, 125, 42, 0.06) !important;
    }

    .stTabs [aria-selected="true"] {
        color: #fa7d2a !important;
        border-bottom: 3px solid #fa7d2a !important;
        background: rgba(250, 125, 42, 0.08) !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #fa7d2a !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1.8rem 1.6rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }

    /* ═══════════════════════════════════════════════════════
       MÉTRICAS / KPI CARDS
    ═══════════════════════════════════════════════════════ */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        transition: box-shadow 0.2s ease, transform 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.09);
        transform: translateY(-1px);
        border-color: rgba(250, 125, 42, 0.35);
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.73rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    [data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

    /* ═══════════════════════════════════════════════════════
       EXPANDER (Panel de Parámetros)
    ═══════════════════════════════════════════════════════ */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        margin-bottom: 1.1rem !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: var(--primary) !important;
        font-size: 0.87rem !important;
        letter-spacing: 0.02em;
        padding: 0.7rem 1rem !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: rgba(250, 125, 42, 0.04) !important;
        color: #fa7d2a !important;
    }

    /* ═══════════════════════════════════════════════════════
       TIPOGRAFÍA
    ═══════════════════════════════════════════════════════ */
    h1, h2, h3, h4 {
        color: var(--primary) !important;
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* ═══════════════════════════════════════════════════════
       INPUTS
    ═══════════════════════════════════════════════════════ */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stNumberInput input {
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus {
        border-color: #fa7d2a !important;
        box-shadow: 0 0 0 1px #fa7d2a !important;
    }

    /* ═══════════════════════════════════════════════════════
       DATAFRAMES
    ═══════════════════════════════════════════════════════ */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    /* ═══════════════════════════════════════════════════════
       ENCABEZADO DE MÓDULO (clases reutilizables)
    ═══════════════════════════════════════════════════════ */
    .module-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 14px 24px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.12rem;
        letter-spacing: 0.02em;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 12px rgba(26, 58, 92, 0.18);
        border-left: 4px solid var(--accent);
    }

    .kpi-section-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        margin: 0.8rem 0 0.5rem 0;
    }

    /* ═══════════════════════════════════════════════════════
       SEPARADOR
    ═══════════════════════════════════════════════════════ */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #cbd5e1, transparent);
        margin: 1.4rem 0;
    }

    /* ═══════════════════════════════════════════════════════
       SPINNER
    ═══════════════════════════════════════════════════════ */
    [data-testid="stSpinner"] { color: var(--accent) !important; }

    /* ═══════════════════════════════════════════════════════
       PIE DE PÁGINA
    ═══════════════════════════════════════════════════════ */
    .footer-custom {
        margin-top: 3rem;
        padding: 1.2rem 0;
        border-top: 1px solid var(--border);
        font-size: 0.82rem;
        color: var(--text-muted);
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)