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
            col_l, col_c, col_r = st.columns([1.5, 1.3, 1.5])
            with col_c:
                st.image("assets/logo_empresa.png", use_column_width=True)
        else:
            st.markdown("<h1 style='text-align:center; color:#1a3a5c; margin:0; font-size:2rem; letter-spacing:0.04em;'>SAPORI</h1>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center; color:#2f353d; margin:0.3rem 0 1.4rem 0; font-size:1.3rem; font-family: \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif; font-weight:600;'>Portal de Supply Chain &amp; S&amp;OP</p>", unsafe_allow_html=True)

        with st.form("formulario_login"):
            st.markdown("##### Ingrese Credenciales")
            usuario = st.text_input("Usuario o Correo", placeholder="sapori@empresa.com")
            contrasena = st.text_input("Contraseña", type="password", placeholder="••••••••")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            boton_ingresar = st.form_submit_button("Acceder", type="primary", use_container_width=True)

            if boton_ingresar:
                usuarios_autorizados = {
                    "admin": "sapori2026",
                    "Jair Ramos": "1402",
                    "Romulo Delgado": "gerencia123",
                    "logistica": "logistica2026",
                    "Gerente General": "sapori2026"
                }
                if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == contrasena:
                    st.session_state['autenticado'] = True
                    st.success("✅ Acceso concedido. Inicializando entorno...")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Verifique e intente de nuevo.")

        st.markdown("""
            <p style='text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:1.8rem; line-height:1.5;'>
                © 2026 kaisenYork | Software <br>
                Versión 1.7 (Sapori, C. A.) | Todos los derechos reservados
            </p>
        """, unsafe_allow_html=True)
        return False
        
    return True