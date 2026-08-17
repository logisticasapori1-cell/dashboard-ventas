import streamlit as st
from utils.estilos import cargar_css
from utils.auth import verificar_login

# Importación de los módulos (Asegúrate de haberles puesto la letra 'm' al principio en la carpeta)
import modulos.m1_ventas_forecast as m1
import modulos.m2_desviaciones as m2
import modulos.m3_produccion as m3
import modulos.m4_asistente_ia as m4
import modulos.m5_cierre_inventario as m5
import modulos.m6_salud_financiera as m6
import modulos.m7_control_multicentro as m7

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(layout="wide", page_title="Portal de Supply Chain & S&OP - Sapori", page_icon="🟠")
cargar_css()

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN
# ==========================================
if not verificar_login():
    st.stop() # Detiene la ejecución si el usuario no ha ingresado credenciales

# ==========================================
# 3. INTERFAZ LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("assets/logo_empresa.png")
    
    st.markdown("### Módulos de Operación")
    modulo_activo = st.radio(
        "Área a visualizar",
        [
            "1. Control Operativo de Ventas y Forecast",
            "2. Tablero de Desviaciones y Tendencias",
            "3. Control y Análisis de Producción Mensual",
            "4. Asistente de Consultas (IA)",
            "5. Cierre de Inventario Valorizado",
            "6. Salud Financiera y Riesgo Suministro",
            "7. Control Integral Multicentro (SICI)"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### Control de Tiempos")
    dias_efectivos = st.number_input("Días de Venta Efectivos", min_value=1, value=8, step=1)
    dias_restantes = st.number_input("Días de Venta Restantes", min_value=0, value=15, step=1)

    st.markdown("---")
    st.caption("👤 Rol: Gerencia")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['autenticado'] = False
        st.rerun()

# ==========================================
# 4. ENRUTADOR DE MÓDULOS
# ==========================================
if modulo_activo == "1. Control Operativo de Ventas y Forecast":
    m1.renderizar(dias_efectivos, dias_restantes)

elif modulo_activo == "2. Tablero de Desviaciones y Tendencias":
    m2.renderizar()

elif modulo_activo == "3. Control y Análisis de Producción Mensual":
    m3.renderizar()

elif modulo_activo == "4. Asistente de Consultas (IA)":
    m4.renderizar(dias_efectivos, dias_restantes)

elif modulo_activo == "5. Cierre de Inventario Valorizado":
    m5.renderizar()

elif modulo_activo == "6. Salud Financiera y Riesgo Suministro":
    m6.renderizar()

elif modulo_activo == "7. Control Integral Multicentro (SICI)":
    m7.renderizar()
# ==========================================
# 5. PIE DE PÁGINA GLOBAL
# ==========================================
st.markdown("""
<div class="footer-custom">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
        <div>
            <strong>Plataforma de Inteligencia Operativa</strong><br>
            <span style="font-size:0.75rem; color:#94a3b8;">Versión 3.1 · Entorno Seguro</span>
        </div>
        <div style="text-align:right;">
            Desarrollado por <strong>Jair Ramos</strong><br>
            <span style="color:#1a3a5c; font-weight:600; font-size:0.82rem;">
                Dirección de Supply Chain Sapori
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)