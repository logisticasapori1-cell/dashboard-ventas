import streamlit as st
import time
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
import modulos.m8_ventas_regionales as m8

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(layout="wide", page_title="Portal de Supply Chain & S&OP - Sapori", page_icon="🟠")
cargar_css()

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN
# ==========================================
if not verificar_login():
    st.stop() 

# ==========================================
# 3. GESTIÓN DE ESTADO (MEMORIA DEL MENÚ)
# ==========================================
lista_modulos = [
    "1. Control Operativo de Ventas y Forecast",
    "2. Tablero de Desviaciones y Tendencias",
    "3. Control y Análisis de Producción Mensual",
    "4. Asistente de Consultas (IA)",
    "5. Cierre de Inventario Valorizado",
    "6. Salud Financiera y Riesgo Suministro",
    "7. Control Integral Multicentro (SICI)",
    "8. Desempeño Regional de Ventas (CEDIs)"
]

if "modulo_actual" not in st.session_state:
    st.session_state.modulo_actual = lista_modulos[0]

# ==========================================
# 4. INTERFAZ LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("assets/logo_empresa.png")
    
    st.markdown("### Módulos de Operación")
    # El radio button ahora lee y escribe en nuestra memoria segura
    modulo_seleccionado = st.radio(
        "Área a visualizar", 
        lista_modulos, 
        index=lista_modulos.index(st.session_state.modulo_actual),
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
# 5. EL HACK DEL DOBLE RERUN (DESTRUCTOR DE CACHÉ)
# ==========================================
# Si el usuario hace clic en un módulo diferente, interceptamos la acción
if modulo_seleccionado != st.session_state.modulo_actual:
    st.session_state.modulo_actual = modulo_seleccionado
    
    # Obligamos al servidor a borrar el módulo anterior de la pantalla
    with st.spinner("Desplegando análisis..."):
        time.sleep(0.2)
        
    # Reiniciamos la aplicación entera de forma invisible para que el nuevo módulo cargue en un lienzo en blanco
    st.rerun() 

# ==========================================
# 6. ENRUTADOR DE MÓDULOS (EJECUCIÓN LIMPIA)
# ==========================================
modulo_activo = st.session_state.modulo_actual

if modulo_activo == lista_modulos[0]:
    m1.renderizar(dias_efectivos, dias_restantes)
elif modulo_activo == lista_modulos[1]:
    m2.renderizar()
elif modulo_activo == lista_modulos[2]:
    m3.renderizar()
elif modulo_activo == lista_modulos[3]:
    m4.renderizar(dias_efectivos, dias_restantes)
elif modulo_activo == lista_modulos[4]:
    m5.renderizar()
elif modulo_activo == lista_modulos[5]:
    m6.renderizar()
elif modulo_activo == lista_modulos[6]:
    m7.renderizar()
elif modulo_activo == lista_modulos[7]:
    m8.renderizar()
# ==========================================
# 7. PIE DE PÁGINA GLOBAL
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