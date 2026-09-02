import streamlit as st
import os
import base64
from utils.estilos import cargar_css
from utils.auth import verificar_login

# Importación de módulos (sin cambios)
import modulos.m1_ventas_forecast as m1
import modulos.m2_desviaciones as m2
import modulos.m3_produccion as m3
import modulos.m4_asistente_ia as m4
import modulos.m5_cierre_inventario as m5
import modulos.m6_salud_financiera as m6
import modulos.m7_control_multicentro as m7
import modulos.m8_ventas_regionales as m8

# ══════════════════════════════════════════════════════════
# 0. CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════
st.set_page_config(
    layout="wide",
    page_title="Portal Supply Chain & S&OP – Sapori",
    page_icon="🟠"
)
cargar_css()

# ══════════════════════════════════════════════════════════
# 1. AUTENTICACIÓN
# ══════════════════════════════════════════════════════════
if not verificar_login():
    st.stop()

# ══════════════════════════════════════════════════════════
# 2. TOPBAR (banner institucional)
# ══════════════════════════════════════════════════════════
if os.path.exists("assets/logo_empresa.png"):
    with open("assets/logo_empresa.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="erp-logo" />'
else:
    logo_html = '<span class="erp-logo-text">SAPORI</span>'

usuario_activo = st.session_state.get("usuario_nombre", "Gerencia")

st.markdown(f"""
<div class="erp-topbar">
    <div class="erp-topbar-left">
        {logo_html}
        <div class="erp-topbar-info">
            <span class="erp-topbar-title">Portal Supply Chain &amp; S&amp;OP</span>
            <span class="erp-topbar-sub">Plataforma de Inteligencia Operativa &nbsp;·&nbsp; Sapori, C.A.</span>
        </div>
    </div>
    <div class="erp-topbar-right">
        <span class="erp-user-badge">👤 {usuario_activo}</span>
        <span class="erp-version">v1.7</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 3. BARRA DE LOGOUT (alineada a la derecha, bajo el topbar)
# ══════════════════════════════════════════════════════════
_, col_logout = st.columns([11.5, 1])
with col_logout:
    # El CSS .erp-logout-col da estilo especial a este botón
    st.markdown('<div class="erp-logout-col">', unsafe_allow_html=True)
    if st.button("🚪 Salir", key="btn_logout", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 4. NAVEGACIÓN PRINCIPAL – GRUPOS DE MÓDULOS
#    Cada grupo es una pestaña de nivel 1 (estilo ERP oscuro).
#    Dentro de cada grupo, los módulos son pestañas de nivel 2.
# ══════════════════════════════════════════════════════════
grupo_tabs = st.tabs([
    "📊  Comercial",
    "🏭  Operaciones",
    "📦  Supply & Inventario",
    "💰  Finanzas & Riesgo",
    "🤖  Asistente IA",
])

# ──────────────────────────────────────────────────────────
# GRUPO 1 · Comercial
#   M1 – Ventas & Forecast  |  M8 – Desempeño Regional
# ──────────────────────────────────────────────────────────
with grupo_tabs[0]:
    # Panel de parámetros (reemplaza los inputs del sidebar)
    de_prev = st.session_state.get("dias_efectivos", 8)
    dr_prev = st.session_state.get("dias_restantes", 15)
    with st.expander(
        f"⚙️  Parámetros del Período  ·  {de_prev} días efectivos  ·  {dr_prev} restantes",
        expanded=False
    ):
        col_a, col_b, _ = st.columns([1.6, 1.6, 5])
        with col_a:
            dias_efectivos = st.number_input(
                "Días Efectivos de Venta", min_value=1, value=de_prev, step=1, key="de_grp1"
            )
        with col_b:
            dias_restantes = st.number_input(
                "Días Restantes de Venta", min_value=0, value=dr_prev, step=1, key="dr_grp1"
            )
        # Persistir para que el expander refleje valores actualizados
        st.session_state["dias_efectivos"] = dias_efectivos
        st.session_state["dias_restantes"] = dias_restantes

    # Módulos del grupo como pestañas de nivel 2
    mod_tabs_c = st.tabs(["📈  Ventas & Forecast", "🗺️  Desempeño Regional (CEDIs)"])
    with mod_tabs_c[0]:
        m1.renderizar(dias_efectivos, dias_restantes)
    with mod_tabs_c[1]:
        m8.renderizar()

# ──────────────────────────────────────────────────────────
# GRUPO 2 · Operaciones
#   M3 – Producción  |  M7 – Control Multicentro (SICI)
# ──────────────────────────────────────────────────────────
with grupo_tabs[1]:
    mod_tabs_o = st.tabs(["⚙️  Control de Producción", "🏢  Control Multicentro (SICI)"])
    with mod_tabs_o[0]:
        m3.renderizar()
    with mod_tabs_o[1]:
        m7.renderizar()

# ──────────────────────────────────────────────────────────
# GRUPO 3 · Supply & Inventario
#   M2 – Desviaciones  |  M5 – Cierre de Inventario
# ──────────────────────────────────────────────────────────
with grupo_tabs[2]:
    mod_tabs_s = st.tabs(["📉  Desviaciones & Tendencias", "📦  Cierre de Inventario Valorizado"])
    with mod_tabs_s[0]:
        m2.renderizar()
    with mod_tabs_s[1]:
        m5.renderizar()

# ──────────────────────────────────────────────────────────
# GRUPO 4 · Finanzas & Riesgo
#   M6 – Salud Financiera (módulo único en el grupo)
# ──────────────────────────────────────────────────────────
with grupo_tabs[3]:
    m6.renderizar()

# ──────────────────────────────────────────────────────────
# GRUPO 5 · Asistente IA
#   M4 – Asistente de Consultas  (también necesita parámetros de período)
# ──────────────────────────────────────────────────────────
with grupo_tabs[4]:
    de_ia = st.session_state.get("dias_efectivos_ia", 8)
    dr_ia = st.session_state.get("dias_restantes_ia", 15)
    with st.expander(
        f"⚙️  Parámetros del Período  ·  {de_ia} días efectivos  ·  {dr_ia} restantes",
        expanded=False
    ):
        col_a, col_b, _ = st.columns([1.6, 1.6, 5])
        with col_a:
            dias_efectivos_ia = st.number_input(
                "Días Efectivos de Venta", min_value=1, value=de_ia, step=1, key="de_grp5"
            )
        with col_b:
            dias_restantes_ia = st.number_input(
                "Días Restantes de Venta", min_value=0, value=dr_ia, step=1, key="dr_grp5"
            )
        st.session_state["dias_efectivos_ia"] = dias_efectivos_ia
        st.session_state["dias_restantes_ia"] = dias_restantes_ia

    m4.renderizar(dias_efectivos_ia, dias_restantes_ia)

# ══════════════════════════════════════════════════════════
# 5. PIE DE PÁGINA GLOBAL
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-custom">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
        <div>
            <strong>Plataforma de Inteligencia Operativa</strong><br>
            <span style="font-size:0.75rem; color:#94a3b8;">Versión 1.7 · Sapori, C. A. Todos los derechos reservados</span>
        </div>
        <div style="text-align:right;">
            Desarrollado por <strong>Jair Ramos</strong><br>
            <span style="color:#1a3a5c; font-weight:600; font-size:0.82rem;">KaisenYork | Software</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)