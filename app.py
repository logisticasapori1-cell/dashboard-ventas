import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuración de la interfaz
st.set_page_config(layout="wide", page_title="Control de Desviaciones Comerciales", page_icon="📊")
# --- LOGO DE LA EMPRESA ---
with st.sidebar:
    st.image("logosapori.png", width=200)
    st.markdown("---") # Una línea divisoria después del logo

st.title("📊 Tablero de Control de Desviaciones Comerciales Sapori")
st.markdown("### Análisis Comparativo de Venta Diaria por SKU (Junio vs Julio)")
st.info("Visualizador oficial para el equipo. Los datos son actualizados periódicamente por el administrador.")

# Nombre del archivo excel esperado
file_name = "Comparación de Venta Diaria por SKU (Junio vs Julio).xlsx"

if not os.path.exists(file_name):
    st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
else:
    try:
        # Carga de datos
        df = pd.read_excel(file_name, sheet_name="Table 1")
        
        # Limpieza de tipos de datos
        for col in ['PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO']:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        
        # Columna de ordenamiento interno
        if 'Porcentaje de desviación' in df.columns:
            df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
        else:
            df['Desviacion_Num'] = ((df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']) / df['PROMD VTA DIA JUNIO']) * 100

        # --- SECCIÓN 1: METRICAS CLAVE (KPIs) ---
        total_skus = len(df)
        subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
        bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total SKUs Monitoreados", f"{total_skus} Productos")
        kpi2.metric("SKUs con Crecimiento (SUBIÓ)", f"{subio}", delta=f"+{subio} SKUs", delta_color="normal")
        kpi3.metric("SKUs en Alerta (BAJO)", f"{bajo}", delta=f"-{bajo} SKUs", delta_color="normal")
        
        st.markdown("---")
        
        # --- SECCIÓN 2: FILTROS INTERACTIVOS ---
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_tendencia = st.selectbox("🎯 Filtrar por Estado de Tendencia:", ["Todos", "SUBIÓ", "BAJO"])
        with col_f2:
            busqueda = st.text_input("🔍 Buscar por Nombre de Producto o Referencia:")
        
        # Aplicación de los filtros
        df_filtrado = df.copy()
        if filtro_tendencia != "Todos":
            if 'Estado de tendencia' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Estado de tendencia'] == filtro_tendencia]
                
        if busqueda:
            df_filtrado = df_filtrado[
                df_filtrado['PRODUCTO'].str.contains(busqueda, case=False, na=False) | 
                df_filtrado['REFERENCIA INTERNA'].astype(str).str.contains(busqueda, na=False)
            ]
        
        # --- SECCIÓN 3: GRÁFICO INTERACTIVO ---
        df_grafico = df_filtrado.sort_values(by='PROMD VTA DIA JUNIO', ascending=False)
        
        if not df_grafico.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico['PROMD VTA DIA JUNIO'], name='Venta Promedio Junio', marker_color='#1f4e79'))
            fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico['PROMD VTA DIA JULIO'], name='Venta Promedio Julio', marker_color='#d95f02'))
            
            fig.update_layout(
                barmode='group',
                title="<b>Comparativa del Volumen de Venta Diaria por SKU</b>",
                xaxis_title="Productos (SKUs)",
                yaxis_title="Unidades / Día",
                height=500,
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01),
                margin=dict(l=40, r=40, t=80, b=120)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No se encontraron productos que coincidan con tu búsqueda.")
        
        # --- SECCIÓN 4: TABLA DE DETALLE ---
        st.markdown("---")
        st.markdown("### 📋 Detalle de Ventas y Desviaciones")
        
        columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
        
        def resaltar_tendencia(val):
            if val == 'SUBIÓ':
                return 'background-color: #e2f0d9; color: #385723; font-weight: bold;' # Rojo/Naranja de alerta constante con tu KPI
            elif val == 'BAJO':
                return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
            return ''
            
        st.dataframe(
            df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia']), 
            use_container_width=True, 
            hide_index=True
        )

        # --- SECCIÓN DE FIRMA ---
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "Elaborado por: <b>Jair Ramos - Planificador de Materiales</b>"
            "</div>", 
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo Excel: {e}")