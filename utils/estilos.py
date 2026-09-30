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
       ERP TOPBAR (BANNER INSTITUCIONAL CON USUARIO Y SALIR)
    ═══════════════════════════════════════════════════════ */
    div[data-testid="stHorizontalBlock"]:has(.st-key-top_btn_logout) {
        background: linear-gradient(135deg, var(--primary) 0%, var(--nav-darker) 100%);
        padding: 0.6rem 1.8rem;
        margin: 0 -1.8rem 1.1rem -1.8rem;
        border-bottom: 3px solid var(--accent);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
        align-items: center !important;
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
    .erp-user-badge {
        background: var(--accent-dim);
        border: 1px solid rgba(250, 125, 42, 0.45);
        color: var(--accent) !important;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        white-space: nowrap;
        display: inline-block;
    }
    .erp-version {
        color: #64748b;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        font-weight: 600;
        white-space: nowrap;
        display: inline-block;
    }

    /* Botón Logout integrado en la Topbar al lado del usuario */
    .st-key-top_btn_logout .stButton > button {
        background: rgba(220, 38, 38, 0.12) !important;
        border: 1px solid rgba(220, 38, 38, 0.35) !important;
        color: #fca5a5 !important;
        font-size: 0.8rem !important;
        padding: 0.38rem 0.85rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.18s ease !important;
        white-space: nowrap !important;
        box-shadow: none !important;
    }
    .st-key-top_btn_logout .stButton > button:hover {
        background: #dc2626 !important;
        border-color: #dc2626 !important;
        color: #ffffff !important;
        box-shadow: 0 3px 10px rgba(220, 38, 38, 0.35) !important;
        transform: translateY(-1px);
    }

  /* ═══════════════════════════════════════════════════════
  RESUMEN EJECUTIVO
  ═══════════════════════════════════════════════════════ */
  .executive-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 1.5rem;
      margin: 0.4rem 0 1.1rem;
  }
  .eyebrow {
      color: var(--accent);
      font-size: 0.7rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 0.25rem;
  }
  .executive-header h1 {
      color: var(--primary);
      font-size: clamp(1.65rem, 2.5vw, 2.2rem);
      line-height: 1.1;
      margin: 0;
      letter-spacing: -0.035em;
  }
  .executive-header p {
      color: var(--text-muted);
      margin: 0.45rem 0 0;
      font-size: 0.88rem;
  }
  .period-status {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 0.7rem 0.9rem;
      min-width: 220px;
      box-shadow: 0 2px 8px rgba(15, 39, 68, 0.05);
  }
  .period-status strong, .period-status small { display: block; }
  .period-status strong { color: var(--primary); font-size: 0.78rem; }
  .period-status small { color: var(--text-muted); font-size: 0.7rem; margin-top: 0.18rem; }
  .status-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--success); box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12); flex: 0 0 auto; }
  .summary-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--primary-light);
      border-radius: 10px;
      padding: 0.95rem 1rem;
      min-height: 108px;
      box-shadow: 0 2px 8px rgba(15, 39, 68, 0.04);
  }
  .summary-label, .summary-trend { display: block; }
  .summary-label { color: var(--text-muted); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
  .summary-card strong { display: block; color: var(--primary); font-size: 1.7rem; line-height: 1.25; margin: 0.35rem 0 0.2rem; }
  .summary-trend { font-size: 0.72rem; font-weight: 600; }
  .positive { color: var(--success); } .warning { color: var(--warning); } .neutral { color: var(--text-muted); }
  .insight-strip {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      background: #fff8f2;
      border: 1px solid #fed7aa;
      border-radius: 10px;
      padding: 0.75rem 0.9rem;
      margin: 1rem 0 1.2rem;
  }
  .insight-mark { display: grid; place-items: center; width: 25px; height: 25px; border-radius: 50%; color: #fff; background: var(--accent); font-weight: 800; font-size: 0.8rem; flex: 0 0 auto; }
  .insight-strip strong, .insight-strip span { display: block; }
  .insight-strip strong { color: var(--primary); font-size: 0.78rem; }
  .insight-strip span { color: var(--text-muted); font-size: 0.76rem; margin-top: 0.12rem; }
  .insight-action { margin-left: auto; color: var(--accent) !important; font-weight: 700; white-space: nowrap; }

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
