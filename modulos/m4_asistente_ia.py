import streamlit as st
import pandas as pd
import os
import requests

@st.cache_data
def _cargar_ventas_dashboard(path):
    return pd.read_excel(path, sheet_name="DASHBOARD", header=None)

@st.cache_data
def _cargar_ventas_matriz(path):
    return pd.read_excel(path, sheet_name="file_ventas")

@st.cache_data
def _cargar_desviaciones(path):
    return pd.read_excel(path, sheet_name="Table 1")

@st.cache_data
def _cargar_produccion_todas(path):
    xls = pd.ExcelFile(path)
    hojas = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}
    return xls.sheet_names, hojas

@st.cache_data
def _cargar_cierre_todas(path):
    xls = pd.ExcelFile(path)
    return {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}

@st.cache_data
def _cargar_kpis_fin(path):
    return pd.read_excel(path, sheet_name=0, header=None)

@st.cache_data
def _cargar_sici(path):
    return pd.read_excel(path, sheet_name=0, header=None)

def renderizar(dias_efectivos, dias_restantes):
    st.title("🤖 Asistente de Consultas — Supply Chain & S&OP")
    st.caption("Pregunta en lenguaje natural sobre ventas, forecast, desviaciones y producción")
    st.markdown('<div class="module-header">ASISTENTE INTELIGENTE CON DATOS DEL DASHBOARD</div>', unsafe_allow_html=True)

    def leer_secreto(nombre):
        try:
            if nombre in st.secrets and st.secrets[nombre]: return str(st.secrets[nombre]).strip()
        except Exception: pass
        env_val = os.environ.get(nombre, "").strip()
        if env_val: return env_val
        return st.session_state.get(nombre.lower(), "")

    if "gemini_api_key" not in st.session_state: st.session_state["gemini_api_key"] = ""
    if "groq_api_key" not in st.session_state: st.session_state["groq_api_key"] = ""
    if "chat_messages" not in st.session_state: st.session_state["chat_messages"] = []

    gemini_api_key = leer_secreto("GEMINI_API_KEY") or st.session_state.get("gemini_api_key", "")
    groq_api_key = leer_secreto("GROQ_API_KEY") or st.session_state.get("groq_api_key", "")
    proveedor = "gemini" if gemini_api_key else ("groq" if groq_api_key else None)

    if proveedor == "gemini": st.success("🔑 Usando Google Gemini (clave permanente o de sesión).")
    elif proveedor == "groq": st.warning("⚠️ Usando Groq. Si ves error 403, cambia a Gemini (recomendado).")
    else:
        with st.expander("🔑 Configurar API de IA (recomendado: Google Gemini)", expanded=True):
            st.markdown("""
            **Opción A — Google Gemini (recomendada, gratis y estable)**
            1. Entra a https://aistudio.google.com/apikey
            2. Pulsa **Create API key** y copia la clave.
            3. En `.streamlit/secrets.toml` agrega: `GEMINI_API_KEY = "AIza..."`
            """)
            col_g, col_q = st.columns(2)
            with col_g:
                g_in = st.text_input("Gemini (temporal)", type="password", placeholder="AIza...")
                if st.button("Usar Gemini", use_container_width=True):
                    st.session_state["gemini_api_key"] = g_in.strip()
                    st.rerun()
            with col_q:
                q_in = st.text_input("Groq (temporal)", type="password", placeholder="gsk_...")
                if st.button("Usar Groq", use_container_width=True):
                    st.session_state["groq_api_key"] = q_in.strip()
                    st.rerun()
        gemini_api_key = leer_secreto("GEMINI_API_KEY") or st.session_state.get("gemini_api_key", "")
        groq_api_key = leer_secreto("GROQ_API_KEY") or st.session_state.get("groq_api_key", "")
        proveedor = "gemini" if gemini_api_key else ("groq" if groq_api_key else None)

    def construir_contexto_dashboard():
        bloques = []
        bloques.append("Eres el asistente oficial del Portal de Supply Chain & S&OP de Sapori.")
        bloques.append("Responde siempre en español, de forma clara y ejecutiva. Usa números con separador de miles punto (ej. 1.234).")
        bloques.append(f"Parámetros de tiempo: días efectivos = {dias_efectivos}, días restantes = {dias_restantes}.")

        # --- MÓDULOS ANTERIORES (INTACTOS) ---
        file_ventas = "data/VINCULO VTS BY SKU.xlsx"
        if os.path.exists(file_ventas):
            try:
                df_kpis = _cargar_ventas_dashboard(file_ventas)
                val_gross = pd.to_numeric(df_kpis.iloc[2, 0], errors='coerce') or 0
                val_forecast = pd.to_numeric(df_kpis.iloc[2, 4], errors='coerce') or 0
                bloques.append(f"\n=== KPIs DE VENTAS Y FORECAST ===")
                bloques.append(f"Total Units Sales Gross: {val_gross:,.0f}".replace(",", "."))
                bloques.append(f"Forecast: {val_forecast:,.0f}".replace(",", "."))
                
                df_vts = _cargar_ventas_matriz(file_ventas)
                bloques.append("\n=== MUESTRA MATRIZ DE VENTAS ===")
                bloques.append(df_vts.head(80).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo ventas: {e}]")
        else: bloques.append("[Archivo ventas no encontrado]")

        file_desv = "data/Comparación de Venta Diaria por SKU (Julio vs Agosto).xlsx"
        if os.path.exists(file_desv):
            try:
                df = _cargar_desviaciones(file_desv)
                bloques.append("\n=== DESVIACIONES ===")
                bloques.append(f"Total SKUs: {len(df)}")
                bloques.append(df.head(60).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo desviaciones: {e}]")

        file_prod = "data/Historico_Produccion_CREMIGURT.xlsx"
        if os.path.exists(file_prod):
            try:
                sheet_names_prod, hojas_prod = _cargar_produccion_todas(file_prod)
                bloques.append(f"\n=== PRODUCCIÓN MENSUAL ===")
                bloques.append(f"Categorías: {', '.join(sheet_names_prod)}")
                for hoja in sheet_names_prod[:8]:
                    df_h = hojas_prod[hoja]
                    bloques.append(f"--- {hoja} ---")
                    bloques.append(df_h.head(15).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo producción: {e}]")

        # --- NUEVOS MÓDULOS INTEGRADOS (M5, M6, M7) ---
        file_cierre = "data/Historico Cierre Inventario Valorizado.xlsx"
        if os.path.exists(file_cierre):
            try:
                hojas_cierre = _cargar_cierre_todas(file_cierre)
                bloques.append(f"\n=== CIERRE DE INVENTARIO VALORIZADO ===")
                for hoja, df_cierre in hojas_cierre.items():
                    bloques.append(f"Mes Cierre: {hoja}")
                    bloques.append(df_cierre.to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo Cierre Valorizado: {e}]")
        else: 
            bloques.append("\n[Archivo Historico Cierre Inventario Valorizado.xlsx no encontrado]")

        file_kpis_fin = "data/Kpis Financieros Inventario.xlsx"
        if os.path.exists(file_kpis_fin):
            try:
                df_kf = _cargar_kpis_fin(file_kpis_fin)
                bloques.append(f"\n=== SALUD FINANCIERA Y RIESGO DE SUMINISTRO ===")
                bloques.append(df_kf.head(40).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo KPIs Financieros: {e}]")
        else: 
            bloques.append("\n[Archivo Kpis Financieros Inventario.xlsx no encontrado]")

        file_sici = "data/Sistema Integral de Control de Inventarios.xlsx"
        if os.path.exists(file_sici):
            try:
                df_sici = _cargar_sici(file_sici)
                bloques.append(f"\n=== SICI: CONTROL DE INVENTARIO MULTICENTRO ===")
                df_sici_clean = df_sici.dropna(how='all') 
                bloques.append(df_sici_clean.head(75).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo SICI: {e}]")
        else: 
            bloques.append("\n[Archivo Sistema Integral de Control de Inventarios.xlsx no encontrado]")

        return "\n".join(bloques)

    def consultar_gemini(pregunta, contexto, api_key):
        modelos = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"]
        ultimo_error = None
        for modelo in modelos:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key.strip()}"
            payload = {
                "system_instruction": {"parts": [{"text": contexto}]},
                "contents": [{"role": "user", "parts": [{"text": pregunta}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500}
            }
            try:
                resp = requests.post(url, json=payload, timeout=60)
                if resp.status_code == 200:
                    return "".join(p.get("text", "") for p in resp.json()["candidates"][0]["content"]["parts"])
                ultimo_error = f"HTTP {resp.status_code}"
                if resp.status_code in (400, 403): break
            except requests.RequestException as e: ultimo_error = str(e)
        raise RuntimeError(f"Revisa tu GEMINI_API_KEY. Error: {ultimo_error}")

    def consultar_groq(pregunta, contexto, api_key):
        modelos_a_probar = ["openai/gpt-oss-20b", "llama-3.1-8b-instant"]
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
        for modelo in modelos_a_probar:
            payload = {"model": modelo, "messages": [{"role": "system", "content": contexto}, {"role": "user", "content": pregunta}], "temperature": 0.2}
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                if resp.status_code == 200: return resp.json()["choices"][0]["message"]["content"]
                if resp.status_code == 401: break
            except: pass
        raise RuntimeError("Fallo con Groq. Intenta con Gemini.")

    if not proveedor: return
    
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    pregunta = st.chat_input("Escribe tu consulta sobre el dashboard...")
    if pregunta:
        st.session_state["chat_messages"].append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            with st.spinner("Analizando datos del dashboard..."):
                try:
                    contexto = construir_contexto_dashboard()
                    respuesta = consultar_gemini(pregunta, contexto, gemini_api_key) if proveedor == "gemini" else consultar_groq(pregunta, contexto, groq_api_key)
                except Exception as e: respuesta = f"❌ No se pudo obtener respuesta: {e}"
            st.markdown(respuesta)
        st.session_state["chat_messages"].append({"role": "assistant", "content": respuesta})

    if st.button("🗑️ Limpiar chat"):
        st.session_state["chat_messages"] = []
        st.rerun()