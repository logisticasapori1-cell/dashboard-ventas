import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y LOGO
# ==========================================
st.set_page_config(layout="wide", page_title="Control de Desviaciones Comerciales", page_icon="📊")

with st.sidebar:
    if os.path.exists("logo_empresa.png"):
        st.image("logo_empresa.png", use_container_width=True)
    st.markdown("---")
    st.markdown("### Parámetros de Análisis")
    st.info("Visualizador oficial para el equipo. Los datos son actualizados por el administrador.")

st.title("📊 Tablero de Control de Desviaciones Comerciales")
st.markdown("### Análisis Comparativo, Financiero y Pareto (ABC) por SKU")

# ==========================================
# CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
file_name = "Comparación de Venta Diaria por SKU (Junio vs Julio).xlsx"

if not os.path.exists(file_name):
    st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
    st.warning("Asegúrate de que el archivo Excel esté en la misma carpeta que este script.")
else:
    try:
        df = pd.read_excel(file_name, sheet_name="Table 1")
        
        for col in ['PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO']:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        
        if 'Porcentaje de desviación' in df.columns:
            df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
        else:
            df['Desviacion_Num'] = ((df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']) / df['PROMD VTA DIA JUNIO']) * 100

        # --- CÁLCULO DE IMPACTO FINANCIERO ---
        tiene_precio = 'PRECIO UNITARIO' in df.columns
        if tiene_precio:
            df['Dif_Unidades_Diarias'] = df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']
            df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
            df['Impacto_Mensual_$'] = df['Impacto_Diario_$'] * 30

        # --- NUEVO: CÁLCULO DE ANÁLISIS ABC (PARETO) ---
        # 1. Ordenar de mayor a menor por el volumen actual (Julio)
        df = df.sort_values(by='PROMD VTA DIA JULIO', ascending=False).reset_index(drop=True)
        # 2. Calcular el porcentaje de participación de cada SKU
        volumen_total_julio = df['PROMD VTA DIA JULIO'].sum()
        df['Porcentaje_Participacion'] = (df['PROMD VTA DIA JULIO'] / volumen_total_julio) * 100
        # 3. Calcular el porcentaje acumulado
        df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()
        # 4. Asignar Categoría ABC
        def asignar_abc(acumulado):
            if acumulado <= 80:
                return 'A'
            elif acumulado <= 95:
                return 'B'
            else:
                return 'C'
        df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

        # ==========================================
        # SECCIÓN 1: KPIs (TARJETAS DE MÉTRICAS)
        # ==========================================
        total_skus = len(df)
        subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
        bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total SKUs", f"{total_skus} Prod.")
        kpi2.metric("SKUs en Alza", f"{subio}", delta=f"+{subio} SKUs", delta_color="inverse")
        kpi3.metric("SKUs en Alerta", f"{bajo}", delta=f"-{bajo} SKUs")
        
        if tiene_precio:
            impacto_total = df['Impacto_Mensual_$'].sum()
            kpi4.metric("Balance Financiero Mensual", f"${impacto_total:,.2f}", delta="Proyección vs Junio")
        else:
            kpi4.metric("Balance Financiero", "Sin Datos")
            
        st.markdown("---")
        
        # ==========================================
        # SECCIÓN 2: FILTROS INTERACTIVOS
        # ==========================================
        # Se agregaron 3 columnas para incluir el nuevo filtro ABC
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_tendencia = st.selectbox("🎯 Estado de Tendencia:", ["Todos", "SUBIÓ", "BAJO"])
        with col_f2:
            filtro_abc = st.selectbox("📊 Clasificación ABC:", ["Todos", "A", "B", "C"])
        with col_f3:
            busqueda = st.text_input("🔍 Buscar SKU o Producto:")
        
        # Aplicación de los filtros al dataframe
        df_filtrado = df.copy()
        
        if filtro_tendencia != "Todos" and 'Estado de tendencia' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Estado de tendencia'] == filtro_tendencia]
            
        if filtro_abc != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Clasificación ABC'] == filtro_abc]
                
        if busqueda:
            df_filtrado = df_filtrado[
                df_filtrado['PRODUCTO'].str.contains(busqueda, case=False, na=False) | 
                df_filtrado['REFERENCIA INTERNA'].astype(str).str.contains(busqueda, na=False)
            ]
        
        # ==========================================
        # SECCIÓN 3: GRÁFICO INTERACTIVO (PLOTLY)
        # ==========================================
        df_grafico = df_filtrado.sort_values(by='PROMD VTA DIA JUNIO', ascending=False)
        
        if not df_grafico.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_grafico['PRODUCTO'], 
                y=df_grafico['PROMD VTA DIA JUNIO'], 
                name='Venta Promedio Junio', 
                marker_color='#1f4e79'
            ))
            fig.add_trace(go.Bar(
                x=df_grafico['PRODUCTO'], 
                y=df_grafico['PROMD VTA DIA JULIO'], 
                name='Venta Promedio Julio', 
                marker_color='#d95f02'
            ))
            
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
        
        # ==========================================
        # SECCIÓN 4: TABLA DE DETALLE ESTILIZADA
        # ==========================================
        st.markdown("---")
        st.markdown("### 📋 Detalle de Ventas, Clasificación ABC e Impacto")
        
        # Se agregó la columna 'Clasificación ABC' para renderizar
        if tiene_precio:
            columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Impacto_Mensual_$', 'Estado de tendencia']
        else:
            columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
        
        def resaltar_tendencia(val):
            if val == 'SUBIÓ':
                return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
            elif val == 'BAJO':
                return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
            return ''
        
        if tiene_precio:
            tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia']).format({'Impacto_Mensual_$': '${:,.2f}'})
        else:
            tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia'])
            
        st.dataframe(tabla_estilizada, use_container_width=True, hide_index=True)

        # ==========================================
        # SECCIÓN 5: DESCARGA EJECUTIVA (EXCEL MEMORIA)
        # ==========================================
        st.markdown("---")
        st.markdown("### 📥 Módulo de Descarga Ejecutiva")
        st.info("Descarga la vista actual (con los filtros aplicados) en un documento formateado y listo para aprobación de gerencia.")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
            worksheet = writer.sheets['Reporte_Filtrado']
            
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter 
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width
            
            max_row = worksheet.max_row
            worksheet.cell(row=max_row + 4, column=1, value="___________________________________")
            worksheet.cell(row=max_row + 5, column=1, value="Firma: Gerencia de Operaciones")
            worksheet.cell(row=max_row + 4, column=3, value="___________________________________")
            worksheet.cell(row=max_row + 5, column=3, value="Firma: Supply Chain / Ventas")

        excel_data = buffer.getvalue()
        
        st.download_button(
            label="📄 Descargar Reporte para Firmas (Excel)",
            data=excel_data,
            file_name="Reporte_Desviaciones_Gerencia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

        # ==========================================
        # SECCIÓN 6: FIRMA DEL AUTOR
        # ==========================================
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "Jair Ramos - Supply Chain</b>"
            "</div>", 
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo Excel: {e}")