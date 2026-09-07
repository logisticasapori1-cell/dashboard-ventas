import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

@st.cache_data
def _cargar_sici(path):
    return pd.read_excel(path, sheet_name=0, header=None)

def renderizar():
    st.markdown("# 🌍 Sistema Integral de Control Multicentro (SICI)")
    st.caption("Visión Global · Coberturas por CEDIS · Eficiencia Logística")

    file_path = "data/Sistema Integral de Control de Inventarios.xlsx"
    if not os.path.exists(file_path):
        st.error(f"❌ **Archivo requerido no encontrado:** '{file_path}'")
        return
        
    try:
        # Cargar datos sin cabecera para extraer métricas y tablas dinámicamente
        df_raw = _cargar_sici(file_path)
        
        # --- 1. EXTRACCIÓN INTELIGENTE DE TOTALES (Incluyendo Zulia en el índice +5 y Total en +6) ---
        idx_val = df_raw[df_raw[1] == 'VALORIZADO'].index[0]
        idx_inv = df_raw[df_raw[1] == 'INVENTARIO'].index[0]
        
        val_ccs = pd.to_numeric(df_raw.iloc[idx_val+1, 3], errors='coerce')
        val_car = pd.to_numeric(df_raw.iloc[idx_val+2, 3], errors='coerce')
        val_ori = pd.to_numeric(df_raw.iloc[idx_val+3, 3], errors='coerce')
        val_lar = pd.to_numeric(df_raw.iloc[idx_val+4, 3], errors='coerce')
        val_zul = pd.to_numeric(df_raw.iloc[idx_val+5, 3], errors='coerce')
        val_total = pd.to_numeric(df_raw.iloc[idx_val+6, 3], errors='coerce')
        
        inv_ccs = pd.to_numeric(df_raw.iloc[idx_inv+1, 3], errors='coerce')
        inv_car = pd.to_numeric(df_raw.iloc[idx_inv+2, 3], errors='coerce')
        inv_ori = pd.to_numeric(df_raw.iloc[idx_inv+3, 3], errors='coerce')
        inv_lar = pd.to_numeric(df_raw.iloc[idx_inv+4, 3], errors='coerce')
        inv_zul = pd.to_numeric(df_raw.iloc[idx_inv+5, 3], errors='coerce')
        inv_total = pd.to_numeric(df_raw.iloc[idx_inv+6, 3], errors='coerce')
        
        def formato_dinero(x):
            if pd.isna(x): return "-"
            return f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        def formato_entero(x):
            if pd.isna(x): return "-"
            return f"{x:,.0f}".replace(",", ".")

        # --- SECCIÓN 1: CABECERA MACRO (Matriz adaptada a los 5 CEDIS + Total) ---
        st.markdown('<div class="module-header">SÍNTESIS GLOBAL DE CAPITAL E INVENTARIO</div>', unsafe_allow_html=True)
        
        # Fila 1: Total Global, Caracas y Carabobo
        f1_c1, f1_c2, f1_c3 = st.columns(3)
        f1_c1.metric("🌍 TOTAL CIDES (USD)", formato_dinero(val_total), f"{formato_entero(inv_total)} Unds Físicas")
        f1_c2.metric("🏭 Caracas (USD)", formato_dinero(val_ccs), f"{formato_entero(inv_ccs)} Unds")
        f1_c3.metric("🏭 Carabobo (USD)", formato_dinero(val_car), f"{formato_entero(inv_car)} Unds")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fila 2: Oriente, Lara y Zulia
        f2_c1, f2_c2, f2_c3 = st.columns(3)
        f2_c1.metric("🌅 Oriente (USD)", formato_dinero(val_ori), f"{formato_entero(inv_ori)} Unds")
        f2_c2.metric("🎸 Lara (USD)", formato_dinero(val_lar), f"{formato_entero(inv_lar)} Unds")
        f2_c3.metric("☀️ Zulia (USD)", formato_dinero(val_zul), f"{formato_entero(inv_zul)} Unds")
        
        st.markdown("---")
        
        # Gráficos de Dona para los 5 CEDIs
        col_d1, col_d2 = st.columns(2)
        labels_cedis = ["Caracas", "Carabobo", "Oriente", "Lara", "Zulia"]
        colores_cedis = ['#1a3a5c', '#fa7d2a', '#dc2626', '#16a34a', '#8b5cf6']
        
        with col_d1:
            fig_val = go.Figure(data=[go.Pie(labels=labels_cedis, values=[val_ccs, val_car, val_ori, val_lar, val_zul], hole=.5, marker_colors=colores_cedis)])
            fig_val.update_layout(title_text="Distribución de Capital (USD)", margin=dict(t=40, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig_val, use_container_width=True)
            
        with col_d2:
            fig_inv = go.Figure(data=[go.Pie(labels=labels_cedis, values=[inv_ccs, inv_car, inv_ori, inv_lar, inv_zul], hole=.5, marker_colors=colores_cedis)])
            fig_inv.update_layout(title_text="Distribución Física (Unidades)", margin=dict(t=40, b=10, l=0, r=0), height=300)
            st.plotly_chart(fig_inv, use_container_width=True)

        # --- SECCIÓN 2: CONTROL MULTICENTRO (SELECTBOX) ---
        st.markdown("---")
        st.markdown("### 🎛️ Centro de Mando Logístico")
        
        centro_seleccionado = st.selectbox(
            "Seleccione la Vista Operativa (CEDIS):",
            [
                "🌐 Visión Global (Consolidado SICI)", 
                "🏢 CEDIS Caracas", 
                "🏭 CEDIS Carabobo", 
                "🌅 CEDIS Oriente", 
                "🎸 CEDIS Lara",
                "☀️ CEDIS Zulia"
            ]
        )
        
        # Recortar solo las filas de productos (desde la fila 11)
        df_tabla_raw = df_raw.iloc[12:idx_val-2].copy()
        
        # Lógicas de Semáforos Corporativos seguros
        def semaforo_cobertura(val):
            try:
                v = float(val)
                if v < 7: return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                elif v <= 15: return 'background-color: #fff2cc; color: #7f6000; font-weight: bold;'
                else: return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
            except: return ''
            
        def semaforo_eficiencia(val):
            try:
                v = float(val)
                if v < 0.70: return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                elif v <= 0.95: return 'background-color: #fff2cc; color: #7f6000; font-weight: bold;'
                else: return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
            except: return ''

        # Renderizado Dinámico
        if centro_seleccionado == "🌐 Visión Global (Consolidado SICI)":
            cols = [1, 2, 29, 30, 31, 32, 33] # Nuevas coordenadas globales con Zulia
            df_render = df_tabla_raw[cols].copy()
            df_render.columns = ["SKU", "Producto", "Existencia Total", "Valor Total ($)", "Demanda Promedio", "Cobertura (Días)", "Eficiencia SICI"]
            
            # Asegurar conversión numérica para evitar errores de formato
            for col in ["Existencia Total", "Valor Total ($)", "Demanda Promedio", "Cobertura (Días)", "Eficiencia SICI"]:
                df_render[col] = pd.to_numeric(df_render[col], errors='coerce')

            st.dataframe(
                df_render.style
                .map(semaforo_cobertura, subset=['Cobertura (Días)'])
                .map(semaforo_eficiencia, subset=['Eficiencia SICI'])
                .format({
                    "Existencia Total": lambda x: formato_entero(x),
                    "Valor Total ($)": lambda x: formato_dinero(x),
                    "Demanda Promedio": lambda x: formato_entero(x),
                    "Cobertura (Días)": lambda x: f"{x:.1f}" if pd.notnull(x) else "-",
                    "Eficiencia SICI": lambda x: f"{x:.0%}" if pd.notnull(x) else "-"
                }),
                use_container_width=True, hide_index=True
            )
            
        else:
            mapa_cols = {
                "🏢 CEDIS Caracas": [4, 5, 6, 7, 8],
                "🏭 CEDIS Carabobo": [9, 10, 11, 12, 13],
                "🌅 CEDIS Oriente": [14, 15, 16, 17, 18],
                "🎸 CEDIS Lara": [19, 20, 21, 22, 23],
                "☀️ CEDIS Zulia": [24, 25, 26, 27, 28]
            }
            
            cols_base = [1, 2]
            cols_extra = mapa_cols[centro_seleccionado]
            
            df_render = df_tabla_raw[cols_base + cols_extra].copy()
            df_render.columns = ["SKU", "Producto", "Existencia Local", "Valor Local ($)", "Cobertura (Días)", "Demanda Mensual", "Balance"]
            
            # Asegurar conversión numérica
            for col in ["Existencia Local", "Valor Local ($)", "Cobertura (Días)", "Demanda Mensual", "Balance"]:
                df_render[col] = pd.to_numeric(df_render[col], errors='coerce')

            st.dataframe(
                df_render.style
                .map(semaforo_cobertura, subset=['Cobertura (Días)'])
                .format({
                    "Existencia Local": lambda x: formato_entero(x),
                    "Valor Local ($)": lambda x: formato_dinero(x),
                    "Cobertura (Días)": lambda x: f"{x:.1f}" if pd.notnull(x) else "-",
                    "Demanda Mensual": lambda x: formato_entero(x),
                    "Balance": lambda x: formato_entero(x)
                }),
                use_container_width=True, hide_index=True
            )

    except Exception as e:
        st.error(f"Error analizando la estructura del Excel SICI: {e}")