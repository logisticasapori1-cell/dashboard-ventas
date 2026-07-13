import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(layout="wide", page_title="Control de Desviaciones - Sapori", page_icon="🔒")

# Inicializar el estado de autenticación en la sesión
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# ==========================================
# MÓDULO DE ACCESO / LOGIN (CARA PRINCIPAL)
# ==========================================
if not st.session_state['autenticado']:
    # Ocultar la barra lateral predeterminada durante el login
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )

    col_izq, col_centro, col_der = st.columns([1, 1.5, 1])
    
    with col_centro:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #1f4e79; font-family: Arial;'>SAPORI</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='text-align: center; color: #2b2b2b; font-family: Arial; margin-top:0px;'>Control de Desviaciones Comerciales</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Portal Oficial de Análisis Operativo y Cadena de Suministro</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("formulario_login"):
            st.markdown("##### 🔐 Ingrese sus credenciales corporativas")
            usuario = st.text_input("Usuario o Correo Institucional", placeholder="ej. gerencia.operaciones")
            contrasena = st.text_input("Contraseña del Sistema", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            boton_ingresar = st.form_submit_button("Acceder al Tablero", type="primary", use_container_width=True)
            
            if boton_ingresar:
                if usuario == "admin" and contrasena == "sapori2026":
                    st.session_state['autenticado'] = True
                    st.success("✅ Acceso concedido. Inicializando entorno...")
                    st.rerun()
                elif usuario == "" or contrasena == "":
                    st.warning("⚠️ Por favor, complete todos los campos obligatorios.")
                else:
                    st.error("❌ Credenciales incorrectas. Verifique e intente de nuevo.")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(
            "⚠️ **Aviso de Confidencialidad:** Este sistema contiene información estratégica de propiedad exclusiva "
            "de Sapori. El acceso no autorizado, distribución o uso indebido de estos datos de inventario y ventas "
            "está estrictamente prohibido y sujeto a las normativas de la Dirección de la Empresa."
        )
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #888; font-size: 12px; font-family: Arial;'>"
            "© 2026 Sapori | Dirección de Supply Chain & Operaciones<br>"
            "Soporte Técnico: TI-Planta | Versión del Sistema: 2.6"
            "</div>", 
            unsafe_allow_html=True
        )

