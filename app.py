import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(layout="wide", page_title="Portal Analítico - Sapori", page_icon="🔒")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# ==========================================
# MÓDULO DE ACCESO / LOGIN
# ==========================================
if not st.session_state['autenticado']:
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
            
        st.markdown("<h2 style='text-align: center; color: #2b2b2b; font-family: Arial; margin-top:0px;'>Portal Oficial de Operaciones</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Supply Chain, Ventas y Pronósticos</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("formulario_login"):
            st.markdown("##### 🔐 Ingrese sus credenciales corporativas")
            usuario = st.text_input("Usuario o Correo Institucional", placeholder="ej. gerencia.operaciones")
            contrasena = st.text_input("Contraseña del Sistema", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            boton_ingresar = st.form_submit_button("Acceder al Sistema", type="primary", use_container_width=True)
            
            if boton_ingresar:
                if usuario == "admin" and contrasena == "sapori2026":
                    st.session_state['autenticado'] = True
                    st.success("✅ Acceso concedido. Inicializando entorno...")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Verifique e intente de nuevo.")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align: center; color: #888; font-size: 12px; font-family: Arial;'>"
            "© 2026 Sapori | Dirección de Supply Chain & Operaciones<br>Versión del Sistema: 3.1 (Lógica Dinámica)"
            "</div>", 
            unsafe_allow_html=True
        )

# ==========================================
# ENTORNO DEL SISTEMA AUTENTICADO
# ==========================================
else:
    with st.sidebar:
        if os.path.exists("logo_empresa.png"):
            st.image("logo_empresa.png", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 📌 Módulos de Operación")
        modulo_activo = st.radio(
            "Seleccione el área a visualizar:",
            [
                "1. Dashboard Venta Diaria & Forecast", 
                "2. Control de Desviaciones (Mensual)", 
                "3. Análisis Estratégico y Desviaciones vs Forecast" # TEXTO EXACTO (Con "s")
            ]
        )
        
        # --- AQUÍ AGREGAMOS EL BOTÓN DE SUBIDA PARA EL MÓDULO 3 ---
        Historico_Produccion_CREMIGURT = None
        if modulo_activo == "3. Análisis Estratégico y Desviaciones vs Forecast":
            st.markdown("### 📁 Cargar Histórico")
            Historico_Produccion_CREMIGURT = st.file_uploader("Producción CREMIGURT", type=['xlsx'])
            
        st.markdown("---")
        # --- PARÁMETROS CRÍTICOS DE TIEMPO PARA EL FORECAST ---
        st.markdown("### ⏱️ Control de Tiempos del Mes")
        dias_efectivos = st.number_input("Días de Venta Efectivos (Transcurridos):", min_value=1, value=8, step=1)
        dias_restantes = st.number_input("Días de Venta Restantes del Mes:", min_value=0, value=15, step=1)
        
        st.markdown("---")
        st.success("👤 Rol: **Administrador / Gerencia**")
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

    # =========================================================================
    # MÓDULO 1: VENTA DIARIA Y FORECAST (CÁLCULO DINÁMICO)
    # =========================================================================
    if modulo_activo == "1. Dashboard Venta Diaria & Forecast":
        st.title("📈 Dashboard Ejecutivo: Pronósticos y Ventas")
        st.markdown("### Seguimiento de Forecast y Venta Diaria por SKU")
        
        file_ventas = "VINCULO VTS BY SKU.xlsx"
        
        if not os.path.exists(file_ventas):
            st.error(f"❌ **Archivo requerido no encontrado:** '{file_ventas}'")
            st.info("💡 Por favor, guarde la matriz con el nombre exacto de **'VINCULO VTS BY SKU.xlsx'** en la raíz de la carpeta.")
        else:
            try:
                df_vts = pd.read_excel(file_ventas)
                for col in df_vts.columns:
                    if 'PROMEDIO' in str(col).upper() or 'PROMD' in str(col).upper():
                        df_vts[col] = pd.to_numeric(df_vts[col], errors='coerce').round(0).fillna(0).astype(int)
                
                cols_upper = {col: str(col).upper().strip() for col in df_vts.columns}
                col_gross = next((c for c, m in cols_upper.items() if 'GROSS' in m or 'BRUTA' in m or 'VENTA_BRUTA' in m), None)
                col_return = next((c for c, m in cols_upper.items() if 'RETURN' in m or 'DEVOL' in m or 'RECHAZO' in m), None)
                col_forecast = next((c for c, m in cols_upper.items() if 'FORECAST' in m or 'META' in m or 'OBJETIVO' in m), None)
                
                val_gross = df_vts[col_gross].sum() if col_gross else 171575
                val_return = df_vts[col_return].sum() if col_return else 2145
                val_forecast = df_vts[col_forecast].sum() if col_forecast else 696207
                
                val_net = val_gross - val_return
                val_prom_dia = val_gross / dias_efectivos if dias_efectivos > 0 else 0
                val_pronost_mes = val_prom_dia * (dias_efectivos + dias_restantes)
                val_dif_units = val_gross - val_forecast
                val_efficiency = (val_gross / val_forecast) * 100 if val_forecast > 0 else 0
                
                if not col_gross or not col_forecast:
                    st.sidebar.warning("⚠️ Columnas no detectadas textualmente en Excel. Mostrando plantilla base estándar.")
                
                st.markdown(
                    """
                    <div style="background-color: #a9cce3; padding: 10px; text-align: center; font-weight: bold; font-size: 20px; color: #1f4e79; border-radius: 5px; margin-bottom: 20px;">
                        DASHBOARD DE CONTROL OPERATIVO DE DEMANDA
                    </div>
                    """, unsafe_allow_html=True
                )
                
                col_a1, col_a2, col_a3, col_a4, col_a5, col_a6, col_a7 = st.columns(7)
                col_a1.metric("TOTAL UNITS SALES GROSS", f"{val_gross:,.0f}")
                col_a2.metric("TOTAL UNITS SALES NET", f"{val_net:,.0f}")
                col_a3.metric("PROMEDIO VENTA DIARIA", f"{val_prom_dia:,.0f}")
                col_a4.metric("PRONOSTICO VENTA MENSUAL", f"{val_pronost_mes:,.0f}")
                col_a5.metric("FORECAST", f"{val_forecast:,.0f}")
                col_a6.metric("FORECAST EFFICIENCY", f"{val_efficiency:.1f}%")
                
                delta_dif = "- Brecha de Cobertura" if val_dif_units < 0 else "+ Superávit Comercial"
                col_a7.metric("DIFERENCIA ALCANCE FORECAST", f"{val_dif_units:,.0f}", delta=delta_dif, delta_color="normal")
                
                st.markdown("---")
                
                col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)
                col_b1.metric("UNITS RETURN (Devoluciones)", f"{val_return:,.0f}")
                col_b2.metric("INICIO DE VENTA", "01/07/2026")
                col_b4.metric("FINAL DE VENTA", "31/07/2026")
                col_b5.metric("DIAS VENTA EFECTIVOS.", f"{dias_efectivos} días")
                col_b6.metric("DIAS VENTA RESTANTES.", f"{dias_restantes} días")
                
                st.markdown("---")
                
                st.markdown("### 📋 Desglose Operativo: Matriz de Ventas por SKU")
                busqueda_sku = st.text_input("🔍 Filtrar tabla por Nombre de Producto o SKU de Producción:")
                
                df_vts_filtrado = df_vts.copy()
                if busqueda_sku:
                    mask = df_vts_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda_sku, case=False, na=False)).any(axis=1)
                    df_vts_filtrado = df_vts_filtrado[mask]
                
                st.dataframe(df_vts_filtrado, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"Error analítico durante el procesamiento del archivo: {e}")

    # =========================================================================
    # MÓDULO 2: CONTROL DE DESVIACIONES (MÓDULO MENSUAL)
    # =========================================================================
    elif modulo_activo == "2. Control de Desviaciones (Mensual)":
        st.title("📊 Tablero de Control de Desviaciones")
        st.markdown("### Análisis Comparativo, Financiero y Pareto (ABC) por SKU")

        file_name = "Comparación de Venta Diaria por SKU (Junio vs Julio).xlsx"

        if not os.path.exists(file_name):
            st.error(f"❌ **No se encontró el archivo de datos:** '{file_name}'")
        else:
            try:
                df = pd.read_excel(file_name, sheet_name="Table 1")
                
                if 'CATEGORÍA' not in df.columns:
                    df['CATEGORÍA'] = "Por Asignar"

                for col in ['PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO']:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
                    df[col] = df[col].round(0).astype(int)
                
                if 'Porcentaje de desviación' in df.columns:
                    df['Desviacion_Num'] = df['Porcentaje de desviación'].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
                else:
                    df['Desviacion_Num'] = ((df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']) / df['PROMD VTA DIA JUNIO']) * 100

                tiene_precio = 'PRECIO UNITARIO' in df.columns
                if tiene_precio:
                    df['Dif_Unidades_Diarias'] = df['PROMD VTA DIA JULIO'] - df['PROMD VTA DIA JUNIO']
                    df['Impacto_Diario_$'] = df['Dif_Unidades_Diarias'] * df['PRECIO UNITARIO']
                    df['Impacto_Mensual_$'] = df['Impacto_Diario_$'] * 30

                df = df.sort_values(by='PROMD VTA DIA JULIO', ascending=False).reset_index(drop=True)
                volumen_total_julio = df['PROMD VTA DIA JULIO'].sum()
                df['Porcentaje_Participacion'] = (df['PROMD VTA DIA JULIO'] / volumen_total_julio) * 100 if volumen_total_julio > 0 else 0
                df['Acumulado_ABC'] = df['Porcentaje_Participacion'].cumsum()
                
                def asignar_abc(acumulado):
                    if acumulado <= 80: return 'A'
                    elif acumulado <= 95: return 'B'
                    else: return 'C'
                df['Clasificación ABC'] = df['Acumulado_ABC'].apply(asignar_abc)

                total_skus = len(df)
                subio = len(df[df['Estado de tendencia'] == 'SUBIÓ']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] > 0])
                bajo = len(df[df['Estado de tendencia'] == 'BAJO']) if 'Estado de tendencia' in df.columns else len(df[df['Desviacion_Num'] < 0])
                
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Total SKUs en Planta", f"{total_skus} Prod.")
                kpi2.metric("SKUs en Alza", f"{subio}", delta=f"+{subio} SKUs", delta_color="normal")
                kpi3.metric("SKUs en Alerta", f"{bajo}", delta=f"-{bajo} SKUs", delta_color="normal")
                
                if tiene_precio:
                    impacto_total = df['Impacto_Mensual_$'].sum()
                    delta_financiero = "- Mensual vs Junio" if impacto_total < 0 else "Mensual vs Junio"
                    kpi4.metric("Balance Financiero Proyectado", f"${impacto_total:,.2f}", delta=delta_financiero, delta_color="normal")
                else:
                    kpi4.metric("Balance", "Falta Precio Unitario")
                    
                st.markdown("---")
                
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    filtro_tendencia = st.selectbox("🎯 Estado de Tendencia:", ["Todos", "SUBIÓ", "BAJO"])
                with col_f2:
                    filtro_abc = st.selectbox("📊 Clasificación ABC:", ["Todos", "A", "B", "C"])
                with col_f3:
                    lista_categorias = ["Todos"] + sorted(df['CATEGORÍA'].dropna().unique().tolist())
                    filtro_categoria = st.selectbox("🏷️ Categoría/Marca:", lista_categorias)
                with col_f4:
                    busqueda = st.text_input("🔍 Filtrar Nombre:")
                
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
                
                df_grafico = df_filtrado.sort_values(by='PROMD VTA DIA JUNIO', ascending=False)
                if not df_grafico.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico['PROMD VTA DIA JUNIO'], name='Junio', marker_color='#1f4e79'))
                    fig.add_trace(go.Bar(x=df_grafico['PRODUCTO'], y=df_grafico['PROMD VTA DIA JULIO'], name='Julio', marker_color='#d95f02'))
                    fig.update_layout(barmode='group', height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.markdown("### 📋 Detalle de Desviaciones")
                
                if tiene_precio:
                    columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Impacto_Mensual_$', 'Estado de tendencia']
                else:
                    columnas_render = ['REFERENCIA INTERNA', 'PRODUCTO', 'CATEGORÍA', 'Clasificación ABC', 'PROMD VTA DIA JUNIO', 'PROMD VTA DIA JULIO', 'Porcentaje de desviación', 'Estado de tendencia']
                
                def resaltar_tendencia(val):
                    if val == 'SUBIÓ': return 'background-color: #e2f0d9; color: #385723; font-weight: bold;'
                    elif val == 'BAJO': return 'background-color: #fce4d6; color: #c65911; font-weight: bold;'
                    return ''
                
                formato_columnas = {
                    'PROMD VTA DIA JUNIO': '{:,.0f}',
                    'PROMD VTA DIA JULIO': '{:,.0f}',
                    'Porcentaje de desviación': '{:.2%}'
                }
                
                if tiene_precio:
                    formato_columnas['Impacto_Mensual_$'] = '${:,.2f}'
                
                tabla_estilizada = df_filtrado[columnas_render].style.map(
                    resaltar_tendencia, subset=['Estado de tendencia']
                ).format(formato_columnas)
                    
                st.dataframe(tabla_estilizada, use_container_width=True, hide_index=True)

                st.markdown("---")
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_filtrado[columnas_render].to_excel(writer, sheet_name='Reporte_Filtrado', index=False)
                excel_data = buffer.getvalue()
                st.download_button("📄 Descargar Reporte para Firmas", data=excel_data, file_name="Reporte_Desviaciones.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

            except Exception as e:
                st.error(f"Error crítico en la lectura del archivo Excel: {e}")

    # =========================================================================
    # MÓDULO 3: DASHBOARD DE CONTROL DE PRODUCCIÓN (Estructura Horizontal)
    # =========================================================================
    elif modulo_activo == "3. Análisis Estratégico y Desviaciones vs Forecast":
        
        def render_modulo_analisis_produccion(file_historico):
            st.title("🏭 Tablero de Control de Producción Mensual")
            st.markdown("### Monitoreo de Volúmenes de Producción por Categoría")
        
            try:
                # 1. Leer archivo Excel completo para listar las hojas (categorías)
                xls = pd.ExcelFile(file_historico)
                nombres_hojas = xls.sheet_names
                
                # --- FILTROS DE INTERFAZ ---
                st.markdown("### 🎛️ Filtros de Análisis")
                col_filtro1, col_filtro2 = st.columns(2)
                
                with col_filtro1:
                    categoria_seleccionada = st.selectbox(
                        "🏷️ Seleccione la Categoría (Hoja):", 
                        options=nombres_hojas,
                        index=0
                    )
                
                # Cargar la hoja seleccionada
                df = pd.read_excel(xls, sheet_name=categoria_seleccionada)
                
                # --- LÓGICA DE EXTRACCIÓN HORIZONTAL INTELIGENTE ---
                meses_patrones = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
                pairs = []
                
                # Función para comprobar si una celda contiene o es una fecha
                def es_celda_fecha(val):
                    if hasattr(val, 'strftime'): # Verdadero si Excel ya lo lee como objeto de fecha nativo
                        return True
                    val_str = str(val).lower().strip()
                    return any(m in val_str for m in meses_patrones)

                # Escenario A: Las fechas quedaron en los encabezados de las columnas (df.columns)
                conteo_cols = sum(1 for col in df.columns if es_celda_fecha(col))
                if conteo_cols >= 2:
                    for idx, row in df.iterrows():
                        fila_pairs = []
                        for i, col in enumerate(df.columns):
                            if es_celda_fecha(col):
                                val_num = pd.to_numeric(row.iloc[i], errors='coerce')
                                if pd.notna(val_num) and val_num > 0:
                                    fila_pairs.append((col, val_num))
                        if len(fila_pairs) >= 2:
                            pairs = fila_pairs
                            break
                                
                # Escenario B: Las fechas están en una fila interna del archivo Excel
                if len(pairs) == 0:
                    for idx, row in df.iterrows():
                        conteo_fila = sum(1 for val in row if es_celda_fecha(val))
                        if conteo_fila >= 2:
                            if idx + 1 < len(df):
                                fila_valores = df.iloc[idx + 1]
                                for i in range(len(row)):
                                    f_val = row.iloc[i]
                                    if es_celda_fecha(f_val):
                                        val_num = pd.to_numeric(fila_valores.iloc[i], errors='coerce')
                                        if pd.notna(val_num) and val_num > 0:
                                            pairs.append((f_val, val_num))
                            break
                            
                if len(pairs) == 0:
                    st.warning("⚠️ No se detectó la secuencia horizontal de meses o valores en esta hoja. Verifica la estructura.")
                    return
                    
                # --- TRADUCCIÓN Y FORMATEO DE FECHAS ---
                import re
                meses_espanol = {
                    'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 
                    'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 
                    'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
                }
                
                clean_data = []
                for f_val, val in pairs:
                    if hasattr(f_val, 'strftime'): # Si ya es un objeto de tiempo, lo procesamos directo
                        dt = pd.to_datetime(f_val)
                        if pd.notna(dt):
                            clean_data.append({'Fecha': dt, 'Real': val})
                    else: # Si viene como texto puro (ej. "feb-26"), lo traducimos
                        m_str = str(f_val).lower().strip()
                        for m_letra, m_num in meses_espanol.items():
                            if m_letra in m_str:
                                year_match = re.search(r'(\d{2,4})$', m_str)
                                if year_match:
                                    year_part = year_match.group(1)
                                    m_str_numeric = f"{m_num}-{year_part}"
                                    fmt = '%m-%y' if len(year_part) == 2 else '%m-%Y'
                                    dt = pd.to_datetime(m_str_numeric, format=fmt, errors='coerce')
                                    if pd.notna(dt):
                                        clean_data.append({'Fecha': dt, 'Real': val})
                                break
                            
                df_final = pd.DataFrame(clean_data)
                if df_final.empty:
                    st.warning("⚠️ Las celdas de fecha detectadas no pudieron ser procesadas correctamente.")
                    return
                    
                df_final = df_final.sort_values(by='Fecha').reset_index(drop=True)
                
                # Formato visual para el selector (Ej: Feb-2026)
                meses_display = {
                    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
                }
                df_final['Mes_Filtro'] = df_final['Fecha'].dt.month.map(meses_display) + "-" + df_final['Fecha'].dt.strftime('%Y')
                
                meses_disponibles = ["Todos los meses"] + df_final['Mes_Filtro'].unique().tolist()
                
                with col_filtro2:
                    mes_seleccionado = st.selectbox(
                        "📅 Seleccione el Mes:", 
                        options=meses_disponibles
                    )
                    
                # Aplicar filtro de tiempo si aplica
                if mes_seleccionado != "Todos los meses":
                    df_final = df_final[df_final['Mes_Filtro'] == mes_seleccionado]
                    
                if df_final.empty:
                    st.info("No hay registros para mostrar con el filtro seleccionado.")
                    return
                    
                # --- KPI CARDS (Formato limpio con puntos) ---
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                total_prod = df_final['Real'].sum()
                promedio_prod = df_final['Real'].mean()
                max_idx = df_final['Real'].idxmax()
                max_row = df_final.loc[max_idx]
                
                with col1:
                    st.metric("Total Volumen Producido", f"{total_prod:,.0f}".replace(",", "."))
                with col2:
                    st.metric("Promedio de Producción Mensual", f"{promedio_prod:,.0f}".replace(",", "."))
                with col3:
                    st.metric("Pico Más Alto de Producción", f"{max_row['Real']:,.0f}".replace(",", "."), f"Mes: {max_row['Mes_Filtro']}")
                    
                # --- GRÁFICO DE BARRAS DE TENDENCIA ---
                st.markdown("---")
                st.subheader(f"Tendencia de Producción: Período Actual ({categoria_seleccionada})")
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_final['Mes_Filtro'],
                    y=df_final['Real'],
                    name='Producción (Unidades)',
                    marker_color='#1f4e79',
                    text=[f"{v:,.0f}".replace(",", ".") for v in df_final['Real']],
                    textposition='auto'
                ))
                fig.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=20, b=20),
                    hovermode="x unified",
                    yaxis=dict(title="Unidades"),
                    xaxis=dict(title="Meses")
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # --- TABLA DETALLADA ---
                st.subheader("📋 Resumen de Datos Analizados")
                df_tabla = df_final[['Mes_Filtro', 'Real']].copy()
                df_tabla.columns = ['Mes / Período', 'Producción Real (Unidades)']
                
                st.dataframe(
                    df_tabla.style.format({
                        'Producción Real (Unidades)': lambda x: f"{x:,.0f}".replace(",", ".")
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
            except Exception as e:
                st.error(f"Error analítico durante el procesamiento horizontal: {e}")

        ## --- ORDEN DE EJECUCIÓN DEL MÓDULO ---
        file_historico_path = "Historico_Produccion_CREMIGURT.xlsx"
        
        if os.path.exists(file_historico_path):
            # Si el archivo existe en GitHub/carpeta local, ejecuta el dashboard automáticamente
            render_modulo_analisis_produccion(file_historico_path)
        else:
            # Si no lo encuentra, mostramos un error estilizado igual que en el Módulo 1 y 2
            st.error(f"❌ **Archivo requerido no encontrado:** '{file_historico_path}'")
            st.info("💡 Asegúrate de que el archivo 'Historico_Produccion_CREMIGURT.xlsx' esté guardado en el repositorio (raíz) junto a tu código.")
    # =========================================================================
    # PIE DE PÁGINA GLOBAL
    # =========================================================================
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-family: Arial;'>"
        "📝 Sistema Operativo Realizado por: <b>Dirección de Supply Chain Sapori</b>"
        "</div>", 
        unsafe_allow_html=True
    )