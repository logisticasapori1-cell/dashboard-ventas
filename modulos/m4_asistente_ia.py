import streamlit as st
import pandas as pd
import os
import requests

def renderizar(dias_efectivos, dias_restantes):
    st.title("🤖 Asistente de Consultas — Supply Chain & S&OP")
    st.caption("Pregunta en lenguaje natural sobre ventas, forecast, desviaciones, producción y salud financiera.")
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
        with st.expander("🔑 Configurar API de IA", expanded=True):
            st.markdown("""1. Entra a https://aistudio.google.com/apikey y copia tu clave.""")
            col_g, col_q = st.columns(2)
            with col_g:
                g_in = st.text_input("Gemini (temporal)", type="password", placeholder="AIza...")
                if st.button("Usar Gemini", use_container_width=True):
                    st.session_state["gemini_api_key"] = g_in.strip()
                    st.rerun()
        gemini_api_key = leer_secreto("GEMINI_API_KEY") or st.session_state.get("gemini_api_key", "")
        proveedor = "gemini" if gemini_api_key else None

    # --- NUEVO: BUSCADOR INTELIGENTE DE ARCHIVOS ---
    def encontrar_archivo(nombre_archivo):
        directorio = "data"
        if not os.path.exists(directorio): return None
        for f in os.listdir(directorio):
            # Compara ignorando mayúsculas, minúsculas y espacios extra
            if f.strip().lower() == nombre_archivo.strip().lower():
                return os.path.join(directorio, f)
        return None

    def construir_contexto_dashboard():
        bloques = []
        bloques.append("Eres el asistente oficial y analista financiero del Portal de Supply Chain de Sapori.")
        bloques.append("Responde de forma clara y ejecutiva. Usa el punto para separar miles.")
        bloques.append("IMPORTANTE: Si en tus instrucciones ves que dice '[ARCHIVO NO ENCONTRADO]', debes decirle al usuario exactamente qué archivo falta en la base de datos para que pueda revisarlo.")
        bloques.append(f"Parámetros de tiempo: días efectivos = {dias_efectivos}, días restantes = {dias_restantes}.")

        # 1. Ventas
        file_ventas = encontrar_archivo("VINCULO VTS BY SKU.xlsx")
        if file_ventas:
            try:
                df_kpis = pd.read_excel(file_ventas, sheet_name="DASHBOARD", header=None)
                val_gross = pd.to_numeric(df_kpis.iloc[2, 0], errors='coerce') or 0
                val_forecast = pd.to_numeric(df_kpis.iloc[2, 4], errors='coerce') or 0
                bloques.append(f"\n=== KPIs DE VENTAS Y FORECAST ===")
                bloques.append(f"Total Units Sales Gross: {val_gross:,.0f}".replace(",", "."))
                bloques.append(f"Forecast: {val_forecast:,.0f}".replace(",", "."))
                df_vts = pd.read_excel(file_ventas, sheet_name="file_ventas")
                bloques.append("\n=== MUESTRA MATRIZ DE VENTAS ===")
                bloques.append(df_vts.head(80).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo ventas: {e}]")
        else: bloques.append("[ARCHIVO NO ENCONTRADO: VINCULO VTS BY SKU.xlsx]")

        # 2. Desviaciones
        file_desv = encontrar_archivo("Comparación de Venta Diaria por SKU (Julio vs Agosto).xlsx")
        if file_desv:
            try:
                df = pd.read_excel(file_desv, sheet_name="Table 1")
                bloques.append("\n=== DESVIACIONES ===")
                bloques.append(df.head(60).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo desviaciones: {e}]")
        else: bloques.append("[ARCHIVO NO ENCONTRADO: Comparación de Venta Diaria por SKU (Julio vs Agosto).xlsx]")

        # 3. Producción
        file_prod = encontrar_archivo("Historico_Produccion_CREMIGURT.xlsx")
        if file_prod:
            try:
                xls = pd.ExcelFile(file_prod)
                bloques.append(f"\n=== PRODUCCIÓN MENSUAL ===")
                for hoja in xls.sheet_names[:8]:
                    df_h = pd.read_excel(xls, sheet_name=hoja)
                    bloques.append(f"--- {hoja} ---")
                    bloques.append(df_h.head(15).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo producción: {e}]")
        else: bloques.append("[ARCHIVO NO ENCONTRADO: Historico_Produccion_CREMIGURT.xlsx]")

        # 4. Módulo 5 (Cierre Inventario)
        file_cierre = encontrar_archivo("Historico Cierre Inventario Valorizado.xlsx")
        if file_cierre:
            try:
                xls_cierre = pd.ExcelFile(file_cierre)
                bloques.append(f"\n=== CIERRE DE INVENTARIO VALORIZADO ===")
                for hoja in xls_cierre.sheet_names:
                    df_cierre = pd.read_excel(xls_cierre, sheet_name=hoja)
                    bloques.append(f"Mes Cierre: {hoja}")
                    bloques.append(df_cierre.to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo Cierre Valorizado: {e}]")
        else: bloques.append("[ARCHIVO NO ENCONTRADO: Historico Cierre Inventario Valorizado.xlsx]")

        # 5. Módulo 6 (KPIs Financieros)
        file_kpis_fin = encontrar_archivo("Kpis Financieros Inventario.xlsx")
        if file_kpis_fin:
            try:
                df_kf = pd.read_excel(file_kpis_fin, sheet_name=0, header=None)
                bloques.append(f"\n=== SALUD FINANCIERA Y RIESGO DE SUMINISTRO (KPIs) ===")
                bloques.append(df_kf.head(40).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo KPIs Financieros: {e}]")
        else: bloques.append("[ARCHIVO NO ENCONTRADO: Kpis Financieros Inventario.xlsx]")

        # 6. Módulo 7 (SICI)
        file_sici = encontrar_archivo("Sistema Integral de Control de Inventarios.xlsx")
        if file_sici:
            try:
                df_sici = pd.read_excel(file_sici, sheet_name=0, header=None)
                bloques.append(f"\n=== SICI: CONTROL DE INVENTARIO MULTICENTRO (RED SAPORI) ===")
                df_sici_clean = df_sici.dropna(how='all') 
                bloques.append(df_sici_clean.head(75).to_string(index=False))
            except Exception as e: bloques.append(f"[Error leyendo SICI: {e}]")
        else: bloques.append("[ARCHIVO NO ENCONTRADO: Sistema Integral de Control de Inventarios.xlsx]")

        return "\n".join(bloques)

    def consultar_gemini(pregunta, contexto, api_key):
        # Usamos los modelos más rápidos y estables. 'gemini-pro' es el comodín universal que nunca falla.
        modelos = ["gemini-1.5-flash", "gemini-pro"]
        errores = []
        
        # TÁCTICA BLINDADA: Combinamos el contexto y la pregunta en un solo bloque. 
        # Así evitamos pelear con los parámetros cambiantes de "systemInstruction" de Google.
        prompt_completo = f"INSTRUCCIONES DEL SISTEMA Y BASE DE DATOS:\n{contexto}\n\nPREGUNTA DEL GERENTE:\n{pregunta}"
        
        for modelo in modelos:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key.strip()}"
            
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt_completo}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500}
            }
            try:
                headers = {'Content-Type': 'application/json'}
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if resp.status_code == 200:
                    return "".join(p.get("text", "") for p in resp.json()["candidates"][0]["content"]["parts"])
                
                # Si falla, guardamos el error para depurar pero continuamos con el siguiente modelo
                errores.append(f"{modelo} ({resp.status_code})")
                
            except requests.RequestException as e: 
                errores.append(f"{modelo}: Error de red")
                
        # Si todos los modelos fallan, mostramos exactamente por qué falló cada uno
        raise RuntimeError(f"Fallo al conectar con Gemini. Detalles de los intentos: {' | '.join(errores)}")

    if not proveedor: return
    
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    pregunta = st.chat_input("Escribe tu consulta sobre el dashboard...")
    if pregunta:
        st.session_state["chat_messages"].append({"role": "user", "content": pregunta})
        with st.chat_message("user"): st.markdown(pregunta)
        with st.chat_message("assistant"):
            with st.spinner("Analizando base de datos de la red Sapori..."):
                try:
                    contexto = construir_contexto_dashboard()
                    # Muestra un pequeño mensaje temporal indicando que terminó de leer
                    st.toast("Datos cargados. Procesando respuesta...") 
                    respuesta = consultar_gemini(pregunta, contexto, gemini_api_key)
                except Exception as e: respuesta = f"❌ Error interno: {e}"
            st.markdown(respuesta)
        st.session_state["chat_messages"].append({"role": "assistant", "content": respuesta})

    if st.button("🗑️ Limpiar chat"):
        st.session_state["chat_messages"] = []
        st.rerun()