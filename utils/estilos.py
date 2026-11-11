import streamlit as st

# Colores y tipografía base: .streamlit/config.toml
# Componentes `sp-*`: utils/ui.py

_CSS = """
<style>
/*__VARS__*/

/* ── Chrome de Streamlit ───────────────────────────── */
/* stToolbar NO se oculta: ahí vive el botón que abre el menú en teléfono */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"] { display:none !important; }
header[data-testid="stHeader"] { background:transparent !important; }
.block-container { padding:2rem 2.25rem 2rem !important; max-width:1440px !important; }
@media (max-width: 640px) { .block-container { padding:4rem 1rem 2rem !important; } }
[data-testid="stMainBlockContainer"] { font-variant-numeric:tabular-nums; }

/* ── Barra lateral ─────────────────────────────────── */
[data-testid="stSidebar"] { border-right:none !important; }
[data-testid="stSidebarHeader"] { padding:1.5rem 1.5rem .5rem !important; }
[data-testid="stSidebarHeader"] img { height:auto !important; max-height:72px !important; width:auto !important; }
[data-testid="stNavSectionHeader"] {
  font-size:11px !important; font-weight:600 !important; letter-spacing:.08em; text-transform:uppercase;
  color:#a9bccf !important; padding-left:.75rem !important;
}
[data-testid="stSidebarNavLink"] { border-radius:8px !important; min-height:40px; }
[data-testid="stSidebarNavLink"] span { color:#d6e0ea !important; font-weight:500; }
[data-testid="stSidebarNavLink"]:hover { background:rgba(255,255,255,.08) !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:rgba(250,125,42,.22) !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] span { color:#ffffff !important; font-weight:600; }
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] { color:#a9bccf !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stIconMaterial"] { color:var(--orange) !important; }
[data-testid="stSidebarNavSeparator"] { border-color:rgba(255,255,255,.12) !important; }
[data-testid="stSidebar"] .sp-side-label {
  margin:0 0 .25rem; font-size:11px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:#a9bccf;
}
[data-testid="stSidebar"] .sp-side-meta { margin:0; font-size:12px; color:#d6e0ea; }
[data-testid="stSidebar"] .sp-user { display:flex; align-items:center; gap:10px; }
[data-testid="stSidebar"] .sp-avatar {
  width:32px; height:32px; border-radius:16px; background:rgba(255,255,255,.14);
  display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:600; color:#fff; flex:none;
}
[data-testid="stSidebar"] .sp-user-name { font-size:13px; font-weight:600; color:#fff; display:block; overflow-wrap:anywhere; }
[data-testid="stSidebar"] .sp-user-ver { font-size:12px; color:#a9bccf; display:block; }
[data-testid="stSidebar"] [data-testid="stNumberInput"] label p { color:#d6e0ea !important; font-size:12px !important; }
[data-testid="stSidebar"] .stButton > button {
  background:transparent !important; border:1px solid rgba(255,255,255,.22) !important; color:#d6e0ea !important;
}
[data-testid="stSidebar"] .stButton > button:hover { border-color:var(--orange) !important; color:#fff !important; }

/* ── Encabezado de página ──────────────────────────── */
.sp-head { display:flex; flex-direction:column; gap:6px; margin:0 0 .25rem; }
.sp-crumb { margin:0; font-size:13px; color:var(--muted); }
.sp-title { margin:0; padding:0 !important; font-size:28px !important; font-weight:700 !important; color:var(--ink) !important; letter-spacing:-.015em; line-height:1.2 !important; }
.sp-sub { margin:0; font-size:13px; color:var(--muted); }
.sp-section { display:flex; flex-direction:column; gap:4px; margin-top:1.25rem; padding-top:1.25rem; border-top:1px solid var(--border); }
.sp-section-title { margin:0 !important; padding:0 !important; font-size:20px !important; font-weight:700 !important; color:var(--ink) !important; }

/* ── Tarjetas ──────────────────────────────────────── */
[class*="st-key-sp_card_"] { background:var(--surface); border-radius:12px !important; padding:20px !important; border-color:var(--border) !important; }
.sp-card-head { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:baseline; gap:8px; }
.sp-card-title { margin:0 !important; padding:0 !important; font-size:15px !important; font-weight:600 !important; color:var(--ink) !important; }
.sp-card-note { font-size:13px; color:var(--muted); }

/* ── KPIs ──────────────────────────────────────────── */
.sp-grid { display:grid; gap:16px; }
.sp-kpi {
  background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; box-sizing:border-box;
  display:flex; flex-direction:column; gap:10px; min-width:0;
}
.sp-label { margin:0; font-size:12px; font-weight:600; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); }
.sp-big { margin:0; font-size:30px; line-height:1.1; font-weight:700; color:var(--ink); letter-spacing:-.01em; overflow-wrap:anywhere; }
.sp-unit { font-size:14px; font-weight:500; color:var(--muted); margin-left:4px; letter-spacing:0; white-space:nowrap; display:inline-block; overflow-wrap:normal; }
.sp-row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.sp-delta { display:inline-flex; align-items:center; gap:4px; font-size:13px; font-weight:600; color:var(--muted); }
.sp-note { margin:0; font-size:13px; color:var(--muted); }
.sp-extra { display:flex; align-items:baseline; gap:8px; padding-top:6px; border-top:1px solid var(--border); }
.sp-extra-val { font-size:22px; font-weight:700; color:var(--ink); }
.sp-extra-txt { font-size:13px; color:var(--muted); }
.sp-bar-wrap { display:flex; flex-direction:column; gap:6px; }
.sp-track { display:block; width:100%; border-radius:4px; background:var(--track); }
.sp-fill { display:block; border-radius:4px; background:var(--orange); }
.sp-bar-labels { display:flex; justify-content:space-between; gap:8px; font-size:13px; color:var(--muted); }
.sp-group { gap:16px; }
.sp-group-head { display:flex; justify-content:space-between; align-items:center; gap:8px; }
.sp-badge { font-size:13px; font-weight:600; color:var(--orange-txt); }
.sp-period { margin:0; font-size:18px; font-weight:600; color:var(--ink); }
.sp-stats { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; padding-top:14px; border-top:1px solid var(--border); }
.sp-stat { display:flex; flex-direction:column; gap:4px; min-width:0; }
.sp-stat-label { margin:0; font-size:13px; color:var(--muted); }
.sp-stat-val { margin:0; font-size:22px; font-weight:700; color:var(--ink); }

/* ── Barras horizontales / resúmenes ──────────────── */
.sp-hbars { display:flex; flex-direction:column; gap:6px; }
.sp-hb { display:grid; align-items:center; gap:12px; min-height:32px; }
.sp-hb-name { font-size:13px; color:var(--ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sp-hb-val { font-size:13px; font-weight:600; text-align:right; color:var(--ink); }
.sp-hb-extra { font-size:13px; text-align:right; color:var(--muted); }
.sp-summary { display:flex; flex-wrap:wrap; gap:24px; padding-top:12px; border-top:1px solid var(--border); font-size:13px; color:var(--muted); }
.sp-legend { display:flex; flex-wrap:wrap; gap:16px; font-size:12px; color:var(--muted); }
.sp-legend span { display:inline-flex; align-items:center; gap:6px; }
.sp-legend i { width:10px; height:10px; border-radius:2px; display:inline-block; }

/* ── Puntos de atención ───────────────────────────── */
.sp-alert { display:flex; gap:12px; padding-top:12px; border-top:1px solid var(--border); }
.sp-alert-ico { width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; flex:none; }
.sp-alert-body { display:flex; flex-direction:column; gap:4px; min-width:0; }
.sp-alert-title { margin:0; font-size:14px; font-weight:600; color:var(--ink); }
.sp-alert-text { margin:0; font-size:13px; color:var(--muted); }
[class*="st-key-sp_card_"] [data-testid="stPageLink"] a { padding-left:44px !important; }
[class*="st-key-sp_card_"] [data-testid="stPageLink"] a span { color:var(--navy) !important; font-size:13px !important; font-weight:600; }

/* ── Estado ───────────────────────────────────────── */
.sp-status { display:flex; flex-wrap:wrap; align-items:center; gap:8px; padding:10px 14px; border:1px solid; border-radius:10px; font-size:13px; }
.sp-status-text { color:var(--muted); }
[class*="st-key-ia_sugerida_"] button { min-height:48px; justify-content:flex-start; }
[class*="st-key-ia_sugerida_"] button p { white-space:normal !important; text-align:left; line-height:1.3; overflow:visible !important; text-overflow:clip !important; }

/* ── Botón principal: texto con contraste AA en ambos modos ── */
[data-testid="stMainBlockContainer"] button[kind="primary"], [data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"] {
  background-color:var(--primary) !important; border-color:var(--primary) !important; color:var(--on-primary) !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"] p { color:var(--on-primary) !important; }

/* ── Selector de tema y botón técnico de recarga (invisible) ── */
.st-key-sp_tema_rerun, [class*="st-key-sp_tema_js"] { display:none !important; }
[data-testid="stSidebar"] iframe[title="st.iframe"], [data-testid="stSidebar"] [data-testid="stIFrame"] { display:none !important; }

/* ── Selectores segmentados: texto del botón activo con contraste AA ── */
[data-testid="stMainBlockContainer"] [data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stMainBlockContainer"] [data-testid="stButtonGroup"] button[kind*="Active"] { color:var(--orange-txt) !important; }
[data-testid="stMainBlockContainer"] [data-testid="stButtonGroup"] button[aria-checked="true"] p,
[data-testid="stMainBlockContainer"] [data-testid="stButtonGroup"] button[kind*="Active"] p { color:var(--orange-txt) !important; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[kind*="Active"] {
  color:#ffffff !important; background:rgba(250,125,42,.30) !important; border-color:var(--orange) !important;
}
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[aria-checked="true"] p,
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[kind*="Active"] p { color:#ffffff !important; }

/* Selector de apariencia: tres opciones en una sola fila */
[data-testid="stSidebar"] .st-key-sp_tema [data-testid="stButtonGroup"] > div { flex-wrap:nowrap !important; }
[data-testid="stSidebar"] .st-key-sp_tema button { padding-left:6px !important; padding-right:6px !important; min-height:36px; flex:1 1 0; min-width:0; }
[data-testid="stSidebar"] .st-key-sp_tema button p { font-size:12.5px !important; }

/* ── Pie ──────────────────────────────────────────── */
.sp-foot { display:flex; flex-wrap:wrap; justify-content:space-between; gap:12px; margin-top:1rem; padding-top:20px; border-top:1px solid var(--border); font-size:12px; color:var(--muted); }

/* ══════════════════════════════════════════════════
   COMPATIBILIDAD: módulos que aún no migran a la plantilla
   ══════════════════════════════════════════════════ */
h1, h2, h3, h4 { color:var(--ink) !important; letter-spacing:-.015em; }
[data-testid="stMetric"] {
  background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px 18px;
}
[data-testid="stMetricLabel"] { color:var(--muted) !important; font-size:.73rem !important; text-transform:uppercase; letter-spacing:.04em; font-weight:600 !important; }
[data-testid="stMetricValue"] { color:var(--ink) !important; font-weight:700 !important; font-size:1.45rem !important; }
.module-header {
  color:var(--ink); font-weight:600; font-size:.8rem; letter-spacing:.06em; text-transform:uppercase;
  padding:0 0 .6rem; margin:.5rem 0 1rem; border-bottom:1px solid var(--border);
}
.kpi-section-label { font-size:.75rem; font-weight:600; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); margin:.8rem 0 .5rem; }
.stTabs [data-baseweb="tab-list"] { gap:4px; border-bottom:1px solid var(--border); }
.stTabs [aria-selected="true"] { color:var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color:var(--orange) !important; }
.stDataFrame { border-radius:10px; overflow:hidden; }
hr { border:none; height:1px; background:var(--border); margin:1.4rem 0; }
</style>
"""

# Pantalla de acceso: sin barra lateral
CSS_LOGIN = """
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display:none !important; }
</style>
"""


def _variables():
    from utils import tema
    p = tema.paleta()
    nombres = {"BG": "bg", "SURFACE": "surface", "TRACK": "track", "BORDER": "border", "INK": "ink", "MUTED": "muted",
               "NAVY": "navy", "ORANGE": "orange", "ORANGE_TXT": "orange-txt", "POS": "pos", "NEG": "neg",
               "PRIMARY": "primary", "ON_PRIMARY": "on-primary"}
    return ":root{" + "".join(f"--{v}:{p[k]};" for k, v in nombres.items()) + "}"


def cargar_css():
    """CSS del portal con los colores del modo activo (claro u oscuro)."""
    st.html(_CSS.replace("/*__VARS__*/", _variables()))


def ocultar_barra_lateral():
    st.html(CSS_LOGIN)
