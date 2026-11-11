import os

import streamlit as st

from utils import apariencia, datos, ui
from utils.auth import verificar_login
from utils.estilos import cargar_css, ocultar_barra_lateral

import modulos.m0_resumen as m0
import modulos.m1_ventas_forecast as m1
import modulos.m2_desviaciones as m2
import modulos.m3_produccion as m3
import modulos.m4_asistente_ia as m4
import modulos.m5_cierre_inventario as m5
import modulos.m6_salud_financiera as m6
import modulos.m7_control_multicentro as m7
import modulos.m8_ventas_regionales as m8

VERSION = "v2.0"
LOGO = "assets/logo_empresa.png"

# ══════════════════════════════════════════════════════════
# 0. CONFIGURACIÓN
# ══════════════════════════════════════════════════════════
st.set_page_config(
    layout="wide",
    page_title="Portal Supply Chain & S&OP – Sapori",
    page_icon=LOGO if os.path.exists(LOGO) else "🟠",
    initial_sidebar_state="auto",
)
cargar_css()

# ══════════════════════════════════════════════════════════
# 1. AUTENTICACIÓN
# ══════════════════════════════════════════════════════════
if not st.session_state.get("autenticado", False):
    ocultar_barra_lateral()
    apariencia.aplicar_guardado()
if not verificar_login():
    st.stop()


# ══════════════════════════════════════════════════════════
# 2. PARÁMETROS GLOBALES DEL PERÍODO (uno solo para todo el portal)
# ══════════════════════════════════════════════════════════
def dias():
    return st.session_state.get("dias_efectivos", 8), st.session_state.get("dias_restantes", 15)


# ══════════════════════════════════════════════════════════
# 3. PÁGINAS
# ══════════════════════════════════════════════════════════
PAGINAS = {}


def resumen():
    m0.renderizar(PAGINAS, *dias())


def ventas():
    m1.renderizar(*dias())


def cedis():
    m8.renderizar()


def produccion():
    m3.renderizar()


def multicentro():
    m7.renderizar()


def desviaciones():
    m2.renderizar()


def cierre():
    m5.renderizar()


def finanzas():
    m6.renderizar()


def asistente():
    m4.renderizar(*dias())


PAGINAS.update({
    "resumen": st.Page(resumen, title="Resumen ejecutivo", icon=":material/home:", url_path="resumen", default=True),
    "ventas": st.Page(ventas, title="Ventas & Forecast", icon=":material/trending_up:", url_path="ventas"),
    "cedis": st.Page(cedis, title="Desempeño por CEDI", icon=":material/location_on:", url_path="cedis"),
    "produccion": st.Page(produccion, title="Producción", icon=":material/factory:", url_path="produccion"),
    "multicentro": st.Page(multicentro, title="Control Multicentro", icon=":material/apartment:", url_path="multicentro"),
    "desviaciones": st.Page(desviaciones, title="Desviaciones", icon=":material/warning:", url_path="desviaciones"),
    "cierre": st.Page(cierre, title="Cierre de inventario", icon=":material/inventory_2:", url_path="cierre"),
    "finanzas": st.Page(finanzas, title="Salud financiera", icon=":material/account_balance_wallet:", url_path="finanzas"),
    "asistente": st.Page(asistente, title="Asistente IA", icon=":material/chat:", url_path="asistente"),
})

navegacion = st.navigation({
    "Inicio": [PAGINAS["resumen"]],
    "Comercial": [PAGINAS["ventas"], PAGINAS["cedis"]],
    "Operaciones": [PAGINAS["produccion"], PAGINAS["multicentro"]],
    "Supply": [PAGINAS["desviaciones"], PAGINAS["cierre"]],
    "Finanzas": [PAGINAS["finanzas"]],
    "Asistente": [PAGINAS["asistente"]],
}, position="sidebar")

# ══════════════════════════════════════════════════════════
# 4. BARRA LATERAL
# ══════════════════════════════════════════════════════════
if os.path.exists(LOGO):
    st.logo(LOGO, size="large")

with st.sidebar:
    st.html('<p class="sp-side-label">Parámetros del período</p>')
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Días efectivos", min_value=1, value=8, step=1, key="dias_efectivos")
    with c2:
        st.number_input("Días restantes", min_value=0, value=15, step=1, key="dias_restantes")

    fecha = datos.fecha_actualizacion()
    texto_fecha = fecha.strftime("%d/%m/%Y %H:%M") if fecha else "sin fecha"
    st.html(f'<p class="sp-side-meta">Datos: {os.path.basename(datos.ARCHIVO_DATOS)} · {texto_fecha}</p>')

    st.divider()
    apariencia.selector()

    st.divider()
    usuario = st.session_state.get("usuario_nombre", "Gerencia")
    inicial = (usuario.strip()[:1] or "G").upper()
    cu, cb = st.columns([3, 2], vertical_alignment="center")
    with cu:
        st.html(f'<div class="sp-user"><span class="sp-avatar">{ui._e(inicial)}</span>'
                f'<span><span class="sp-user-name">{ui._e(usuario)}</span><span class="sp-user-ver">{VERSION}</span></span></div>')
    with cb:
        if st.button("Salir", key="btn_salir", icon=":material/logout:", width="stretch"):
            st.session_state["autenticado"] = False
            st.rerun()

# ══════════════════════════════════════════════════════════
# 5. PÁGINA ACTIVA + PIE
# ══════════════════════════════════════════════════════════
navegacion.run()
ui.pie(VERSION)
