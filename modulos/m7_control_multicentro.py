import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

def renderizar():
    st.title("🌍 Sistema Integral de Control Multicentro (SICI)")
    st.caption("Visión Global · Coberturas por CEDIS · Eficiencia Logística")

    file_path = "data/Sistema Integral de Control de Inventarios.xlsx"
    if not os.path.exists(file_path):
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_path}'")
        return
        
    try:
        # Cargar datos sin cabecera para poder extraer métricas y tablas dinámicamente
        df_raw = pd.read_excel(file_path, sheet_name=0, header=None)
        
        # --- 1. EXTRACCIÓN INTELIGENTE DE TOTALES ---
        # Buscamos exactamente dónde están los resúmenes financieros para que no se 
        # rompa si en el futuro agregas más filas de productos.
        idx_val = df_raw[df_raw[1] == 'VALORIZADO'].index[0]
        idx_inv = df_raw[df_raw[1] == 'INVENTARIO'].index[0]
        
        # Extraer totales Valorizados (Se encuentran en la columna 3 del DataFrame crudo)
        val_ccs = pd.to_numeric(df_raw.iloc[idx_val+1, 3], errors='coerce')
        val_car = pd.to_numeric(df_raw.iloc[idx_val+2, 3], errors='coerce')
        val_ori = pd.to_numeric(df_raw.iloc[idx_val+3, 3], errors='coerce')
        val_lar = pd.to_numeric(df_raw.iloc[idx_val+4, 3], errors='coerce')
        val_total = pd.to_numeric(df_raw.iloc[idx_val+5, 3], errors='coerce')
        
        # Extraer totales Inventario Físico
        inv_ccs = pd.to_numeric(df_raw.iloc[idx_inv+1, 3], errors='coerce')
        inv_car = pd.to_numeric(df_raw.iloc[idx_inv+2, 3], errors='coerce')
        inv_ori = pd.to_numeric(df_raw.iloc[idx_inv+3, 3], errors='coerce')
        inv_lar = pd.to_numeric(df_raw.iloc[idx_inv+4, 3], errors='coerce')
        inv_total = pd.to_numeric(df_raw.iloc[idx_inv+5, 3], errors='coerce')

        def formato_dinero(x):
            if pd.isna(x): return "-"
            return f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        def formato_entero(x):
            if pd.isna(x): return "-"
            return f"{x:,.0f}".replace(",", ".")

        # --- SECCIÓN 1: CABECERA MACRO ---
        st.markdown('<div class="module-header">SÍNTESIS GLOBAL DE CAPITAL E INVENTARIO</div>', unsafe_allow_html=True)
        
        # Dividimos en 5 columnas para mostrar el Total y el desglose por CEDIS
        c_tot, c_ccs, c_car, c_ori, c_lar = st.columns(5)
        
        # Columna 1: Total Red
        c_tot.metric("TOTAL RED (USD)", formato_dinero(val_total))
        c_tot.metric("Unidades Totales", formato_entero(inv_total))
        
        # Columna 2: Caracas
        c_ccs.metric("🏢 Caracas (USD)", formato_dinero(val_ccs))
        c_ccs.metric("Unds. Caracas", formato_entero(inv_ccs))
        
        # Columna 3: Carabobo
        c_car.metric("🏭 Carabobo (USD)", formato_dinero(val_car))
        c_car.metric("Unds. Carabobo", formato_entero(inv_car))
        
        # Columna 4: Oriente
        c_ori.metric("🌅 Oriente (USD)", formato_dinero(val_ori))
        c_ori.metric("Unds. Oriente", formato_entero(inv_ori))
        
        # Columna 5: Lara
        c_lar.metric("🎸 Lara (USD)", formato_dinero(val_lar))
        c_lar.metric("Unds. Lara", formato_entero(inv_lar))
        
        st.markdown("---")
        
        # Gráficos de Dona para representar las particiones financieras
        col_d1, col_d2 = st.columns(2)
        labels_cedis = ["Caracas", "Carabobo", "Oriente", "Lara"]
        colores_cedis = ['#1a3a5c', '#e8a317', '#dc2626', '#16a34a']
        
        with col_d1:
            fig_val = go.Figure(data=[go.Pie(labels=labels_cedis, values=[val_ccs, val_car, val_ori, val_lar], hole=.5, marker_colors=colores_cedis)])
            fig_val.update_layout(title_text="Distribución de Capital (USD)", margin=dict(t=40, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig_val, use_container_width=True)
            
        with col_d2:
            fig_inv = go.Figure(data=[go.Pie(labels=labels_cedis, values=[inv_ccs, inv_car, inv_ori, inv_lar], hole=.5, marker_colors=colores_cedis)])
            fig_inv.update_layout(title_text="Distribución Física (Unidades)", margin=dict(t=40, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig_inv, use_container_width=True)

        # --- SECCIÓN 2: CONTROL MULTICENTRO (SELECTBOX) ---
        st.markdown("---")
        st.markdown("### 🎛️ Centro de Mando Logístico")
        
        # Aquí implementamos el Dropdown moderno que solicitaste
        centro_seleccionado = st.selectbox(
            "Seleccione la Vista Operativa (CEDIS):",
            [
                "🌐 Visión Global (Consolidado SICI)", 
                "🏢 CEDIS Caracas", 
                "🏭 CEDIS Carabobo", 
                "🌅 CEDIS Oriente", 
                "🎸 CEDIS Lara"
            ]
        )
        
        # Recortar solo las filas de productos (fila 12 hasta donde inician los totales)
        df_tabla_raw = df_raw.iloc[12:idx_val-2].copy()
        
        # Lógicas de Semáforos Corporativos
        def semaforo_cobertura(val):
            try:
                v = float(val)
                if v < 7: return 'background-color: #fce4d6; color: #c65911; font-weight: bold;' # Crítico (< 7 días)
                elif v <= 15: return 'background-color: #fff2cc; color: #7f6000; font-weight: bold;' # Alerta (7 a 15 días)
                else: return 'background-color: #e2f0d9; color: #385723; font-weight: bold;' # Sano (> 15 días)
            except: return ''
            
        def semaforo_eficiencia(val):
            try:
                v = float(val)
                if v < 0.70: return 'background-color: #fce4d6; color: #c65911; font-weight: bold;' # Pobre (< 70%)
                elif v <= 0.95: return 'background-color: #fff2cc; color: #7f6000; font-weight: bold;' # Regular (70-95%)
                else: return 'background-color: #e2f0d9; color: #385723; font-weight: bold;' # Óptimo (> 95%)
            except: return ''

        # Renderizado Dinámico según selección del Selectbox
        if centro_seleccionado == "🌐 Visión Global (Consolidado SICI)":
            cols = [1, 2, 24, 25, 26, 27, 28] # Coordenadas de las columnas globales en tu Excel
            df_render = df_tabla_raw[cols].copy()
            df_render.columns = ["SKU", "Producto", "Existencia Total", "Valor Total ($)", "Demanda Promedio", "Cobertura (Días)", "Eficiencia SICI"]
            
            st.dataframe(
                df_render.style
                .map(semaforo_cobertura, subset=['Cobertura (Días)'])
                .map(semaforo_eficiencia, subset=['Eficiencia SICI'])
                .format({
                    "Existencia Total": formato_entero,
                    "Valor Total ($)": formato_dinero,
                    "Demanda Promedio": formato_entero,
                    "Cobertura (Días)": "{:.1f}",
                    "Eficiencia SICI": "{:.0%}"
                }, na_rep="Sin datos"),
                use_container_width=True, hide_index=True
            )
            
        else:
            # Mapa de coordenadas para extraer solo lo relevante a cada CEDIS
            mapa_cols = {
                "🏢 CEDIS Caracas": [4, 5, 6, 7, 8],
                "🏭 CEDIS Carabobo": [9, 10, 11, 12, 13],
                "🌅 CEDIS Oriente": [14, 15, 16, 17, 18],
                "🎸 CEDIS Lara": [19, 20, 21, 22, 23]
            }
            
            cols_base = [1, 2] # SKU y Producto siempre visibles
            cols_extra = mapa_cols[centro_seleccionado]
            
            df_render = df_tabla_raw[cols_base + cols_extra].copy()
            df_render.columns = ["SKU", "Producto", "Existencia Local", "Valor Local ($)", "Cobertura (Días)", "Demanda Mensual", "Balance"]
            
            st.dataframe(
                df_render.style
                .map(semaforo_cobertura, subset=['Cobertura (Días)'])
                .format({
                    "Existencia Local": formato_entero,
                    "Valor Local ($)": formato_dinero,
                    "Cobertura (Días)": "{:.1f}",
                    "Demanda Mensual": formato_entero,
                    "Balance": formato_entero
                }, na_rep="Sin datos"),
                use_container_width=True, hide_index=True
            )

    except Exception as e:
        st.error(f"Error analizando la estructura del Excel SICI: {e}")