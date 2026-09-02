import streamlit as st

def cargar_css():
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════
       VARIABLES GLOBALES
    ═══════════════════════════════════════════════════════ */
    :root {
        --primary:        #1a3a5c;
        --primary-light:  #2c5a8a;
        --accent:         #e8a317;
        --accent-dim:     rgba(232, 163, 23, 0.15);
        --bg-main:        #f0f4f8;
        --bg-card:        #ffffff;
        --bg-soft:        #f8fafc;
        --text-main:      #1e293b;
        --text-muted:     #64748b;
        --border:         #e2e8f0;
        --success:        #16a34a;
        --warning:        #d97706;
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
       ERP TOPBAR
    ═══════════════════════════════════════════════════════ */
    .erp-topbar {
        background: linear-gradient(135deg, var(--primary) 0%, var(--nav-darker) 100%);
        padding: 0 1.8rem;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0 -1.8rem 0 -1.8rem;
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
        color: #7a94b0;
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
        border: 1px solid rgba(232, 163, 23, 0.45);
        color: var(--accent) !important;
        padding: 0.32rem 0.9rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .erp-version {
        color: #475569;
        font-size: 0.7rem;
        letter-spacing: 0.06em;
        font-weight: 500;
    }

    /* ═══════════════════════════════════════════════════════
       BARRA DE ACCIÓN (contiene el botón de logout)
    ═══════════════════════════════════════════════════════ */
    .erp-action-row {
        background: var(--nav-dark);
        margin: 0 -1.8rem;
        padding: 0.3rem 1.8rem 0.3rem;
        display: flex;
        justify-content: flex-end;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    /* ═══════════════════════════════════════════════════════
       NAVEGACIÓN PRINCIPAL – TABS DE GRUPO (nivel 1)
       Estilo: barra oscura tipo menú ERP
    ═══════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--nav-dark) !important;
        gap: 0 !important;
        padding: 0 1rem !important;
        margin: 0 -1.8rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 0 !important;
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #7a94b0 !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        font-weight: 500;
        font-size: 0.87rem;
        padding: 0.88rem 1.35rem !important;
        transition: color 0.18s ease, background 0.18s ease, border-color 0.18s ease;
        letter-spacing: 0.01em;
        white-space: nowrap;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #d1dde9 !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }

    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 3px solid var(--accent) !important;
        background: rgba(232, 163, 23, 0.07) !important;
        font-weight: 700 !important;
    }

    /* Quitar la línea azul nativa de Streamlit */
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

    /* Área de contenido del tab de grupo */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1.4rem 0 0 0 !important;
        background: transparent !important;
    }

    /* ═══════════════════════════════════════════════════════
       TABS DE MÓDULO (nivel 2, anidados dentro de un tab-panel)
       Estilo: tarjeta blanca con pestañas profesionales
    ═══════════════════════════════════════════════════════ */
    [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9 !important;
        margin: 0 !important;
        padding: 0 0.6rem !important;
        border: 1px solid var(--border) !important;
        border-bottom: none !important;
        border-radius: 10px 10px 0 0 !important;
        gap: 2px !important;
    }

    [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        padding: 0.62rem 1.15rem !important;
        border-bottom: 2px solid transparent !important;
    }

    [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-light) !important;
        background: rgba(26, 58, 92, 0.06) !important;
    }

    [data-baseweb="tab-panel"] .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
        font-weight: 700 !important;
        background: rgba(26, 58, 92, 0.06) !important;
    }

    /* Contenido del tab de módulo: panel tipo tarjeta */
    [data-baseweb="tab-panel"] .stTabs [data-baseweb="tab-panel"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1.8rem 1.6rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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
        background: rgba(26, 58, 92, 0.04) !important;
    }

    /* ═══════════════════════════════════════════════════════
       BOTÓN DE LOGOUT (estilo sobrio para topbar)
    ═══════════════════════════════════════════════════════ */
    .erp-logout-col .stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        padding: 0.28rem 0.9rem !important;
        border-radius: 6px !important;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .erp-logout-col .stButton > button:hover {
        background: rgba(220, 38, 38, 0.12) !important;
        border-color: rgba(220, 38, 38, 0.4) !important;
        color: #fca5a5 !important;
    }

    /* ═══════════════════════════════════════════════════════
       BOTONES GENERALES
    ═══════════════════════════════════════════════════════ */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"] {
        background: var(--primary);
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-light);
        box-shadow: 0 4px 12px rgba(26, 58, 92, 0.25);
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