# ==========================================
# TABLERO PRINCIPAL (ACCESO AUTORIZADO)
# ==========================================
else:
    with st.sidebar:
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)
        st.markdown("---")
        st.markdown("### 👤 Usuario Conectado")
        st.success("Rol: **Administrador / Gerencia**")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()
            
        st.markdown("---")
        st.markdown("### Parámetros de Análisis")
        st.info("Los datos son consolidados periódicamente a partir de las matrices de Supply Chain.")

    st.title("📊 Tablero de Control de Desviaciones Comerciales")
    st.markdown("### Análisis Comparativo, Financiero, Categorías y Pareto (ABC) por SKU")

    file_name = "Comparación de Venta Diaria por SKU (Junio vs Julio).xlsx"

    if not os.path.exists(file_name):
        st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
        st.warning("Asegúrate de que la matriz de datos Excel se encuentre en la raíz del repositorio.")
    else:
        try:
            df = pd.read_excel(file_name, sheet_name="Table 1")
            
            # --- VALIDACIÓN DE LA NUEVA COLUMNA DE CATEGORÍA/MARCA ---
            if 'CATEGORÍA' not in df.columns:
                df['CATEGORÍA'] = "Por Asignar"
                st.sidebar.warning("⚠️ La columna 'CATEGORÍA' no existe en el Excel. Agrega una columna llamada 'CATEGORÍA' en tu archivo para ver las marcas.")

            for col in ['PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO']:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
            
            if 'Porcentaje de desviación' in df.columns:
                df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
            else:
                df['Desviacion_Num'] = ((df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']) / df['PROMD VTA DIA JUNIO']) * 100

            # --- IMPACTO FINANCIERO ---
            tiene_precio = 'PRECIO UNITARIO' in df.columns
            if tiene_precio:
                df['Dif_Unidades_Diarias'] = df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']
                df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
                df['Impacto_Mensual_$'] = df['Impacto_Diario_$'] * 30

            # --- ANÁLISIS ABC (PARETO) ---
            df = df.sort_values(by='PROMD VTA DIA JULIO', ascending=False).reset_index(drop=True)
            volumen_total_julio = df['PROMD VTA DIA JULIO'].sum()
            df['Porcentaje_Participacion'] = (df['PROMD VTA DIA JULIO'] / volumen_total_julio) * 100 if volumen_total_julio > 0 else 0
            df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()
            
            def asignar_abc(acumulado):
                if acumulado <= 80: return 'A'
                elif acumulado <= 95: return 'B'
                else: return 'C'
            df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

            # ==========================================
            # SECCIÓN 1: KPIs OPERATIVOS Y FINANCIEROS (CORREGIDOS)
            # ==========================================
            total_skus = len(df)
            subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
            bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
            
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total SKUs en Planta", f"{total_skus} Prod.")
            kpi2.metric("SKUs en Alza", f"{subio}", delta=f"+{subio} SKUs", delta_color="normal")
            kpi3.metric("SKUs en Alerta", f"{bajo}", delta=f"-{bajo} SKUs", delta_color="normal")
            
            if tiene_precio:
                impacto_total = df['Impacto_Mensual_$'].sum()
                if impacto_total < 0:
                    delta_financiero = "- Mensual vs Junio"
                else:
                    delta_financiero = "Mensual vs Junio"
                kpi4.metric("Balance Financiero Proyectado", f"${impacto_total:,.2f}", delta=delta_financiero, delta_color="normal")
            else:
                kpi4.metric("Balance Financiero", "Falta Precio Unitario")
                
            st.markdown("---")
            
            # ==========================================
            # SECCIÓN 2: FILTROS INTERACTIVOS (4 COLUMNAS)
            # ==========================================
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filtro_tendencia = st.selectbox("🎯 Estado de Tendencia:", ["Todos", "SUBIÓ", "BAJO"])
            with col_f2:
                filtro_abc = st.selectbox("📊 Clasificación ABC (Pareto):", ["Todos", "A", "B", "C"])
            with col_f3:
                # Extrae dinámicamente las marcas/categorías únicas del archivo Excel
                lista_categorias = ["Todos"] + sorted(df['CATEGORÍA'].dropna().unique().tolist())
                filtro_categoria = st.selectbox("🏷️ Filtrar por Categoría / Marca:", lista_categorias)
            with col_f4:
                busqueda = st.text_input("🔍 Filtrar por Nombre o Referencia:")
            
            # Aplicar filtros cruzados
            df_filtrado = df.copy()
            if filtro_tendencia != "Todos" and 'Estado de tendencia' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Estado de tendencia'] == filtro_tendencia]
            if filtro_abc != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Clasificación ABC'] == filtro_abc]
            if filtro_categoria != "Todos":
                df_filtrado = df_filtrado[df_filtrado['CATEGORÍA'] == filtro_categoria]
            if busqueda:
                df_filtrado = df_filtrado[
                    df_filtrado['PRODUCTO'].str.contains(busqueda, case=False, na=False) | 
                    df_filtrado['REFERENCIA INTERNA'].astype(str).str.contains(busqueda, na=False)
                ]
            
            # ==========================================
            # SECCIÓN 3: GRÁFICO INTERACTIVO
            # ==========================================
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
                st.warning("⚠️ No se encontraron registros que cumplan los criterios de filtrado seleccionados.")
            
            # ==========================================
            # SECCIÓN 4: TABLA DE DETALLE MATRICIAL
            # ==========================================
            st.markdown("---")
            st.markdown("### 📋 Detalle de Ventas, Clasificación ABC e Impacto")
            
            # Se incluye la columna 'CATEGORÍA' en la visualización
            if tiene_precio:
                columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Impacto_Mensual_$', 'Estado de tendencia']
            else:
                columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
            
            def resaltar_tendencia(val):
                if val == 'SUBIÓ': return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                elif val == 'BAJO': return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                return ''
            
            if tiene_precio:
                tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia']).format({'Impacto_Mensual_$': '${:,.2f}'})
            else:
                tabla_estilizada = df_filtrado[columnas_render].style.map(resaltar_tendencia, subset=['Estado de tendencia'])
                
            st.dataframe(tabla_estilizada, use_container_width=True, hide_index=True)

            # ==========================================
            # SECCIÓN 5: DESCARGA EJECUTIVA PARA FIRMAS
            # ==========================================
            st.markdown("---")
            st.markdown("### 📥 Módulo de Descarga Ejecutiva")
            st.info("Exporta la vista filtrada en una hoja formateada con las líneas institucionales de validación gerencial.")
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
                worksheet = writer.sheets['Reporte_Filtrado']
                
                for col in worksheet.columns:
                    max_length = 0
                    column = col[0].column_letter 
                    for cell in col:
                        try: 
                            if len(str(cell.value)) > max_length: max_length = len(str(cell.value))
                        except: pass
                    worksheet.column_dimensions[column].width = (max_length + 2)
                
                max_row = worksheet.max_row
                worksheet.cell(row=max_row + 4, column=1, value="___________________________________")
                worksheet.cell(row=max_row + 5, column=1, value="Firma: Gerencia de Operaciones Sapori")
                worksheet.cell(row=max_row + 4, column=3, value="___________________________________")
                worksheet.cell(row=max_row + 5, column=3, value="Firma: Dirección de Supply Chain")

            excel_data = buffer.getvalue()
            
            st.download_button(
                label="📄 Descargar Reporte para Firmas (Excel)",
                data=excel_data,
                file_name="Reporte_Desviaciones_Sapori.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

            # ==========================================
            # SECCIÓN 6: PIE DE PÁGINA AUTORÍA
            # ==========================================
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: gray; font-family: Arial;'>"
                "📝 Reporte Elaborado por: <b>Dirección de Supply Chain Sapori</b>"
                "</div>", 
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error crítico en la lectura del archivo Excel: {e}")