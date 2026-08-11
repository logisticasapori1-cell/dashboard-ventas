import streamlit as st
import os

def verificar_login():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
            .block-container { padding-top: 4rem !important; max-width: 480px !important; }
        </style>
        """, unsafe_allow_html=True)

        # Buscar logo en la nueva ruta
        if os.path.exists("assets/logo_empresa.png"):
            col_l, col_c, col_r = st.columns([1.4, 1.2, 1.4])
            with col_c:
                st.image("assets/logo_empresa.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center; color:#1a3a5c; margin:0; font-size:2rem; letter-spacing:0.04em;'>SAPORI</h1>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center; color:#64748b; margin:0.3rem 0 1.4rem 0; font-size:0.95rem;'>Portal de Supply Chain &amp; S&amp;OP</p>", unsafe_allow_html=True)

        with st.form("formulario_login"):
            st.markdown("##### 🔐 Credenciales corporativas")
            usuario = st.text_input("Usuario o Correo Institucional", placeholder="ej. gerencia.operaciones")
            contrasena = st.text_input("Contraseña del Sistema", type="password", placeholder="••••••••")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            boton_ingresar = st.form_submit_button("Acceder al Sistema", type="primary", use_container_width=True)

            if boton_ingresar:
                usuarios_autorizados = {
                    "admin": "sapori2026",
                    "Jair Ramos": "1402",
                    "Romulo Delgado": "gerencia123",
                    "logistica": "logistica2026"
                }
                if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == contrasena:
                    st.session_state['autenticado'] = True
                    st.success("✅ Acceso concedido. Inicializando entorno...")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Verifique e intente de nuevo.")

        st.markdown("""
            <p style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:1.8rem; line-height:1.5;'>
                © 2026 Sapori · Dirección de Supply Chain &amp; Operaciones<br>
                Versión 3.1 (Lógica Dinámica)
            </p>
        """, unsafe_allow_html=True)
        return False
        
    return True