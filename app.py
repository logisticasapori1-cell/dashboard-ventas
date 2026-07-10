import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y LOGO
# ==========================================
st.set_page_config(layout="wide", page_title="Control de Desviaciones Comerciales", page_icon="📊")

# Agregar Logo en la barra lateral (si existe el archivo)
with st.sidebar:
    if os.path.exists("logosapori.png"):
        st.image("logosapori.png", use_container_width=True)
    st.markdown("---")
    st.markdown("### Parámetros de Análisis")
    st.info("Visualizador oficial para el equipo. Los datos son actualizados por el administrador.")

# Títulos principales
st.title("📊 Tablero de Control de Desviaciones Comerciales")
st.markdown("### Análisis Comparativo y Financiero por SKU (Junio vs Julio)")

# ==========================================
# CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
file_name = "Comparación de Venta Diaria por SKU (Junio vs Julio).xlsx"

if not os.path.exists(file_name):
    st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
    st.warning("Asegúrate de que el archivo Excel esté en la misma carpeta que este script.")
else:
    try:
        # Cargar datos
        df = pd.read_excel(file_name, sheet_name="Table 1")
        
        # Limpiar formatos de miles y decimales si vienen como texto
        for col in ['PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO']:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        
        # Calcular porcentaje de desviación numérico para ordenamientos internos
        if 'Porcentaje de desviación' in df.columns:
            df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
        else:
            df['Desviacion_Num'] = ((df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']) / df['PROMD VTA DIA JUNIO']) * 100

        # --- CÁLCULO DE IMPACTO FINANCIERO ---
        tiene_precio = 'PRECIO UNITARIO' in df.columns
        if tiene_precio:
            # Calcular la diferencia en unidades diarias
            df['Dif_Unidades_Diarias'] = df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']
            # Calcular el impacto diario en moneda
            df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
            # Proyectar el impacto al mes completo (30 días)
            df['Impacto_Mensual_$'] = df['Impacto_Diario_$'] * 30
        else:
            st.warning("⚠️ **Aviso:** Para ver el impacto financiero, agrega una columna llamada 'PRECIO UNITARIO' a tu archivo Excel original.")

        # ==========================================
        # SECCIÓN 1: KPIs (TARJETAS DE MÉTRICAS)
        # ==========================================
        total_skus = len(df)
        subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
        bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total SKUs", f"{total_skus} Prod.")
        
        # KPI en rojo para incrementos (según configuración anterior)
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
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_tendencia = st.selectbox("🎯 Filtrar por Estado de Tendencia:", ["Todos", "SUBIÓ", "BAJO"])
        with col_f2:
            busqueda = st.text_input("🔍 Buscar por Nombre de Producto o Referencia:")
        
        # Aplicación de los filtros al dataframe
        df_filtrado = df.copy()
        if filtro_tendencia != "Todos":
            if 'Estado de tendencia' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Estado de tendencia'] == filtro_tendencia]
                
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
        st.markdown("### 📋 Detalle de Ventas, Desviaciones e Impacto")
        
        if tiene_precio:
            columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Impacto_Mensual_$', 'Estado de tendencia']
        else:
            columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
        
        # Función de colores invertida según solicitud: SUBIÓ (Verde), BAJO (Rojo)
        def resaltar_tendencia(val):
            if val == 'SUBIÓ':
                return 'background-color: #e2f0d9; color: #385723; font-weight: bold;' # Verde
            elif val == 'BAJO':
                return 'background-color: #fce4d6; color: #c65911; font-weight: bold;' # Rojo/Naranja
            return ''
        
        # Aplicar formato de colores y moneda (si existe el precio)
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
            # Escribir la tabla filtrada al Excel
            df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
            worksheet = writer.sheets['Reporte_Filtrado']
            
            # Ajustar anchos de columna dinámicamente
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
            
            # Bloque de Firmas al final de los datos
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
            "<div style='text-align: center; color: #555;'>"
            "<strong>Jair Ramos</strong><br> <small>Supply Chain Planning - Sapori</small>"
            "</div>", 
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo Excel: {e}")